{{indexmenu_n>2}}
## 在UK8S中使用已有UDISK

### 已创建云盘在UK8S中进行挂载

已创建UDisk云盘如图显示，其中资源ID、和类型，在集群中挂载时需要使用。

![](\images\volume\have_udisk.png)

在集群中创建StorageClass或修改已有的StorageClass，其中**provisioner**需要对应使用ucloud/udisk，**parameters.type**需要对应上图已创建的ssd磁盘类型，**reclaimPolicy**回收策略需要设置为Retain。

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

创建pv对象使其对应使用已有UDisk硬盘。

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: flexv-existing-udisk
spec:
  accessModes:
  - ReadWriteOnce
  capacity:
    storage: 20Gi
  flexVolume:
    driver: ucloud/flexv
    options:
      diskId: bsm-bh3elplr
      mountFlags: ""
  persistentVolumeReclaimPolicy: Retain
  storageClassName: udisk-ssd-test
```
创建pvc对象使用与pv相同的声明进行关联，其中**spec.storageClassName**、**spec.resources.requests.storage**、**volumeName**需要与pv相对应。

```
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: flexv-existing-udisk
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: udisk-ssd-test
  resources:
    requests:
      storage: 20Gi
  volumeName: flexv-existing-udisk
```
如下操作命令可以发现，上一步创建的pv flexv-existing-udisk已经被绑定到了新的pvc。
```
[root@10-9-63-194 statuspv]# kubectl apply -f pv.yaml 
persistentvolume/flexv-existing-udisk created
[root@10-9-63-194 statuspv]# kubectl get pv
NAME                   CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS     REASON   AGE
flexv-existing-udisk   20Gi       RWO            Retain           Available           udisk-ssd-test            6s
[root@10-9-63-194 statuspv]# kubectl apply -f pvc.yaml 
persistentvolumeclaim/flexv-existing-udisk created
[root@10-9-63-194 statuspv]# kubectl get pvc
NAME                   STATUS   VOLUME                 CAPACITY   ACCESS MODES   STORAGECLASS     AGE
flexv-existing-udisk   Bound    flexv-existing-udisk   20Gi       RWO            udisk-ssd-test   4s
[root@10-9-63-194 statuspv]# kubectl get pv
NAME                   CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                          STORAGECLASS     REASON   AGE
flexv-existing-udisk   20Gi       RWO            Retain           Bound    default/flexv-existing-udisk   udisk-ssd-test            22s
```

### Pod删除后，如何复用原先的云盘？

首先pvc中的StorageClass里的回收策略reclaimPolicy必须设置成Retain。可参照上面静态UDisk磁盘关联方法进行PVC创建。
