# 在UK8S中使用UDISK

UK8S支持直接在集群中使用UDisk作为持久化存储卷。

**备注:**

1. 所有云主机均支持 SSD/SATA UDisk，**如果节点的云主机类型为快杰，则也支持 RSSD UDisk**；

2. SSD/SATA UDisk的最小值为 1GB，最大值为8000GB，RSSD UDisk 最大值为 32000GB；

3. UDisk和云主机必须位于同一可用区，如果您的集群是跨可用区模式，在应用部署的时候请注意。

4. 如果使用快杰云主机及 RSSD UDisk，则 UDisk 和云主机除在同一个可用区外，**也需要在同一个 RDMA 区域**，RDMA 区域范围小于可用区，如在集群中使用已有 UDisk，有可能因 RDMA 区域不一致出现挂载失败的情况；

5. 同一个 Pod 如果挂载多块 UDisk，则必须确保 UDisk 处于同一可用区，否则容器无法启动。

## 一. 存储类 StorageClass

在创建持久化存储卷（PersistentVolume）之前，你需要先创建 StorageClass，然后在 PVC 中使用 StorageClassName。

UK8S 集群默认创建了两个 StorageClass，你也可以创建一个新的StorageClass，示例及说明如下：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: udisk-ssd-test
provisioner: udisk.csi.ucloud.cn #存储供应方，此处不可更改。
parameters:
  type: "ssd"   # 存储介质，支持ssd和sata，必填
  fsType: "ext4"    # 文件系统，必填
  udataArkMode: "no"   # 是否开启方舟模式，默认不开启，非必填
  chargeType: "month" # 付费类型，支持dynamic、month、year,不填默认为按小时。
  quantity: "1" # 购买时长，dynamic无需填写，可购买1-9个月，或1-10年
reclaimPolicy: Delete  # PV回收策略，支持Delete和Retain，默认为Delete，非必填
volumeBindingMode: WaitForFirstConsumer   # 强烈建议配置该参数
mountOptions:   
  - debug
  - rw
```
备注：1.15之前的Kubernetes版本，mountOptions无法正常使用，请勿填写，详见[Issue80191](https://github.com/kubernetes/kubernetes/pull/80191) 


## 二. 创建持久化存储卷声明 PVC


### 1. 新建 UDisk

> 使用新建 UDisk，则可直接创建 PVC 对象，CSI 会自动创建 UDisk 并关联。

>

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test-pvc-claim
spec:
  accessModes:
    - ReadWriteOnce
## storageClassName必须与上文创建的 StorageClass 的name一致
  storageClassName: udisk-ssd-test
  resources:
    requests:
      storage: 20Gi
```


### 2. 使用已有 UDisk

> 如需使用已有 UDisk，需先创建 PV 对象并与已有 UDisk 绑定，再创建 PVC 对象、使用与 PV 相同的声明进行关联

#### 创建持久化存储卷 PV

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: test-pvc-claim
spec:
  accessModes:
  - ReadWriteOnce
  capacity:
    storage: 20Gi
  csi:
    driver: udisk.csi.ucloud.cn
    volumeAttributes:
      type: ssd # 磁盘类型，枚举值为ssd,sata,rssd
    volumeHandle: bs-qg55w254 # 请修改为自己的UDiskId
  persistentVolumeReclaimPolicy: Retain
## storageClassName必须与上文创建的 StorageClass 的name一致
  storageClassName: udisk-ssd-test
```

#### 创建 PVC 并与 PV 关联

**spec.storageClassName**、**spec.resources.requests.storage**、**volumeName**需要与pv相对应。

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test-pvc-claim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: udisk-ssd-test
  resources:
    requests:
      storage: 20Gi
  volumeName: test-pvc-claim
```

## 三. 在 Pod 中使用 PVC

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:latest
    volumeMounts:
    - name: test
      mountPath: /data
    ports:
    - containerPort: 80
  volumes:
  - name: test
    persistentVolumeClaim:
      claimName: test-pvc-claim
```