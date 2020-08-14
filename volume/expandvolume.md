## UDisk 在线扩容

本文档主要描述如何在UK8S中扩容UDisk类型的PVC。

### 1、限制条件

1. UK8S Node节点实例的创建时间必须晚于2020年5月，不满足此条件的节点，则必须先对Node节点进行先关机，再开机操作;

2. Kubernetes版本不低于1.14。1.14和1.15必须开启--feature-gates=ExpandCSIVolumes=true; 1.16及以上无需配置;

3. CSI-UDisk版本不低于20.08.1 ;

4. 扩容时声明的期望容量大小应该是10的整数倍，单位为Gi;

5. 只支持动态创建的PVC扩容，且storageClass必须显示声明可扩容(见后文)；


### 2、准备操作

#### 2.1 升级CSI-UDisk版本

2.1.1. 检查CSI-UDisk版本，确认是否要升级

如下所示，如果CSI-UDisk的版本低于20.08.1,则需要升级CSI-UDisk版本。

```bash

# kubectl describe sts csi-udisk-controller  -n kube-system | grep csi-uk8s

    Image:      uhub.service.ucloud.cn/uk8s/csi-uk8s:20.03.1

```

2.2.2. 升级CSI-UDisk到20.08.1

```bash

# kubectl apply -f http://uk8s.cn-bj.ufileos.com/CSI/CSI-UDisk20.08.1/deploy_udisk_csi-controller.yml

# kubectl apply -f http://uk8s.cn-bj.ufileos.com/CSI/CSI-UDisk20.08.1/deploy_udisk_csi-node.yml

# kubectl apply -f http://uk8s.cn-bj.ufileos.com/CSI/CSI-UDisk20.08.1/deploy_udisk_rbac-controller.yml

# kubectl apply -f http://uk8s.cn-bj.ufileos.com/CSI/CSI-UDisk20.08.1/deploy_udisk_rbac-node.yml

```

#### 2.2 UK8S开启ExpnadCSIVolumes=true特性

仅1.14和1.15两个K8S版本中需要开启，1.16及以上已默认开启，1.13及以下版本不支持该特性。


#### 2.3 检查UK8S Node节点创建时间

如果节点创建时间早于2020年5月，该节点可能不支持在线扩容UDisk，此时需要先将该节点关机，再执行开机。

为了避免运行在节点上的业务受到影响，建议关机之前先执行Drain命令。

```bash

#  kubectl drain node-name --grace-period=900

```

### 3. 扩容UDisk演示

#### 3.1 创建UDisk存储类，显式声明可扩容

```yaml

apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-udisk-ssd
provisioner: udisk.csi.ucloud.cn
parameters:
  type: "ssd" 
  fsType: "ext4" 
  udataArkMode: "yes"  
reclaimPolicy: Delete 
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true  

```

>> 1、allowVolumeExpansion必须设置为true；2、provisioner必须为 udisk.csi.ucloud.cn;

#### 3.2 通过该存储类创建PVC，并挂载到Pod

```yaml

kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: udisk-volume-expand
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: csi-udisk-ssd
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: udisk-expand-test
  labels:
    app: udisk
spec:
  containers:
  - name: http
    image: uhub.service.ucloud.cn/ucloud/nginx:1.17.10-alpine 
    imagePullPolicy: Always
    ports:
    - containerPort: 8080
    volumeMounts:
    - name: udisk
      mountPath: /data
  volumes:
  - name: udisk
    persistentVolumeClaim:
      claimName: udisk-volume-expand

```

Pod启动后，我们分别查看下pvc、pv、以及容器内的文件系统大小，可以发现，目前都是10Gi

```bash

# kubectl  get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                         STORAGECLASS    REASON   AGE
pvc-25b83584-35de-43e4-ad23-c1fc638a09e2   10Gi       RWO            Delete           Bound    default/udisk-volume-expand   ssd-csi-udisk            2m26s

# kubectl  get pvc
NAME                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS    AGE
udisk-volume-expand   Bound    pvc-25b83584-35de-43e4-ad23-c1fc638a09e2   10Gi       RWO            ssd-csi-udisk   2m30s

# kubectl  exec -it udisk-expand-test -- df -h
Filesystem      Size  Used Avail Use% Mounted on
...
/dev/vdc        9.8G   37M  9.7G   1% /data
...

```

#### 3.3 在线扩容PVC

执行kubectl edit pvc udisk-volume-expand，将spec.resource.requests.storage改成20Gi, 保存后退出， 大概在一分钟左右，pv、pvc以及容器内的文件系统大小容量属性都变成了20GB。


```bash

# kubectl  get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                         STORAGECLASS    REASON   AGE
pvc-25b83584-35de-43e4-ad23-c1fc638a09e2   20Gi       RWO            Delete           Bound    default/udisk-volume-expand   ssd-csi-udisk            2m26s

# kubectl  get pvc
NAME                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS    AGE
udisk-volume-expand   Bound    pvc-25b83584-35de-43e4-ad23-c1fc638a09e2   20Gi       RWO            ssd-csi-udisk   2m30s

# kubectl  exec -it udisk-expand-test -- df -h
Filesystem      Size  Used Avail Use% Mounted on
...
/dev/vdc        20G   37M  19.7G   1% /data
...

```
同时登录UDisk控制台，发现UDisk展示容量也增大到了20Gi。这样我们完成了Pod不重启，服务不停机的数据卷在线扩容。

#### 3.4 离线扩容PVC(推荐)

在上面的示例中，我们完成了数据卷的在线扩容。但在高IO的场景下，Pod不重启进行数据卷扩容，有小概率导致文件系统异常。最稳定的扩容方案是先停止应用层服务、解除挂载目录，再进行数据卷扩容。下面我们演示下如何进行停服操作。

上文步骤3.3完成的时候，我们有一个Pod且挂载了一个20Gi的数据卷，现在我们需要对数据卷进行停服扩容。

1. 基于上文的示例yaml，去掉PVC相关的内容，单独创建一个名为udisk-expand-test的yaml，只保留Pod的相关信息。然后删除Pod，但保留pvc和pv。

```bash
# kubectl  delete po udisk-expand-test
pod "udisk-expand-test" deleted

```
此时，pv和pvc依然相互Bound，对应的UDisk已经从云主机中卸载，处于可用状态。 

2. 修改pvc信息，将spec.resource.requests.storage改成30Gi, 保存并退出。

等待一分钟左右后，执行kubectl get pv，当pv的容量增长到30G后，重建Pod。需要注意的是，此时执行kubectl get pvc的时候，返回的pvc容量依然是20Gi，这是因为文件系统尚未扩容完毕，pvc处于FileSystemResizePending状态。

```bash
# kubectl edit pvc udisk-volume-expand
persistentvolumeclaim/udisk-volume-expand edited

# kubectl  get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                   STORAGECLASS    REASON   AGE
pvc-25b83584-35de-43e4-ad23-c1fc638a09e2   30Gi       RWO            Delete           Bound    default/udisk-volume-expand   ssd-csi-udisk            20m

# kubectl create -f udisk-expand-test.yml

```

当Pod重新创建成功后，可以发现，pv，pvc的容量大小的容量都是30Gi，同时在容器中执行df看到的对应文件系统容量也是30Gi。



