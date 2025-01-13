# 在UK8S中使用UPFS

本文档介绍如何在UK8S集群中，使用UPFS作为K8S底层的存储支持，UPFS为共享存储，可以同时为多个Pod提供服务。

## UPFS 使用必读

* UPFS产品目前仅支持部分地域

* **UPFS的其他限制条件，请见[UPFS产品使用限制](https://docs.ucloud.cn/upfs/upfs_manual_instruction/limit)**

## 前置条件

- 在[UFS产品页面](https://console.ucloud.cn/upfs/)购买UFS实例并设置好挂载点，操作完毕后，您会得到两个UPFS挂载地址，类似101.66.127.139:10109,101.66.127.140:10109

## 手动部署CSI

> 因目前的UK8S版本均不封装UPFS CSI，需要自行部署

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/upfs.24.08.15/rbac-controller.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/upfs.24.08.15/rbac-node.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/upfs.24.08.15/csi-controller.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/upfs.24.08.15/csi-node.yml
```

## 创建存储类StorageClass

接下来进行创建StorageClass操作

创建StorageClass时需要注意以下两个参数:

* uri：文件系统URL（URL详细规则请见[UPFS主要概念](https://docs.ucloud.cn/upfs/upfs_manual_instruction/concept)中的文件系统URL部分）

* path：表示宿主上挂载upfs的目录结构，可自行命名，默认值为: `/`，一个UPFS实例可以对应多个不同path的StorageClass(同一个UPFS实例即文件系统url，使用相同的path即相同StorageClass的pvc可以实现共享数据，同理，使用不同的path的StorageClass即可实现数据分离)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-upfs
provisioner: upfs.csi.ucloud.cn
parameters:
  uri: 101.66.127.139:10109,101.66.127.140:10109/upfs-xxxx
  path: /example

```

## 创建PVC

yaml示例如下：

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

kubectl创建pvc:

```
# kubectl apply -f upfspvc.yml 
persistentvolumeclaim/logupfs-claim created
```

创建完PVC后，可以发现PV与PVC已经绑定。
* 可以看到此处PVC的容量为最大256T不做限制 **(但实际容量务必以对应UPFS实例的容量为准)**

```
# kubectl get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                   STORAGECLASS   REASON   AGE
pvc-ae961bc8-2c97-414e-9e7b-bde3e28efee9   256Ti      RWX            Delete           Bound    default/logupfs-claim   csi-upfs                12s
# 
# kubectl get pvc
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
logupfs-claim   Bound    pvc-ae961bc8-2c97-414e-9e7b-bde3e28efee9   256Ti      RWX            csi-upfs       12s
```

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

创建完Pod之后，我们可以通过''kubectl exec''命令进入容器，执行df命令查看pod是否挂载到UPFS

```
# df -h
Filesystem              Size  Used Avail Use% Mounted on
...
UPFS:upfs-xxxx          5.9T  8.5K  5.9T   1% /data
...
```

## 删除UPFS实例

由于UPFS资源删除需要该UPFS处于未挂载状态，而目前仅删除所有用到该UPFS实例的POD，并不能使UPFS文件系统从云主机侧卸载。

当您不需要使用到UPFS实例想要删除该UPFS实例时，需要从云主机卸载UPFS文件系统。

**K8s集群上卸载UPFS文件系统属高危操作，请确认该文件系统不再被pod或其他服务使用后再执行**

登录到所有使用过该UPFS的pod所在的node(云主机)上执行命令：

```
## 查看是否有该UPFS的挂载点
# df -h |grep upfs-xxxx
Filesystem              Size  Used Avail Use% Mounted on
...
UPFS:upfs-xxxx          5.9T  8.5K  5.9T   1% /data/kubelet/plugins/kubernetes.io/csi/upfs.csi.ucloud.cn/uri/101.66.127.139:10109,101.66.127.140:10109/upfs-xxxx

## 卸载UPFS操作
# umount /data/kubelet/plugins/kubernetes.io/csi/upfs.csi.ucloud.cn/uri/101.66.127.139:10109,101.66.127.140:10109/upfs-xxxx

```
