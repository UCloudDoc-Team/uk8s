# Pod 容忍节点异常时间调整

## 1. 原理说明

Kubernetes 集群节点处于异常状态之后需要有一个等待时间，才会对节点上的 Pod 进行驱逐。那么针对部分关键业务，是否可以调整这个时间，便于在节点发生异常时及时将 Pod
驱逐并在别的健康节点上重建？

要解决这个问题，我们首先要了解 Kubernetes 在节点异常时驱逐 Pod 的机制。

在 Kubernetes 1.13 及以后的版本中默认开启了 `TaintBasedEvictions` 及 `TaintNodesByCondition` 这两个 feature
gate，节点及其上 Pod 的生命周期管理将通过节点的 Condition 和 Taint 来进行，Kubernetes 会不断地检查所有节点状态，设置对应的 Condition，根据
Condition 为节点设置对应的 Taint，再根据 Taint 来驱逐节点上的 Pod。

同时在创建 Pod 时会默认为 Pod 添加相应的 tolerationSeconds 参数，指定当节点出现异常（如 NotReady）时 Pod 还将在这个节点上运行多长的时间。

那么，节点发生异常到 Pod 被驱逐的时间，就取决于两个参数：1. 节点实际异常到被判断为不健康的时间；2. Pod 对节点不健康的容忍时间。

Kubernetes 集群中默认节点实际异常到被判断为不健康的时间为 40s，Pod 对节点 NotReady 的容忍时间为 5min，也就是说，节点实际异常 5min40s（340s）后，节点上的
Pod 才会发生驱逐。

## 2. 调整节点被标记为不健康的时间

ControllerManager 参数 `--node-monitor-grace-period` 控制了在将一个节点标记为不健康之前允许其无响应的时长上限，该参数默认值为 40s，且必须比
Kubelet 的 `nodeStatusUpdateFrequency` 参数（Kubelet 向主控节点汇报节点状态的时间间隔）大 N 倍； 这里 N 指的是 kubelet
发送节点状态的重试次数。

如需修改该参数，请**逐台在三台 Master 节点上**进行如下操作：

1. 在 ControllerManager 配置文件`/etc/kubernetes/controller-manager` 中添加参数
   `--node-monitor-grace-period=20s`，将节点被标记为不健康的容忍时间调整为 20s，**修改前请做好配置文件备份**；

2. 执行 `systemctl restart kube-controller-manager` 重启 ControllerManager；

3. 执行 `systemctl status kube-controller-manager` 确认 ControllerManager 状态为 `active`。

## 3. 调整 Pod 对节点不健康的容忍时长

在创建 Pod 时，如无特别指定，节点控制器会为 Pod 添加如下污点：

```yaml
tolerations:
- key: "node.kubernetes.io/unreachable"
  operator: "Exists"
  effect: "NoExecute"
  tolerationSeconds: 300
- key: "node.kubernetes.io/not-ready"
  operator: "Exists"
  effect: "NoExecute"
  tolerationSeconds: 300
```

这种自动添加的容忍度意味着在其中一种问题（NotReady / UnReachable）被检测到时 Pod 默认能够继续停留在当前节点运行 5 分钟。

> 注：当 DaemonSet 中的 Pod 被创建时， 针对 unreachable / not-ready 污点自动添加的 NoExecute 的容忍度将不会指定
> tolerationSeconds，保证出现相应问题时 DaemonSet 中的 Pod 永远不会被驱逐。

### 3.1 调整默认容忍时长

Kubernetes 为 Pod 自动添加的针对 unreachable / not-ready 污点的容忍时长由 APIServer 中的相应参数控制，如需修改**请逐台在三台 Master
节点上**进行如下操作：

1. 在 APIServer 配置文件`/etc/kubernetes/apiserver` 中添加参数 `--default-not-ready-toleration-seconds=100` 及
   `--default-unreachable-toleration-seconds=100`，将对污点 NotReady:NoExecute 及 Unreachable:NoExecute
   的容忍时长（以秒记，默认为 300）调整为 100s，**修改前请做好配置文件备份**；

2. 执行 `systemctl restart kube-apiserver` 重启 APIServer

3. 执行 `systemctl status kube-apiserver` 确认 APIServer 状态为 `active`。

### 3.2 调整现有 Pod 容忍时长

以通过 Deployment 创建的 Pod 为例，我们需要通过 `kubectl patch` 命令修改现有 Deployment 中的 Toleration 参数。

首先，创建 patch 文件 tolerationseconds.yaml，示例如下：

```yaml
spec:
  template:
    spec:
      tolerations:
      - key: "node.kubernetes.io/unreachable"
        operator: "Exists"
        effect: "NoExecute"
        # 调整 Pod 对污点 Unreachable:NoExecute 的容忍时长为 100s
        tolerationSeconds: 100
      - key: "node.kubernetes.io/not-ready"
        operator: "Exists"
        effect: "NoExecute"
        # 调整 Pod 对污点 NotReady:NoExecute 的容忍时长为 100s
        tolerationSeconds: 100
```

再执行 `kubectl patch deploy your-deployment --patch "$(cat tolerationseconds.yaml)"` 命令，对 Deployment
进行修改。修改完成后，会发现该 Deployment 控制的 Pod 中相应的污点容忍时长已经被修改。

> ⚠️ 该操作会引发 Deployment 对所有 Pod 进行重建，请在业务低谷时进行。

## 4. 参考文档

1. [污点和容忍度](https://kubernetes.io/zh/docs/concepts/scheduling-eviction/taint-and-toleration/)

2. [kube-apiserver](https://kubernetes.io/zh/docs/reference/command-line-tools-reference/kube-apiserver/)

3. [kube-controller-manager](https://kubernetes.io/zh/docs/reference/command-line-tools-reference/kube-controller-manager/)
