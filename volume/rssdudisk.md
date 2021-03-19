
## 在UK8S中使用RSSD UDisk

RSSD UDisk最高IOPS可达120万、延时低于0.1ms，数据持久性为99.999999%，最大容量32000G，适用于数据库、Elastic Search等需要低延时的IO密集型业务。UK8S支持将RSSD UDisk作为容器的持久化存储卷，但前提是集群中必须有快杰机型的节点(当前仅快杰云主机支持挂载RSSD UDisk)。

下面演示下如何在UK8S集群中使用RSSD UDisk。



### 限制条件

1. 集群中必须有快杰机型的节点，否则创建出来的PV将无法使用；

2. Kubernetes版本不低于1.14；

3. csi-udisk插件版本必须大于等于20.08.2;

4. StorageClass中的volumeBindingMode必须显式设置为WaitForFirstConsumer（否则创建出来的RSSD UDisk可能无法挂载）；


### 前置准备-->升级csi-udisk

1. 检查CSI-UDisk版本，确认是否要升级

如下所示，如果CSI-UDisk的版本低于20.08.2,则需要升级CSI-UDisk版本。

```bash

# kubectl describe sts csi-udisk-controller  -n kube-system | grep csi-uk8s

    Image:      uhub.service.ucloud.cn/uk8s/csi-uk8s:20.03.1

```

2.2.2. 升级CSI-UDisk到20.08.2

```bash

# kubectl apply -f http://uk8s.cn-bj.ufileos.com/CSI/CSI-UDisk20.08.2/deploy_udisk_csi-controller.yml

# kubectl apply -f http://uk8s.cn-bj.ufileos.com/CSI/CSI-UDisk20.08.2/deploy_udisk_csi-node.yml

# kubectl apply -f http://uk8s.cn-bj.ufileos.com/CSI/CSI-UDisk20.08.2/deploy_udisk_rbac-controller.yml

# kubectl apply -f http://uk8s.cn-bj.ufileos.com/CSI/CSI-UDisk20.08.2/deploy_udisk_rbac-node.yml

```

### 使用示例

1. 创建StorageClass, 注意paramater.type为rssd，volumeBindingMode为WaitForFirstConsumer。如果你的CSI-UDisk版本大于20.08.2，集群已默认创建好RSSD UDisk 类型的StorageClass，则该步骤可略过。

```yaml

apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-udisk-rssd
provisioner: udisk.csi.ucloud.cn
parameters:
  type: "ssd"   # 存储介质，支持ssd和sata，必填
  fsType: "ext4"    # 文件系统，必填
  udataArkMode: "no"   # 是否开启方舟模式，默认不开启，非必填
  chargeType: "month" # 付费类型，支持dynamic、month、year,不填默认为按小时。
  quantity: "1" # 购买时长，dynamic无需填写，可购买1-9个月，或1-10年
reclaimPolicy: Delete 
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

```

2. 创建PVC,这部分与创建SATA、SSD UDisk的PVC完全一致。

```yaml

kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: logdisk-claim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: csi-udisk-rssd
  resources:
    requests:
      storage: 10Gi

```

3. 创建Pod, 注意设置NodeAffinity，确保Pod被调度到快杰Node上。如果你的集群节点的主机类型全部是快杰，则无需设置NodeAffinity。

>> CSI会保证创建出的云盘与Pod所在Node处于同一个RDMA区域，这样才能确保RSSD UDisk成功挂载云主机。


```yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: http
  labels:
    app: http
spec:
  strategy:
    type: Recreate
  replicas: 1
  selector:
    matchLabels:
      app: http
  template:
    metadata:
      labels:
        app: http
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node.uk8s.ucloud.cn/machine_type 
                operator: In
                values:
                - O
                - OS
      containers:
      - name: http
        image: uhub.service.ucloud.cn/wxyz/httpudisk:1.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: log
          mountPath: /data
      volumes:
      - name: log
        persistentVolumeClaim:
          claimName: logdisk-claim

```


