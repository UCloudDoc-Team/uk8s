
## 动态PV 使用UFS

### 一、背景

前面我们描述了通过创建静态PV的方式在UK8S中使用UFS，但这种方式存在两个问题，一是每次都需要手动创建PV和PVC，非常不便；二是无法自动在UFS创建子目录，需要预先配置。

下面我们介绍一个名为nfs-client-provisioner的开源项目，其项目地址为[nfs-client-provisioner](https://github.com/kubernetes-incubator/external-storage/tree/master/nfs-client)，通过此工具，可实现在业务需要UFS存储资源时，只需要创建PVC，nfs-client-provisioner会自动创建PV，并在UFS下创建一个名为{namespace-pvcname}的子目录。


### 二、工作原理

我们需要将创建的UFS系统相关参数通过ENV传入到nfs-client-provisioner，这个nfs-provisioner是通过Deployment控制器来运行一个Pod来实现的，服务启动后，需要再创建一个StorageClass，其provisioner与nfs-provisioner服务内的provisioner-name一致即可。nfs-client-provisioner会watch集群内的PVC对象，并为其提供适配PV的服务，并且会在NFS根目录下创建对应的目录。这些官方文档的描述已经比较详细了，不再赘述，下面说下在UK8S中使用这个组件操作UFS需要做的改动。

### 三、操作指南

1、克隆项目，这里我们只需要关注三个文件，分别是class.yaml,deployment.yaml,rbac.yaml。

```bash
# git clone https://github.com/kubernetes-incubator/external-storage.git
# cd external-storage/nfs-client/deploy/
# ls
class.yaml  deployment-arm.yaml  deployment.yaml  objects  rbac.yaml  test-claim.yaml  test-pod.yaml  
```

2、修改Deployment.yaml

nfs-client-provisioner服务启动时，需要挂载UFS，官网文档是通过spec.volume.nfs来声明的，UFS虽然支持nfs协议，但mount到云主机时，需要指定mountOption，但spec.volume.nfs不支持mountOption参数。因此我们要放弃spec.volume.nfs这种方式，改为静态声明PV的方式来完成首次挂载。具体改动见Yaml说明。

```yaml
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: nfs-client-provisioner
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: nfs-client-provisioner
  template:
    metadata:
      labels:
        app: nfs-client-provisioner
    spec:
      serviceAccountName: nfs-client-provisioner
      containers:
        - name: nfs-client-provisioner
          image: quay.io/external_storage/nfs-client-provisioner:latest
          volumeMounts:
            - name: nfs-client-root
              mountPath: /persistentvolumes
          env:
            - name: PROVISIONER_NAME
              value: fuseim.pri/ifs
            - name: NFS_SERVER  
              value: 10.9.106.78   #这里需要修改为UFS的Server地址
            - name: NFS_PATH
              value: / #这里改成UFS的挂载路径
      volumes:
        - name: nfs-client-root
          persistentVolumeClaim:   #这里由volume改为persistentVolumeClaim
             claimName: nfs-client-root   
---
# 创建PVC
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: nfs-client-root
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 200Gi
---
#手动创建PV，需要指定mountOption。
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-client-root
spec:
  capacity:
    storage: 200Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  nfs:
    path: /  
    server: 10.9.x.x  #这里直接写UFS的Server地址即可。
  mountOptions:
    - nolock   
    - nfsvers=4.0  

```

3、修改class.yaml

class.yaml是第二处要修改的地方，这里主要是新增了mountOption参数，这个值会传递给nfs-client，如果不加的话，挂载UFS的时候会失败。

```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: managed-nfs-storage
provisioner: fuseim.pri/ifs # if choose another name, must match deployment's env PROVISIONER_NAME'
parameters:
  archiveOnDelete: "false"
mountOptions:
  - nolock
  - nfsvers=4.0  

```


4、验证

我们依次执行kubectl apply -f rbac.yaml、deployment.yaml、class.yaml，使用官方的test-pvc和test-pod测试，发现pod已经挂载了UFS，且UFS里面有一个新的目录。
