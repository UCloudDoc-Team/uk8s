# Virtual Kubelet 虚拟节点


[Virtual Kubelet](https://virtual-kubelet.io/) 是 Kubernetes 社区的重要开源项目，基于 Virtual Kubelet 虚拟节点组件，可以实现 UCloud 两大容器产品 UK8S 和 Cube 的无缝对接，用户在 UK8S 集群中可通过 VK 组件创建 [Cube 容器实例](/cube/README)，每个 Cube 实例被视为 VK 节点上的一个Pod。   

> 注意：新建虚拟节点不收取费用，虚拟节点上运行的Pod会收取实时费用；虚拟节点是Serverless的，背后由UCloud海量物理机资源(即Cube)支撑，因此无法登陆虚拟节点或是查看虚拟节点本身监控，但可查看虚拟节点上面Pod的监控   


## 添加虚拟节点

在集群节点列表页，点击「添加虚拟节点」按钮，为 UK8S 集群添加虚拟节点，当前一个 UK8S 集群支持最多添加 8 个虚拟节点，所添加的虚拟节点名称为 **uk8s-xxxxxxxx-vk-xxxxx**，该名称将被注册为虚拟节点的 **spec.nodeName**，其中 **uk8s-xxxxxxxx** 为 UK8S 集群 ID，末五位为随机生成的数字字母组合。

![](../images/administercluster/vk_01.png)

| 字段 | 说明 |
|-----|-------|
|地域|VK 节点所属地域，即 UK8S 集群所在地域，不可更改。|
|所属子网|VK 节点及生成的 Cube Pod 所在子网，默认为 UK8S 集群 Master 节点所在子网。|
|可用区|VK 节点及生成的 Cube Pod 所在可用区，<br>当前 Cube 支持可用区：华北（北京）E，广州B。|
|Pod 默认配置|不指定资源 requests 情况下，VK 节点生成的 Cube Pod 的默认资源配置。|
|节点最大 Pod 数|节点最大可以创建的 Cube Pod 数量，当前支持最多 200 个 Cube Pod。|
|Cluster IP 支持|虚拟节点生成的 Cube Pod 可与 UK8S 中 Pod 通过 Cluster IP 互相访问。<br>当 Cube 急剧扩容时，开启该功能会导致 UK8S ApiServer 压力急剧上升。对无需使用 K8S Service 转发能力的容器，建议不开启该功能。|

## 虚拟节点管理

### 节点描述

VK 节点与普通 Node 节点一样，是 UK8S 集群当中的一个 Node 对象。[命令行管理时](/uk8s/manageviakubectl/intro_of_kubectl)可使用 `kubectl get nodes` 等命令进行节点的管理、查看，在集群列表页点击「节点描述」按钮，亦可查看 VK 节点详细信息、节点状态、节点生成的 Cube Pod 及节点事件。

![](../images/administercluster/vk_02.png)

### 禁用及删除

您可以在控制台页面，进行 VK 节点的禁用和删除，禁用 VK 节点后应用将不能够通过 VK 节点创建 Cube 实例，现有通过 VK 节点创建的 Cube 实例将被保留。删除 VK 节点时，通过 VK 节点创建的 Cube 实例及所挂载的UDisk 将会被默认删除。

## 通过虚拟节点创建 Cube 实例

通过 VK 节点创建 Cube 实例的方式，与普通 Pod 资源类似，但需要在 yaml 文件 Pod spec 中添加 nodeName 或 nodeSelector 指定 VK 节点并添加污点容忍。支持直接创建 Pod，或通过 Deployment 及 StatefulSet 等控制器进行 Pod 的管理。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  # 如pod无需和api server通信，则建议不挂载token。在pod spec中加入以下字段跳过挂载
  # 如果必须使用service account token, 参考下方关于 「1.22版本service account token自动挂载问题」 的说明
  automountServiceAccountToken: false
  # 通过 nodeSelector 调度到 VK 节点，nodeName 及 nodeSelector 只需配置一项
  # 如以 Deploy 及 Sts 形式创建，请务必使用 nodeSelector
  # 虚拟节点创建后，也可为虚拟节点添加指定标签，用于 Pod 调度的管理
  nodeSelector:
    type: virtual-kubelet
  # 通过指定 nodeName 调度到 VK 节点
  # nodeName: uk8s-xxxxxxxx-vk-xxxxx
  # 添加节点容忍
  tolerations:
  - key: virtual-kubelet.io/provider
    operator: Equal
    value: ucloud
    effect: NoSchedule
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:latest
    # 通过以下参数指定Pod资源配置 (如果不使用默认配置)，具体支持规格参考下方
    resources:
      requests:
        cpu: "2"
        memory: 2048Mi
```
创建 Cube 实例时，需注意特定 CPU / 内存规格有一定的比例及限制，VK 支持创建 Cube 规格配置如下：

| CPU | 内存 |
|-----|-----|
|500m|512Mi/1Gi/2Gi|
|1|1Gi/2Gi/4Gi|
|2|2Gi/4Gi/8Gi|
|4|4Gi/8Gi/16Gi|
|8|8Gi/16Gi|

### 详细注释说明

通过 VK 插件创建 Cube 时，支持在 Pod annotations，或 Deployment / Statefulset 的 spec.template.annotations 中添加相应字段，为 Cube 进行进一步配置，相应注释说明如下：

| 注释 | 参数类型 | 注释说明 | 默认值 |
| ------ | ------ | ------ | ------ |
| cube.ucloud.cn/cube-tag | string | 需要指定的业务组的名称 | / |
| cube.ucloud.cn/cube-chargetype | year/month/postpay | Cube 付费模式，即按年预付费 / 按月预付费 / 按秒后付费，请参照[计费说明](/cube/introduction/charge) | postpay |
| cube.ucloud.cn/cube-quantity | int | Cube 付费时长，月付时，此参数传 0，代表购买至月末 | 1 | 
| cube.ucloud.cn/cube-eip | true/false | 是否需要绑定 EIP | false | 
| cube.ucloud.cn/cube-eip-id | eip-xxxxxxxx | 绑定指定 ID 的 EIP | /，仅在 cube.ucloud.cn/cube-eip: "true" 时生效，<br>如该项留空，则创建新的 EIP | 
| cube.ucloud.cn/cube-eip-paymode | traffic/bandwidth/sharebandwidth | EIP 计费模式，即流量计费 / 带宽计费 / 共享带宽模式 | bandwidth | 
| cube.ucloud.cn/cube-eip-share-bandwidth-id | bwshare-xxxxxx | 共享带宽 ID，仅在 EIP 计费模式为「共享带宽」时生效 | / | 
| cube.ucloud.cn/cube-eip-bandwidth | int | 绑定 EIP 的外网带宽大小，共享带宽模式必须指定 0 | 2 | 
| cube.ucloud.cn/cube-eip-chargetype | year/month/dynamic | EIP 付费模式，即按年预付费 / 按月预付费 / 按时后付费 | 取 cube.ucloud.cn/cube-chargetype 值；<br>该项为 postpay 时取 dynamic | 
| cube.ucloud.cn/cube-eip-quantity | int | EIP 付费时长 | 取 cube.ucloud.cn/cube-quantity 值 | 
| cube.ucloud.cn/cube-eip-release | true/false | 删除 Cube 实例时是否需要释放绑定的 EIP | true | 
| cube.ucloud.cn/cube-eip-security-group-id | firewall-xxxxxxxx | 需要绑定的外网防火墙策略，不指定时绑定项目默认防火墙 |/ | 

### 说明：1.22版本支持service account token自动挂载问题
从1.22版本开始service account token挂载默认为projected volume模式，cube不支持此类型的volume。   
#### 如pod无需和api server通信，则可以不挂载token；在pod spec中加入以下字段跳过挂载
```yaml
automountServiceAccountToken: false
```

#### 如果pod的运行依赖service account token, 则可以显式指定以secret的方式挂载

以default sa为例:  

如果是1.24及更高版本的集群，由于创建 service account 时没有自动生成相应的token，首先需要创建一个secret：
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: default-token
  annotations:
    kubernetes.io/service-account.name: default
type: kubernetes.io/service-account-token
```

> 1.22版本不需要以上步骤，执行 `kubectl get secret` 找到 `default` service account 对应的 secret名称即可。

创建deployment时，显式指定service account、volume 和 mount:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      # 指定部署到虚拟节点
      nodeSelector:
        type: virtual-kubelet
      tolerations:
      - effect: NoSchedule
        key: virtual-kubelet.io/provider
        operator: Equal
        value: ucloud
      serviceAccount: default
      containers:
      - name: nginx
        image: uhub.service.ucloud.cn/ucloud/nginx:latest
        ports:
        - containerPort: 80
        # 显式挂载
        volumeMounts:
        - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
          name: default-token
          readOnly: true
      volumes:
      # 显式指定secret形式的volume
      - name: default-token
        secret:
          defaultMode: 420
          secretName: default-token # 1.22版本中加上token后缀

```

## UDisk 存储卷挂载支持

用户可以通过声明 PVC 存储卷的方式为 VK 节点上的 Cube 实例创建挂载 UDisk 存储卷，这部分工作由 CSI UDisk 和 Virtual Kubelet 组件共同完成，存储类、持久卷声明用法与正常在 UK8S 中使用存储卷一致（**包括新建 UDisk 及使用已有 UDisk**，详见：[在 UK8S 中使用 UDisk](/uk8s/volume/udisk)）。

以下是使用例子：

```yaml
## 创建存储类 StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ssd-csi-udisk
provisioner: udisk.csi.ucloud.cn
parameters:
## 建议使用 SSD 或 SATA 云盘，避免因 RSSD 云盘 RDMA 区域与 Cube 无法匹配导致云盘无法挂载
  type: "ssd"
## 不支持 xfs 文件系统
  fsType: "ext4"
## 回收策略，支持Delete和Retain，默认为Delete，非必填
reclaimPolicy: Delete
## 如绑定模式设置为 WaitForFirstConsumer，则只能通过 pod.spec.nodeSelector 指定 VK 节点
volumeBindingMode: WaitForFirstConsumer
---
## 创建持久化存储卷声明 PVC
## 不支持 Volume Expansion（存储卷动态扩容）
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: logdisk-claim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ssd-csi-udisk
  resources:
    requests:
      storage: 20Gi
---
## 在 Pod 中使用 PVC
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  tolerations:                               
  - effect: NoSchedule
    key: virtual-kubelet.io/provider
    operator: Equal
    value: ucloud
## 如绑定模式设置为 WaitForFirstConsumer，则只能通过 pod.spec.nodeSelector 指定 VK 节点
  nodeSelector:
    type: virtual-kubelet
  containers:
  - name: http
    image: uhub.service.ucloud.cn/ucloud/nginx:latest
    volumeMounts:
    - name: log
      mountPath: /data
  volumes:
  - name: log
    persistentVolumeClaim:
      claimName: logdisk-claim
```

## 使用自建镜像仓库   
### 1. 创建自建镜像仓库   
以自建hub地址 `myhub.ucloud.cn` 为例，需要额外提供的信息包括镜像仓库ip地址和所在vpc。用户名和密码非必填。   
参考 https://docs.ucloud.cn/cube/userguide/self_repository
```bash
cat > .dockerconfigjson <<EOF
{
  "auths": {
    "myhub.ucloud.cn": {
      "username": "user-xxx",
      "password": "passwd-yyy",
      "registryaddr": "10.x.y.z",
      "vpcid": "uvnet-xxx"
    }
  }
}
EOF
kubectl create secret docker-registry myhub --from-file=.dockerconfigjson
```
### 2. 创建pod时指定 `imagePullSecret` 
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-myhub-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      automountServiceAccountToken: false
      nodeSelector:
        type: virtual-kubelet
      tolerations:
      - key: virtual-kubelet.io/provider
        operator: "Equal"
        value: ucloud
        effect: NoSchedule
      containers:
      - name: nginx
        image: myhub.ucloud.cn/test/nginx:latest
        ports:
        - containerPort: 80
      imagePullSecrets:
      - name: myhub

```

## 虚拟节点能力限制

### 网络
支持使用VPC，与云主机同级；不支持 `hostNetwork` 、CNI、Calico Policy等功能。
### Pod存储
容器支持10GiB的临时存储空间，对临时存储的修改在Pod重启后会丢失，如有需要推荐挂载持久化存储。   
持久化存储：支持挂载UDisk、NFS、ConfigMap、Secret，不支持其他类型的volume，例如 `hostPath` , `projected volume` 等。注意：挂载ConfigMap和Secret时，总配置大小不能超过30MiB。

### 镜像仓库
支持拉取UHub以及同地域下的自建镜像仓库(仅使用UHost自建仓库)，不支持拉取外网镜像，如DockerHub；并且镜像大小不能超过10GiB。
### 其他功能
支持日志， `exec` ，监控等基本功能；可以使用Deployment、StatefulSet等Kubernetes控制器进行控制。   
其他与Kubernetes原生Pod兼容性一致。
