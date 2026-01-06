# 在UK8S中使用UDISK

UK8S支持直接在集群中使用UDisk作为持久化存储卷。

**备注:**

1. 所有云主机均支持 SSD/SATA UDisk，**如果节点的云主机类型为快杰，则也支持 RSSD UDisk**；

2. SSD/SATA UDisk的最小值为 1GB，最大值为8000GB，RSSD UDisk 最大值为 32000GB；

3. UDisk和云主机必须位于同一可用区，如果您的集群是跨可用区模式，在应用部署的时候请注意。

4. **RSSD云盘有额外的限制条件，请见[在UK8S中使用RSSD UDisk](/uk8s/volume/rssdudisk)。**

5. UDisk以10g为计费单位，不满10g按10g计算，超过10g向上取整到10的整数倍;

## 1. 存储类 StorageClass

在创建持久化存储卷（PersistentVolume）之前，你需要先创建 StorageClass，然后在 PVC 中使用 StorageClassName。

UK8S 集群默认为您创建了该地域可用的云盘类型对应的 StorageClass，您也可以创建一个新的StorageClass，示例及说明如下：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: udisk-ssd-new
provisioner: udisk.csi.ucloud.cn #存储供应方，此处不可更改。
parameters:
  type: "ssd"   # 存储介质，可用选项: sata / ssd / rssd / essd, 必填
  fsType: "ext4"    # 文件系统，必填
  udataArkMode: "no"   # 是否开启方舟模式，默认不开启，非必填
  chargeType: "month" # 付费类型，支持dynamic、month、year, 不填默认为按小时。
  quantity: "1" # 购买时长，dynamic无需填写，可购买1-9个月，或1-10年
reclaimPolicy: Delete  # PV回收策略，支持Delete和Retain，默认为Delete，非必填
volumeBindingMode: WaitForFirstConsumer   # 强烈建议配置该参数
allowVolumeExpansion: true # 声明该存储类支持可扩容特性
mountOptions:
  - debug
  - rw
```

备注：1.15之前的Kubernetes版本，mountOptions无法正常使用，请勿填写，详见[Issue80191](https://github.com/kubernetes/kubernetes/pull/80191)

## 2. 创建持久化存储卷声明 PVC

### 2.1 新建 UDisk

> 使用新建 UDisk，则可直接创建 PVC 对象， CSI 会自动创建 UDisk 并关联。如果storageClass中的 [volumeBindingMode](https://kubernetes.io/docs/concepts/storage/storage-classes/#volume-binding-mode) 设置为 WaitForFirstConsumer，则需要等待Pod使用PVC后才会创建真正的UDisk。

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

### 2.2 使用已有 UDisk

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
#  nodeAffinity：强烈建议添加此字段
  persistentVolumeReclaimPolicy: Retain
#  storageClassName必须与上文创建的 StorageClass 的name一致
  storageClassName: udisk-ssd-test
```

注意：根据[使用UDisk的Pod调度策略](/uk8s/troubleshooting/storage#_9-挂载udisk的pod调度问题)，为了保证后续调度可以顺利执行，强烈建议您创建时为PV添加`nodeAffinity`字段。由于不同版本以及不同Storage
Class本部分的内容不尽相同，可以参照相同Storage Class CSI自动自动创建出来PV的对应字段。

#### 2.3 创建 PVC 并与 PV 关联

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

## 3. 在 Pod 中使用 PVC

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

## 4. 使用StatefulSet

如果有部署多副本有状态应用的需求，建议使用StatefulSet而不是Deployment，因为Deployment中多个pod会共享同一个磁盘，如果pod在不同节点就会导致问题。而StatefulSet能让多个pod使用自己的磁盘。

一般会使用StatefulSet来为每个pod动态创建pvc和udisk磁盘，下面的yaml可以作为参考：

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx
  serviceName: "nginx"
  replicas: 4
  template:
    metadata:
      labels:
        app: nginx
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: nginx
        image: uhub.service.ucloud.cn/ucloud/nginx:latest
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          # 云盘挂载的目录
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      # 要使用的StorageClass，表明要创建什么类型的磁盘
      storageClassName: "udisk-ssd-test"
      resources:
        requests:
          storage: 20Gi
```
