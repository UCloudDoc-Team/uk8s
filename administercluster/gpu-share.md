# 多个Pod共享使用GPU

该方案将部署GPU-Share插件，部署完成后集群节点的GPU将可以被多个Pod共同调度。目前仅支持命令行安装使用，后续UK8S团队会根据排期将该功能添加至集群插件中，方便一键安装。

## 安装使用GPU共享插件

### 1. 在需要共享GPU的节点打上label

```bash
kubectl label node <nodeip> nodeShareGPU=true
```

### 2. 通过kubectl删除集群原有的nvdia插件

```bash
kubectl delete ds -n kube-system nvidia-device-plugin-daemonset
```

### 3. 执行kubectl进行GPU-Share插件安装，安装完成

```bash
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/gpu-share/1.0.0.yaml
```

### 测试GPU共享

测试条件：
1. 集群中只有一台单卡GPU云主机
2. 该集群已经按照以上3步完成插件安装
3. 查看插件pod已经变成running

接下来我们分别运行test-gpushare1、test-gpushare2


```bash
# 运行test-gpushare1
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/gpu-share/test-gpushare1.yaml
# 运行test-gpushare2
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/gpu-share/test-gpushare2.yaml
```

以test-gpushare1为例。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-gpushare1
  labels:
    app: test-gpushare1
spec:
  selector:
    matchLabels:
      app: test-gpushare1
  template:
    metadata:
      labels:
        app: test-gpushare1
    spec:
      schedulerName: gpushare-scheduler
      containers:
      - name: test-gpushare1
        image: uhub.service.ucloud.cn/ucloud/gpu-player:share
        command:
          - python3
          - /app/main.py
        resources:
          limits:
            # GiB
            ucloud.cn/gpu-mem: 1
```

在limits下设置了`ucloud.cn/gpu-mem: 1`，同样test-gpushare2也有该设置，则我们可以观察在该集群只有一台单卡GPU的节点时，该GPU同时支持给到2个Pod使用。

```bash
kubectl get pod |grep test-gpushare
```

### 查看GPU使用量

可以通过监控接入的GPU节点资源用量，或者进入GPU节点执行`nvidia-smi`进行查看。

## 移除GPU共享插件

请在master节点执行以下命令

```bash
kubectl delete -f https://gitee.com/uk8s/uk8s/raw/master/yaml/gpu-share/1.0.0.yaml
kubectl apply -f /etc/kubernetes/yaml/nvidia-device-plugin.yaml
```
