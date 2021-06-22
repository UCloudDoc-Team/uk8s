## 固定 IP 使用方法

固定 IP 适用于对容器固定 IP 强依赖的场景。

在传统的虚拟机部署形式下，部分客户依赖虚拟机 IP 地址，用于问题排查、监控、流量分配等，固定 IP 支持能够帮助用户更好地从虚拟机向容器迁移，提升运维效率。对 IP 无限制的业务**不推荐您使用固定 IP 模式**。

固定 IP 仅支持 **StatefulSet 形式的资源控制器**。

### 固定 IP 插件安装

固定 IP 功能需要部署以下 3 个组件：
* 自定义 CustomResourceDefinition 对象 VpcIPClaim，用以存储 IP + PodName信息；
* VIP-Controller 控制器，负责释放和重新分配固定 IP
* CNI-VPC-IPAMD 网络插件，负责检查是否需要分配固定 IP

请在您的 UK8S 集群中执行以下命令，安装上述固定 IP 功能需要的组件，后续版本将支持通过控制台安装相关组件：

```
kubectl apply -f https://gitee.com/uk8s/dashboard/projects/uk8s/uk8s/blob/master/yaml/network/VpcIpClaim.yaml
kubectl apply -f https://gitee.com/uk8s/dashboard/projects/uk8s/uk8s/blob/master/yaml/network/vip-controller.yaml
kubectl apply -f https://gitee.com/uk8s/dashboard/projects/uk8s/uk8s/blob/master/yaml/network/cni-vpc-ipamd.yaml
```

### 创建固定 IP 类型的 StatefulSet

当前仅支持通过 Yaml 形式创建固定 IP 类型的 StatefulSet，需要您在 spec.template.annotations 添加相应注释进行配置，后续版本将支持通过控制台表单创建：

| 注释 | 注释说明 | 变量值 | 默认值 |
|--------|--------|--------|--------|
| service.beta.kubernetes.io/ucloud-statefulset-static-ip | 是否需要开启固定 IP 功能 | true / false | false |
| service.beta.kubernetes.io/ucloud-statefulset-ip-claim-policy | IP 回收策略，即 Pod 销毁及绑定的 VpcIP 解绑后释放的时间 | hms / never<br>例：1h10m20s 代表 VpcIP 解绑后 1 小时 10 分 20 秒后被释放| never |

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

### 异常情况说明

##### 1. Node 节点宕机 / 移除

节点宕机或从集群中移除，将触发 Pod 的强制迁移，Pod 绑定的 VpcIP 将会被保留，Pod 调度到新的 Node 节点后，管理服务将更新、记录相应的映射关系。

##### 2. Node 节点强制删除

指在云主机页面（而非通过 UK8S 集群管理功能）进行 Node 节点云主机资源的删除，此情况下 UK8S 管理服务无法进行保留 VpcIP 操作，VpcIP 将会被主机服务强制释放，并存在被其他资源占用的可能性。

固定 IP 组件将会尝试以指定 IP 形式重新申请旧有 VpcIP，并绑定至新拉起的 Pod 上，但如相应的 VpcIP 已被占用，将出现更新失败情况。

##### 3. 同一 StatefulSet 中出现不同 VPC 子网的 Pod

固定 IP 功能暂**不支持跨 VPC 子网**，在 CNI 工作原理下，Pod 与所在 Node 节点处在同一 VPC 子网。如在 StatefulSet 扩容、Pod 异地更新、Node 节点宕机等情况下，Pod 被调度到非同子网的 Node 节点上，将会出现 Pod 创建/更新失败的错误。

建议您**合理分配您的子网及网段**，避免在集群中存在多子网现象，或通过标签等将 StatefulSet 指定调度到同一子网 Node 节点上。