# 动态PV 使用UFS

## 背景

前面我们描述了通过创建静态 PV 的方式在 UK8S 中使用 UFS，但这种方式存在两个问题：一是每次都需要手动创建 PV 和 PVC，非常不便；二是无法自动在 UFS 创建子目录，需要预先配置。   

下面介绍一个名为`nfs-subdir-external-provisioner`的开源项目，项目地址为 [nfs-subdir-external-provisioner](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner)。此项目可以为我们提供一个基于 UFS 的`StorageClass`：在业务需要 UFS 存储资源时，只需要创建 PVC，`nfs-client-provisioner`就会自动创建 PV，并在 UFS 下创建一个名为`${namespace}-${pvcName}-${pvName}`的子目录。

## 工作原理

我们将 nfs 相关参数通过环境变量传入到`nfs-client-provisioner`，这个 provisioner 通过 Deployment 控制器运行一个 Pod 来管理 nfs 的存储空间。服务启动后，我们再创建一个`StorageClass`，其 provisioner 与`nfs-client-provisioner`服务内的`provisioner-name`一致。`nfs-client-provisioner`会 watch 集群内的 PVC 对象，为其提供适配 PV 的服务，并且会在 nfs 根目录下创建对应的目录。 这些官方文档的描述已经比较详细了，不再赘述。  
   
以下说明如何在 UK8S 中使用这个服务来管理 UFS。

## 操作指南

1、克隆项目   

克隆项目[nfs-subdir-external-provisioner](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner), 在`deploy/`目录下，我们需要关注三个文件，分别是`rbac.yaml`, `deployment.yaml`, `class.yaml`。

```bash
# git clone https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner.git
# cd nfs-subdir-external-provisioner/deploy/
# ls
class.yaml         kustomization.yaml rbac.yaml          test-claim.yaml
deployment.yaml    objects            test-pod.yaml
```

2、修改`nfs-client-provisioner`服务的 namespace

我们将把`nfs-client-provisioner`服务和 RBAC 需要的资源都部署在系统插件所在的`kube-system`namespace。

```bash
sed -i "s/namespace:.*/namespace: kube-system/g" ./rbac.yaml ./deployment.yaml
```

3、修改`deployment.yaml`

`nfs-client-provisioner`服务启动时，需要挂载 UFS，官网文档是通过`spec.volume.nfs`来声明的，我们这里改为静态声明 PV 的方式。具体原因说明如下:

UFS 文件系统在 mount 到云主机时需要指定额外的`mountOption`参数，但`spec.volume.nfs`不支持这个参数。而`PersistentVolume`的声明中可以支持这个参数，因此我们通过挂载静态 PV 的方式来完成首次挂载。

`deployment.yaml`文件改动处较多，建议直接替换即可。注意将环境变量`NFS_SERVER`和`NFS_PATH`,以及`path`和`server`分别修改为UFS的Server地址和挂载路径。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nfs-client-provisioner
  labels:
    app: nfs-client-provisioner
  namespace: kube-system
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
          # 使用uhub提供的镜像以获取更快的拉取速度
          image: uhub.service.ucloud.cn/uk8s/nfs-subdir-external-provisioner:v4.0.2
          volumeMounts:
            - name: nfs-client-root
              mountPath: /persistentvolumes
          env:
            - name: PROVISIONER_NAME
              value: ucloud/ufs   # 修改为ucloud/ufs
            - name: NFS_SERVER
              value: 10.9.x.x     ## 这里需要修改为UFS的Server地址
            - name: NFS_PATH
              value: /            ## 这里改成UFS的挂载路径
      volumes:
        - name: nfs-client-root
          persistentVolumeClaim:  #这里由 nfs 改为 persistentVolumeClaim
             claimName: nfs-client-root
---
# 创建 PVC
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: nfs-client-root
  namespace: kube-system
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 200Gi
---
#手动创建 PV 并指定 mountOption
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
    path: / ## 和上面nfs-client-provisioner的NFS_PATH变量保持一致
    server: 10.9.x.x ## 这里直接写UFS的Server地址即可。和上面nfs-client-provisioner的NFS_SERVER变量保持一致
  mountOptions:
    - nolock
    - nfsvers=4.0
```

4、修改`class.yaml`

最后需要修改的是`StorageClass`的定义文件 `class.yaml`。   
主要是新增了`mountOption`参数，这个值会传递给`nfs-client-provisioner`; 如果不加的话，挂载UFS的时候会失败。


```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-client
provisioner: ucloud/ufs
parameters:
  onDelete: "retain" # 配置 PV 的回收策略，详情见下文
mountOptions: # 新增mountOption参数
  - nolock
  - nfsvers=4.0
```

此外您可以在`parameters`中指定 PV 的回收策略: 删除、保留或者归档。上面示例中配置了删除 PV 后保留对应的目录。

| 参数              | 选项及作用                                                   | 默认选项 |
| ----------------- | ------------------------------------------------------------ | -------- |
| `onDelete`        | `"delete"`: 删除目录<br> `"retain"`: 保留目录<br> `""` (空值): 取决于`archiveOnDelete`参数 | 空值     |
| `archiveOnDelete` | `"true"`: 归档, 目录会被重命名为`archived-<volume.Name>`<br> `"false"`: 删除目录 | `"true"` |


5、执行部署

依次执行

```bash
# kubectl create -f rbac.yaml
# kubectl create -f deployment.yaml
# kubectl create -f class.yaml
```

6、验证

创建`test-nfs-sc.yaml`

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test-claim
spec:
  storageClassName: nfs-client
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Mi
---
kind: Pod
apiVersion: v1
metadata:
  name: test-pod
spec:
  containers:
  - name: test-pod
    image: uhub.service.ucloud.cn/uk8s/busybox:1.31.1
    command:
      - "/bin/sh"
    args:
      - "-c"
      - "echo 1 > /mnt/SUCCESS; sleep 10000000"
    volumeMounts:
      - name: nfs-pvc
        mountPath: "/mnt"
  restartPolicy: "Never"
  volumes:
    - name: nfs-pvc
      persistentVolumeClaim:
        claimName: test-claim
```

创建测试 pod 并验证挂载的 UFS 可读写:

```bash
# kubectl create -f test-nfs-sc.yaml
# kubectl exec test-pod -- /bin/sh -c 'ls /mnt/ && cat /mnt/*'
SUCCESS
1
# kubectl delete -f test-nfs-sc.yaml
```
