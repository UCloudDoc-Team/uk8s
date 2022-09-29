# 在UK8S中使用RSSD UDisk

RSSD UDisk最高IOPS可达120万、延时低于0.1ms，数据持久性为99.999999%，最大容量32000G，适用于数据库、Elastic
Search等需要低延时的IO密集型业务。UK8S支持将RSSD UDisk作为容器的持久化存储卷，但前提是集群中必须有快杰机型的节点(当前仅快杰云主机支持挂载RSSD UDisk)。

下面演示下如何在UK8S集群中使用RSSD UDisk。

## 限制条件

1. 集群中必须有快杰机型的节点，否则创建出来的PV将无法使用；

2. Kubernetes版本不低于1.18；

3. **csi-udisk插件版本必须大于等于`22.09.1`，如果小于，请到控制台升级，详情见[RSSD云盘挂载问题](/uk8s/troubleshooting/rssd_attachment);**

4. StorageClass中的volumeBindingMode必须显式设置为WaitForFirstConsumer（否则创建出来的RSSD UDisk可能无法挂载）；

## 使用示例

1. 创建PVC,这部分与创建SATA、SSD UDisk的PVC完全一致。

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

2. 创建Pod

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
