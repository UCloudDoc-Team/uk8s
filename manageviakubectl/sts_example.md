## StatefulSet部署示例

在部署一些有状态的服务如 Redis、MySQL 等时，我们需要使用到 StatefulSet 这个控制器，下面介绍下如果在 UK8S 中使用 UDisk 来部署 StatefulSet 服务。

### 了解StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: db
spec:
  selector:
    matchLabels:
      app: mysql
  replicas: 5
  serviceName: mysql
  template:
    PodTemplateSpec..... # 有大量省略，与Deployment一样，是关于要控制的Pod的描述
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: ${YOUR_STORAGECLASS_NAME}
      resources:
        requests:
          storage: 10Gi
```

如果我们熟悉 Deployment 的结构体，则会发现其与 StatefulSet 最大的区别在于**volumeClaimTemplates**，其他地方则基本一致。

我们细看下**volumeClaimTemplates**，发现其结构体与“PersistentVolumeClaim”完全一致，没错，**volumeClaimTemplates**其实就是PVC的模板，用来生成多个访问模式为**单点读写**的PVC，供
StatefulSet 管理的 Pod 使用。

像上面的示例，StatefulSet 不仅会创建出5个 Pod，同时也还会创建出5个 PVC，供对应的Pod使用，以实现每个 Pod 都具有独立的存储状态。

### PVC 示例

对于有状态服务，我们推荐使用SSD UDisk、RSSD UDisk作为存储介质，当然，我们也可以使用LocalPV，但由于目前大多数云主机的数据盘也都是云盘，直接使用 LocalPV
还有各种限制，因此**强烈推荐使用 UDisk 作为存储介质**

UK8S 集群在初始化的时候，已经内置了三个与 UDisk 相关的存储类，我们只需要直接引用存储类创建 PVC 供 Pod 消费即可。下面介绍下如何创建对应的PVC。

> ⚠️ **RSSD UDisk调度要求同一个RDMA区域的快杰型云主机，RDMA区域范围小于可用区，主机目前不支持指定RDMA区域创建机器。因此使用RSSD
> UDisk，在Pod漂移的情况下，有可能出现Pod无法调度的问题。请您使用前务必确认可以接受该风险。**

1. 使用RSSD UDisk

```yaml
volumeClaimTemplates:
  - metadata:
      name: ${YOUR_NAME} # 需要与VolumeMount的名称保持一致;
    spec:
      storageClassName: csi-udisk-rssd #这是集群内置的StorageClass
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 100Gi
```

上面我们使用的是集群内置的 StorageClass，我们也可以根据创建新的
SC，详见[使用RSSD UDisk](https://docs.ucloud.cn/uk8s/volume/rssdudisk)

2. 使用SSD UDisk

```yaml
volumeClaimTemplates:
  - metadata:
      name: ${YOUR_NAME} 
      labels:
        name: redis-cluster
    spec:
      storageClassName: ssd-csi-udisk #这是自行创建的存储介质为SSD UDisk的StorageClass
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 20Gi
```

我们看到，需要使用不同的存储介质，只需要在创建PVC时声明不同的storageClassName即可。下面我们介绍下如果创建自定义StorageClass。

3. 声明自定义的StorageClass(UDisk 类型)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: udisk-ssd-test
provisioner: udisk.csi.ucloud.cn #存储供应方，此处不可更改。
parameters:
  type: "ssd"   # 存储介质，支持ssd和sata、rssd，必填
  fsType: "ext4"    # 文件系统，必填
  udataArkMode: "no"   # 是否开启方舟模式，默认不开启，非必填
  chargeType: "month" # 付费类型，支持dynamic、month、year，非必填
  quantity: "1" # 购买时长，dynamic无需填写，可购买1-9个月，或1-10年
reclaimPolicy: Retain  # PV回收策略，支持Delete和Retain，默认为Delete，非必填
mountOptions:   
  - debug
  - rw
```

上面的示例涵盖了 UDisk 的StorageClass的全部参数，我们可以根据业务需要来自定义 SC。

### StatefulSet 示例

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
    name: web
  clusterIP: None
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx # has to match .spec.template.metadata.labels
  serviceName: "nginx"
  replicas: 3 # by default is 1
  template:
    metadata:
      labels:
        app: nginx # has to match .spec.selector.matchLabels
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
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "csi-udisk-rssd"  # has to match a storageClassname existed in  your cluster
      resources:
        requests:
          storage: 100Gi
```

在上面的示例中，我们声明的名称为 Web 的 StatefulSet 控制器，将创建一个3个nginx Pod，并且为每个Pod分别挂载一个RSSD UDisk，以供其存储数据。
