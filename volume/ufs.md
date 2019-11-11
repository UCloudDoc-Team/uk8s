
## 在UK8S中使用UFS


本文档介绍如何在UK8S集群中，使用UFS作为K8S底层的存储支持，UFS为共享存储，可以同时为多个Pod提供服务。

### 一、前置条件

* 在[UFS产品页面](https://console.ucloud.cn/ufs/ufs)购买UFS实例并设置好挂载点，操作完毕后，您会得到UFS挂载地址和目录，类似10.19.255.192:/ufs-w4wmpkev。

* 集群节点安装nfs-utils，使用''yum install -y nfs-utils''命令，2019年5月1日以后的UK8S节点已默认安装nfs-utils。

* UFS与UK8S集群必须处于同一VPC，否则网络无法互通。



### 二、创建PV


需要在集群内手动创建持久化存储卷，yaml示例如下两种：

**UFS 容量型**

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ufspv3
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  nfs:
    path: /ufs-hoj1utv1
    server: 10.19.255.192
  mountOptions:
    - nolock
    - nfsvers=3
```

**UFS SSD性能型**

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ufspv4.0
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  nfs:
    path: /
    server: 10.9.136.151
  mountOptions:
    - nolock
    - nfsvers=4.0
```

yaml关键字段：

spec.nfs    

spec.nfs.path  此处填写UFS挂载点的路径，通过NFS来创建PV，不支持自动创建子目录，你可以预先创建好一个子目录。

spec.nfs.server 此处填写UFS挂载地址


创建pv:

```
# kubectl  apply -f ufspv.yml 
persistentvolume/ufspv created

```

### 三、创建PVC

yaml示例如下：

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ufsclaim
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 8Gi
```

创建完PVC后，可以发现PV与PVC已经绑定。

```
# kubectl  get pv ufspv
NAME   CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM              STORAGECLASS   REASON   AGE
ufspv   8Gi        RWX            Retain           Bound    default/ufsclaim 
```

### 四、在Pod中挂载UFS

```
apiVersion: v1
kind: Pod
metadata:
     name: myufspod
spec:
     containers:
       - name: myfrontend
         image: uhub.service.ucloud.cn/wxyz/uk8s-helloworld:1.8
         volumeMounts:
         - mountPath: "/var/www/html"
           name: mypd
     volumes:
       - name: mypd
         persistentVolumeClaim:
           claimName: ufsclaim

```

创建完Pod之后，我们可以通过''kubectl exec''命令进入容器，执行df命令查看pod是否挂载到UFS

```
# df -h
Filesystem                   Size  Used Avail Use% Mounted on
...
10.19.255.192:/ufs-w4wmpkev  1.0T     0  1.0T   0% /var/lib/kubelet/pods/c800f8a7-5c38-11e9-8aae-525400fa7819/volumes/kubernetes.io~nfs/ufs
...

```
