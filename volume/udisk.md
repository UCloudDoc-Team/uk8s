{{indexmenu_n>1}}
## 在UK8S中使用UDISK

UK8S支持直接在集群中使用UDisk作为持久化存储卷。

**备注:**

1. 支持SSD/SATA UDisk；

2. SSD UDisk的最小值为20GB，最大值为8000GB；

3. UDisk的步长为10GB，即你只能创建20GB、30GB、110GB的存储卷；

###一、存储类 StorageClass

在创建持久化存储卷（persistentVolume）之前，你需要先创建StorageClass，然后在PVC中使用StorageClassName。

2019年1月22日之后的UK8S集群，有两个默认的StorageClass，名称分别为udisk-ssd和udisk-sata。

你也可以创建一个新的StorageClass，示例及说明如下：
```
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: udisk-ssd-test
provisioner: ucloud/udisk
parameters:
  type: ssd
reclaimPolicy: Retain
```

**provisioner: ** 存储供应方，此处必须为`ucloud/udisk`，否则创建出来的StorageClass可能无效。

**parameters.type：** Udisk的存储介质类型，支持ssd和sata，默认为ssd。

**reclaimPolicy：** 回收策略，支持Delete和Retain，默认为Delete。


2019年1月22日之前创建的UK8S集群，StorageClass示例如下，provisionner不同，不支持选择存储类型。
```
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: cloud
provisioner: archon.kubeup.com/ucloud
reclaimPolicy: Retain
```

### 二、创建持久化存储卷声明（PVC）
```
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

###三、在pod中使用PVC

```
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