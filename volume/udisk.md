
## 在UK8S中使用UDISK

UK8S支持直接在集群中使用UDisk作为持久化存储卷。

**备注:**

1. 非快杰云主机支持SSD/SATA UDisk，**如果节点的云主机类型为快杰，则只支持RSSD UDisk**；

2. SSD UDisk的最小值为1GB，最大值为8000GB；

3. UK8S有flexVolume和CSI两种存储插件版本，2019年9月17日之后创建的UK8S集群为CSI，其余为flexVolume，两者的主要区别在StorageClass部分。

4. UDisk和云主机必须位于同一可用区，如果您的集群是跨可用区模式，在应用部署的时候请注意。

### 一、存储类 StorageClass

在创建持久化存储卷（persistentVolume）之前，你需要先创建StorageClass，然后在PVC中使用StorageClassName。


UK8S集群默认创建了两个StorageClass，你也可以创建一个新的StorageClass，示例及说明如下：


#### 1、CSI版本（2019年9月17日之后创建的UK8S集群）
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
  chargeType: "month" # 付费类型，支持dynamic、month、year，非必填
  quantity: "1" # 购买时长，dynamic无需填写，可购买1-9个月，或1-10年
reclaimPolicy: Delete  # PV回收策略，支持Delete和Retain，默认为Delete，非必填
mountOptions:   
  - debug
  - rw
```
备注：1.15之前的Kubernetes版本，mountOptions无法正常使用，请勿填写，详见[Issue80191](https://github.com/kubernetes/kubernetes/pull/80191) 

#### 2、flexVolume版本(2019年9月17日之前创建的UK8S集群)
```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: udisk-ssd-test
provisioner: ucloud/udisk
parameters:
  type: ssd
reclaimPolicy: Retain
```

**provisioner:** 存储供应方，此处必须为`ucloud/udisk`，否则创建出来的StorageClass可能无效。

**parameters.type:** UDisk的存储介质类型，支持ssd和sata，默认为ssd。

**reclaimPolicy:** 回收策略，支持Delete和Retain，默认为Delete。



### 二、创建持久化存储卷声明（PVC）

>storageClassName必须与上文创建的StorageClass的name一致。

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
```

### 三、在pod中使用PVC

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
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
