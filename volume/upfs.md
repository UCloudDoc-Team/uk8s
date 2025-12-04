# 在UK8S中使用UPFS

本文档介绍如何在UK8S集群中，使用UPFS作为K8S底层的存储支持，UPFS为共享存储，可以同时为多个Pod提供服务。

## UPFS 使用必读

* UPFS产品目前仅支持部分地域

* **UPFS的其他限制条件，请见[UPFS产品使用限制](https://docs.ucloud.cn/upfs/upfs_manual_instruction/limit)**

## 前置条件

设置UPFS挂载点：在[UFS产品页面](https://console.ucloud.cn/upfs/)购买UPFS实例并设置好挂载点，操作完毕后，您会得到两个UPFS挂载地址，类似：
```
101.66.127.139:10109,101.66.127.140:10109
```

## 手动部署CSI

> ⚠️ 如果您目前已经在使用旧版本(低于25.06.27)的UPFS CSI，请联系我们了解CSI升级方案，切勿直接升级！直接升级可能导致数据访问异常。


因目前的UK8S版本均不默认安装UPFS CSI，需要自行部署。请按顺序执行如下命令即可。

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/upfs-25.12.04-cli-v14.10/rbac-controller.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/upfs-25.12.04-cli-v14.10/rbac-node.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/upfs-25.12.04-cli-v14.10/csi-controller.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/upfs-25.12.04-cli-v14.10/csi-node.yml
```

## 创建存储类StorageClass

接下来进行创建StorageClass操作；创建StorageClass时需要注意参数:

* uri：UPFS文件系统URL。URL详细规则请见[UPFS主要概念](https://docs.ucloud.cn/upfs/upfs_manual_instruction/concept?id=%e6%96%87%e4%bb%b6%e7%b3%bb%e7%bb%9furl)

* path：表示需要挂载的UPFS子目录，默认值为`/`。如果指定的子目录在UPFS实例中尚不存在，则会被自动创建。

* autoProvisionSubdir：upfs-csi版本 >= `upfs-25.06.27-cli-v14.0`时支持。默认不启用。开启该参数且配置值为`true`之后，该StorageClass创建出的PVC可以实现数据分离。每个PVC会按如下规则在UPFS上创建对应的子目录: `<path>/<pvc-namespace>-<pvc-name>-<pv-name>`

如当path配置为`/example`，且在`default` namespace中创建名为`logupfs-claim`的PVC时，UPFS实例中自动创建的目录名为

```
/example/default-logupfs-claim-pvc-ae961bc8-2c97-414e-9e7b-bde3e28efee9
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-upfs
provisioner: upfs.csi.ucloud.cn
parameters:
  uri: 101.66.127.139:10109,101.66.127.140:10109/upfs-xxxx
  path: /example
  # autoProvisionSubdir: "true"
```

> ⚠️ StorageClass中的 `uri`、`path`、`autoProvisionSubdir` 参数均不建议在使用中修改，否则会影响pv对应的数据路径，导致业务读取不到对应的数据；

## 创建PVC

将如下内容保存到文件： `upfspvc.yml`
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: logupfs-claim
spec:
  storageClassName: csi-upfs
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi # 因实际会将整个UPFS挂载到节点上，故此处的storage可任意配置并不做限制
```

然后执行如下kubectl命令创建PVC：

```shell
# kubectl apply -f upfspvc.yml
persistentvolumeclaim/logupfs-claim created
```

创建完PVC后，可以发现PV与PVC已经绑定。


```
# kubectl get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                   STORAGECLASS   REASON   AGE
pvc-ae961bc8-2c97-414e-9e7b-bde3e28efee9   256Ti      RWX            Delete           Bound    default/logupfs-claim   csi-upfs                12s
#
# kubectl get pvc
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
logupfs-claim   Bound    pvc-ae961bc8-2c97-414e-9e7b-bde3e28efee9   256Ti      RWX            csi-upfs       12s
```

> ⚠️ PVC中显示的容量，不做实际容量参考；PVC的真实容量务必以对应UPFS实例的容量为准；


## 在Pod中挂载UPFS

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-upfs
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: testupfs
      mountPath: /data
  volumes:
  - name: testupfs
    persistentVolumeClaim:
      claimName: logupfs-claim
```

创建完Pod之后，我们可以通过`kubectl exec`命令进入容器，执行df命令查看Pod是否挂载到UPFS

```
# df -h
Filesystem              Size  Used Avail Use% Mounted on
...
UPFS:upfs-xxxx          5.9T  8.5K  5.9T   1% /data
...
```

## 通过静态PV指定远程UPFS目录挂载

如果您希望指定挂载UPFS上的特定目录，可以通过声明静态PV的方式实现。请参考以下示例：

> ⚠️ UPFS CSI**不会**帮您创建远程子目录。您指定的远程目录必须已经在UPFS上存在。如果指定了挂载不存在的远程目录，Pod将无法正常启动。

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: static-upfs-pvc-1
spec:
  accessModes:
  - ReadWriteMany
  capacity:
    storage: 256Ti
  csi:
    driver: upfs.csi.ucloud.cn
    # 请将 `volumeHandle` 字段修改为 `<您的upfs挂载uri>/<远程目录路径>` 的形式
    volumeHandle: 100.65.128.139:10109,100.65.128.140:10109/upfs-1dcuqwz0e58u/path/to/my-data
  storageClassName: ""
  volumeMode: Filesystem
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: static-upfs-pvc-1
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 500Gi
  storageClassName: ""
  volumeMode: Filesystem
  volumeName: static-upfs-pvc-1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-static-upfs-1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-static-upfs-1
  template:
    metadata:
      labels:
        app: nginx-static-upfs-1
    spec:
      containers:
      - name: nginx
        image: uhub.service.ucloud.cn/ucloud/nginx:latest
        ports:
        - containerPort: 80
        volumeMounts:
        - name: static-upfs
          mountPath: /data
      volumes:
      - name: static-upfs
        persistentVolumeClaim:
          claimName: static-upfs-pvc-1
```

## 使用UPFS挂载参数

UPFS实例挂载时支持`forbidden_delete`、`forbidden_overwrite`、`forbidden_rename`、`forbidden_truncate`等[挂载参数](https://docs.ucloud.cn/upfs/upfs_guide/linux_mount?id=%e6%ad%a5%e9%aa%a4%e4%ba%8c%e3%80%81%e6%8c%82%e8%bd%bd%e6%96%87%e4%bb%b6%e7%b3%bb%e7%bb%9f)。如果您希望在使用PVC挂载时也应用挂载参数，请参考以下示例进行配置。

> ⚠️ 使用挂载参数前，确认您的UPFS CSI版本不低于 `upfs-25.09.08-cli-v14.7`

#### 动态PV使用挂载参数

在存储类中增加`mountOptions`参数，如下所示:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: upfs-example-forbidden-delete
provisioner: upfs.csi.ucloud.cn
parameters:
  uri: 100.65.128.139:10109,100.65.128.140:10109/upfs-xxxx
  path: /example
  # autoProvisionSubdir: "true"
mountOptions:
  - forbidden_delete
  - forbidden_rename
  - forbidden_overwrite
  - forbidden_truncate
```

指定`storageClassName`为`upfs-example-forbidden-delete`创建的PVC在挂载时，都会自动应用存储类中的挂载参数。

#### 静态PV使用挂载参数

1. 在PV定义中增加`mountOptions`参数;
2. 将PV Name标记到`volumeHandle`上，格式为`<挂载uri>#<pv-name>`

> 将PV Name标记到`volumeHandle`上, 保证了每个PV的`volumeHandle`都是不同的，从而触发独立的挂载行为。否则，如果您已经在节点上使用同远程路径的静态PV，挂载将不会重新执行，新的挂载参数也不会被应用。如果您的挂载路径本身包含`#`字符，请转义为`\#`后提供。

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: static-upfs-pvc-mountopt-1
spec:
  accessModes:
  - ReadWriteMany
  capacity:
    storage: 256Ti
  csi:
    driver: upfs.csi.ucloud.cn
    volumeHandle: 100.65.128.139:10109,100.65.128.140:10109/upfs-1dcuqwz0e58u/example#static-upfs-pvc-mountopt-1
  mountOptions:
    - forbidden_delete
    - forbidden_overwrite
    - forbidden_rename
    - forbidden_truncate
  storageClassName: ""
  volumeMode: Filesystem
```

## 删除UPFS实例

由于UPFS资源删除需要该UPFS处于未挂载状态，请先删除所有使用到UPFS PVC的Pod后再执行UPFS资源删除操作。

执行以下命令来确认节点上是否还存在特定UPFS实例的挂载点：
```
# mount |grep upfs-xxxx
Filesystem              Size  Used Avail Use% Mounted on
...
UPFS:upfs-xxxx          5.9T  8.5K  5.9T   1% /data/kubelet/plugins/kubernetes.io/csi/upfs.csi.ucloud.cn/uri/101.66.127.139:10109,101.66.127.140:10109/upfs-xxxx
```

## 版本更新记录
| 版本                    | 说明                                                                                                        |
|-------------------------|-----------------------------------------------------------------------------------------------------------|
| upfs-25.12.04-cli-v14.10 | 支持西南二（贵阳）新地域                                                                                              |
| upfs-25.09.08-cli-v14.10 | upfs客户端: 修复目录缓存不一致问题，缓存readlink，减少重复readlink调用                                                            |
| upfs-25.09.08-cli-v14.7 | 支持通过mountOptions提供UPFS挂载参数                                                                                |
| upfs-25.09.01-cli-v14.7 | 支持通过静态PV挂载指定远程UPFS目录                                                                                      |
| upfs-25.07.18-cli-v14.3 | 修复同时创建多个pvc时，在upfs上创建子目录冲突的问题                                                                             |
| upfs-25.06.27-cli-v14.3 | upfs客户端: 修复从小于v12.0版本升级上来时的兼容性问题                                                                          |
| upfs-25.06.27-cli-v14.1 | upfs客户端: 修复后端锁服务异常下调用锁请求导致客户端挂掉的问题                                                                        |
| upfs-25.06.27-cli-v14.0 | 自动安装upfs v14.0客户端;<br>支持挂载UPFS的子目录;<br>支持自动以pvc名称在UPFS上创建子目录实现数据分离；<br>支持单Pod挂载多PVC、多Pod挂载同PVC、多Pod挂载多PVC。 |
