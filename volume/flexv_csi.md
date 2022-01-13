# 从 Flexvolume UDisk 存储卷升级到 CSI UDisk 存储卷

Kubernetes v1.13 以及更早版本的用户，Pod 通过 Flexvolume 存储卷的方式挂载 UDisk 块存储卷。由于不支持拓扑感知动态调度等基础特性，Flexvolume
方案早已停止演进，而 CSI 已经成为容器存储实现标准。

使用 Flexvolume 创建 UDisk 挂载卷的 UK8S 早期用户目前面临着集群升级时将 Flexvolume PV 转换成 CSI PV
的问题，本文档提供一个示例，用于说明如何完成这一转换。

> ⚠️ 升级时会造成服务中断，请合理规划迁移时间，并做好相关备份。

## 1. Flexvolume UDisk 存储卷说明

如下是一个已经挂载了 Flexvolume UDisk 存储卷 Workload 的 yaml 文件 nginx-fv.yaml，它包含了一个 StorageClass，一个 Pod 声明和其引用的
PVC。

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: udisk-ssd-flexvolume
parameters:
  type: ssd # 磁盘类型，枚举值为ssd,sata,rssd
provisioner: ucloud/udisk
reclaimPolicy: Delete
volumeBindingMode: Immediate
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: nginx-fv
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: udisk-ssd-flexvolume
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:latest
    imagePullPolicy: Always
    ports:
    - containerPort: 8080
    volumeMounts:
    - name: nginxdisk
      mountPath: /data
  volumes:
  - name: nginxdisk
    persistentVolumeClaim:
      claimName: nginx-fv
```

执行 `kubectl apply -f nginx-fv.yaml`，发现相应的 StorageClass、Pod 及相关联的 PVC 已经创建成功，此外 cloudprovider 还会为这个
PVC 创建并绑定一个 PV 对象（名称与 PVC 对象的 **Volume** 值相同），如下所示：

```yaml
Name:            pvc-8b7946f7-1214-11ec-8f6b-5254003e805f-bsm-upc4bc0v
Labels:          <none>
Annotations:     pv.kubernetes.io/provisioned-by: ucloud/udisk
Finalizers:      [kubernetes.io/pv-protection]
StorageClass:    udisk-ssd-flexvolume
Status:          Bound
Claim:           default/nginx-fv
Reclaim Policy:  Delete
Access Modes:    RWO
VolumeMode:      Filesystem
Capacity:        10Gi
Node Affinity:   <none>
Message:         
Source:
    Type:       FlexVolume (a generic volume resource that is provisioned/attached using an exec based plugin)
    Driver:     ucloud/flexv
    FSType:     
    SecretRef:  nil
    ReadOnly:   false
    Options:    map[diskId:bsm-upc4bc0v]
Events:         <none>
```

在 Source.Options 可以发现，这个 PV 对应的实际 UDisk 实例为 bsm-upc4bc0v。

## 2. 升级步骤

> ⚠️ 升级时会造成服务中断，请合理规划迁移时间，准备好所有需要的 yaml 文件，并做好相关备份。

### 2.1 确认原有 PV 回收策略为 Retain

如果 PV 的回收策略不是 **Retain**，则需要通过以下命令将其回收策略改成 **Retain**。这时即使您删除 Pod 和对应的 PVC，可以发现，PV 依然存在，对应的 UDisk
实例也依然保留。

> ⚠️ 如删除 Flexvolume 创建的 PV，则对应的 UDisk 会被删除，如需要相应的 UDisk，请确保该 PV 不会被删除。

```
kubectl patch pv <your-pv-name1> <your-pv-name2> <your-pv-name3> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```

### 2.2 确认集群中已安装 CSI 插件

首先，请参考[CSI 升级指南](/uk8s/volume/CSI_update)中命令行升级的方法，为集群安装最新的 CSI 插件。

### 2.3 删除原有 Pod 及 PVC

通过 `kubectl delete -f nginx-fv.yaml`，删除原有 PVC 及 Pod，这时可以发现由于 PV 回收策略为 **Retain**，PV 及相应的 UDisk
仍被保留，PV 状态为 **Release**。

### 2.4 通过 CSI 以指定 UDisk 创建新的 PV 及 PVC

接下来，我们将以原先的 UDisk 数据盘，创建 PV 并关联 PVC，详见[在 UK8S 中使用 UDisk](/uk8s/volume/udisk)文档中「使用已有 UDisk 部分」。

以下为示例文件 nginx-csi-pv.yaml

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nginx-csi
spec:
  accessModes:
  - ReadWriteOnce
  capacity:
    storage: 10Gi
  csi:
    driver: udisk.csi.ucloud.cn
    volumeAttributes:
      type: ssd
    volumeHandle: bsm-upc4bc0v # 请修改为自己的UDiskId
  persistentVolumeReclaimPolicy: Retain
  storageClassName: udisk-ssd
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: nginx-csi
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: udisk-ssd
  resources:
    requests:
      storage: 10Gi
  volumeName: nginx-csi
```

执行 `kubectl apply -f nginx-csi-pv.yaml` 后，我们可以看到新的 PV 和 PVC 已经创建成功。

### 2.5 将 PVC 挂载到相应的 Pod

详见[在 UK8S 中使用 UDisk](/uk8s/volume/udisk)文档，以下为示例 yaml 文件 nginx-csi.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:latest
    imagePullPolicy: Always
    ports:
    - containerPort: 8080
    volumeMounts:
    - name: nginxdisk
      mountPath: /data
  volumes:
  - name: nginxdisk
    persistentVolumeClaim:
      claimName: nginx-csi # 注意名称与新的 PVC 相对应
```

执行 `kubectl apply -f nginx-csi.yaml` 后，我们可以看到新的 Pod 已经创建成功，并与相应的 PVC 绑定。

> 升级成功后，原有的 FlexVolume 安装文件可保留，只要在申明新的 StorageClass、PV 和 PVC 时，按照 CSI 相应的规范进行声明即可。
