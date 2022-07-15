# 固定 IP 使用方法

固定 IP 适用于对容器固定 IP 强依赖的场景。

在传统的虚拟机部署形式下，部分客户依赖虚拟机 IP 地址，用于问题排查、监控、流量分配等，固定 IP 支持能够帮助用户更好地从虚拟机向容器迁移，提升运维效率。对 IP 无限制的业务**不推荐您使用固定
IP 模式**。

固定 IP 仅支持 **StatefulSet 形式的资源控制器**。

## 1. 固定 IP 插件安装和升级

请在您的 UK8S 集群中执行以下命令，安装固定 IP 功能组件，如果已经安装，再次执行会将其升级到最新版本，后续版本将支持通过控制台安装相关组件：

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/network/cni-vpc-ipamd.yml
```

## 2. 创建固定 IP 类型的 StatefulSet

当前仅支持通过 Yaml 形式创建固定 IP 类型的 StatefulSet，需要您在 spec.template.annotations 添加相应注释进行配置，后续版本将支持通过控制台表单创建：

| 注释                                                            | 注释说明                                | 参数类型                                                      | 默认值   |
| ------------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------- | ----- |
| network.beta.kubernetes.io/ucloud-statefulset-static-ip       | 是否需要开启固定 IP 功能                      | true / false                                              | false |
| network.beta.kubernetes.io/ucloud-statefulset-ip-claim-policy | IP 回收策略，即 Pod 销毁及绑定的 VpcIP 解绑后释放的时间 | hms / Never<br>例：1h10m20s 代表 VpcIP 解绑后 1 小时 10 分 20 秒后被释放 | Never |

以下为创建一个 StatefulSet 类型的 Nginx 应用并对外暴露的 Yaml 范本

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: nginx
  clusterIP: None
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web-test
  namespace: default
spec:
  selector:
    matchLabels:
      app: nginx 
  serviceName: "nginx"
  replicas: 5 
  template:
    metadata:
      annotations:
        # 声明需要开启固定 IP 功能
        network.beta.kubernetes.io/ucloud-statefulset-static-ip: "true"  
        # 设定 VpcIP 释放时间为 300 秒       
        network.beta.kubernetes.io/ucloud-statefulset-ip-claim-policy: "300s"
      labels:
        app: nginx 
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: nginx
        image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
        ports:
        - containerPort: 80
          name: web
```

## 3. 异常情况说明

##### 1. Node 节点宕机 / 移除

节点宕机或从集群中移除，将触发 Pod 的强制迁移，Pod 绑定的 VpcIP 将会被保留，Pod 调度到新的 Node 节点后，管理服务将更新、记录相应的映射关系。

如果该节点上曾经有固定 IP Pod，缩容后该 Pod 被终止，并且没有因为扩容等再重新拉起或被调度至其他节点，节点上将保留有该 Pod 的 VpcIP，在移除节点时，该 VpcIP 会因未被任何
Pod 占用被解除与该节点的绑定关系并释放。此时如再在其他节点重新拉起该 Pod，可能会因该 VpcIP 已被其他应用占用而导致 Pod 无法重新拉起。**因此在移除节点前，请务必确认节点上已无未被
Pod 占用的 VpcIP**，具体步骤请参照「4. 节点下线步骤」。

##### 2. Node 节点强制删除

指在云主机页面（而非通过 UK8S 集群管理功能）进行 Node 节点云主机资源的删除，此情况下 UK8S 管理服务无法进行保留 VpcIP 操作，VpcIP
将会被主机服务强制释放，并存在被其他资源占用的可能性。

固定 IP 组件将会尝试以指定 IP 形式重新申请旧有 VpcIP，并绑定至新拉起的 Pod 上，但如相应的 VpcIP 已被占用，将出现更新失败情况。

##### 3. 同一 StatefulSet 中出现不同 VPC 子网的 Pod

固定 IP 功能暂**不支持跨 VPC 子网**，在 CNI 工作原理下，Pod 与所在 Node 节点处在同一 VPC 子网。如在 StatefulSet 扩容、Pod 异地更新、Node
节点宕机等情况下，Pod 被调度到非同子网的 Node 节点上，将会出现 Pod 创建/更新失败的错误。

建议您**合理分配您的子网及网段**，避免在集群中存在多子网现象，或通过标签等将 StatefulSet 指定调度到同一子网 Node 节点上。

## 4. 节点下线步骤

##### 1. 确认待下线节点的 Mac 信息

登入需要删除的节点，通过 `ifconfig` 命令查看 eth0 网卡的 Mac 地址。

固定 IP 插件通过自定义资源对象 **vpcIpClaim** 记录 VpcIP、Pod 及运行节点的对应关系。如果节点上有未驱逐的固定 IP Pod，也可以通过
`kubectl get pods -o wide` 查看该节点上运行的固定 IP Pod 的名称，并再通过 `kubectl describe vpcIpClaims <pod-name>` 查看
CRD 信息，CRD 中 Status.Mac 可以确定主机的 Mac 地址。

##### 2. 通过 Mac 地址查找归属于下线节点的固定 IP

通过 kubectl 命令，查找出该节点上未被占用 VpcIP 对应的 CRD 对象信息。

```bash
# 将 grep 命令后的 mac 地址替换为待下线的节点 mac 地址
kubectl get vpcIpClaims -l attached=false -o=json | jq '.items[]|.metadata.name + " " + .status.mac' | grep 52:54:00:26:6E:DA
"web-test-11 52:54:00:26:6E:DA"
"web-test-13 52:54:00:26:6E:DA"
"web-test-14 52:54:00:26:6E:DA"
```

该显示结果说明，在 Mac 地址为 52:54:00:26:6E:DA 的节点上，曾经运行过 web-test-11、web-test-13、web-test-14 这几个 Pod。

##### 3. 调整 StatefulSet 副本数目，保证固定 IP 被占用

执行 `kubectl patch sts web-test -p '{"spec":{"replicas":15}}'`，将 Sts 副本数调整为 15，保证 web-test-14
拉起，相应的固定 IP 被占用。

执行 `kubectl drain <node-name> --ignore-daemonsets`，将待下线节点清空，如节点已禁用及清空，则可忽略这一步。

##### 4. 节点下线

再次执行
`kubectl get vpcIpClaims -l attached=false -o=json | jq '.items[]|.metadata.name + " " + .status.mac' | grep 52:54:00:26:6E:DA`，确定节点上已无未被占用的
VpcIP 后，在 UK8S 控制台移除节点。

最后，再次执行 `kubectl patch sts web-test -p '{"spec":{"replicas":<new-replicas>}}'`，将 Sts 副本数调整为期望值。

