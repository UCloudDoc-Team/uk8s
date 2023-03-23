# Volume 介绍

## 概念

我们知道，容器中的磁盘文件是临时的，一旦容器运行结束，其文件也会丢失。如果数据需要长期存储，那就需要对容器数据做持久化支持，在就涉及到Kubernetes中的一个核心概念 Volume。
Kubernetes 和 Docker 类似，也是通过 Volume 的方式提供对存储的支持。Kubernetes 中 的Volume 与Docker 中的 Volume 类似，主要的区别如下：

1. Kubernetes中的Volume被定义到Pod层面，Volume可以被 Pod 中的多个容器挂载到相同或不同的路径。

1. Kubernetes 中的 Volume 与 Pod 的生命周期相同，但与容器的生命周期不相关。当容器终止或重启时，Volume 中的数据不会丢失。

1. 当 Pod 被删除时，Volume 才会被清理。并且数据是否丢失取决于 Volume 的具体类型，比如：emptyDir 类型的 Volume 数据会丢失，而 PV 类型的数据则不会丢失。

Volume的本质是一个目录，其中可以包含数据，Pod中的容器可以访问该目录。该目录的形式，支持该目录的介质以及目录的内容取决于所使用的特定卷类型。 Kubernetes 目前支持多种 Volume
类型，常用的类型如下：

- cephfs

- glusterfs

- nfs

- csi

- FlexVolume

- emptyDir

- hostPath

- local

- persistentVolumeClaim

- secret
- configMap

这里只提到了一些常用的Volume类型，更多详见官网文档[Volume](https://kubernetes.io/docs/concepts/storage/volumes/)。

## 常见Volume类型

### emptyDir

emptyDir与Pod的生命周期完全一致，它 在 Pod 分配到 Node 上时被创建，Kubernetes 会在 Node 上自动分配一个目录，因此无需指定 Node
宿主机上对应的目录文件。这个目录的初始内容为空，当 Pod 从 Node 上移除（Pod 被删除或者 Pod 发生迁移）时，emptyDir 中的数据会被永久删除。emptyDir Volume
主要用于某些应用程序无需永久保存的临时目录，或者在Pod中的多个容器之间共享数据等。emptryDir 默认使用主机磁盘进行存储的，也可以使用其它介质作为存储，比如：网络存储、内存等，设置
emptyDir.medium 字段的值为 Memory 就可以使用内存进行存储。

### hostPath

hostPath 类型的 Volume 允许挂载 Node 节点上的文件或目录到 Pod 中，不过hostPath类型的Volume很少被使用，因为每个Node节点上的文件可能不同，最终导致一组
Pod （如Deployment）在不同Node节点上的行为可能会有所不同，且Pod一旦被调度其他Node节点会导致数据错乱。另外要在Node节点上创建的文件或目录写入内容，需要在容器中以 root
身份运行进程，存在一定的安全隐患。

### Secret

Secret对象用于存储和管理敏感信息，例如密码，OAuth令牌和ssh密钥。将此类信息放入一个secret中可以更好地控制它的用途，并降低意外暴露的风险。
比如我们可以将Docker鉴权的信息放入到Secret，再挂载到的Pod中，用于拉取镜像时做权限认证，示例如下： 1、创建Secret

```
# MYSECRET为secret 名称，请自行指定
kubectl create secret docker-registry MYSECRET \
--docker-server=uhub.service.ucloud.cn \
--docker-username=YOUR_UCLOUD_USERNAME@EMAIL.COM \
--docker-password=YOUR_UHUB_PASSWORD
```

2、Pod挂载Secret

```
apiVersion: v1
kind: Pod
metadata:
  name: secret-test
spec:
  containers:
  - name: secret-test
    image: centos
    command:
      - sleep
      - "3600"
    volumeMounts:
    - name: config
      mountPath: /root/.docker/
  volumes:
  - name: config
    secret:
      secretName: MYSECRET 
      items:
      - key: .dockerconfigjson
        path: config.json
        mode: 0644
```

3、查看挂载效果

```
$ kubectl exec secret-test -- cat /root/.docker/config.json
{"auths":{"uhub.service.ucloud.cn":{"username":"YOUR_UCLOUD_USERNAME@EMAIL.COM","password":"YOUR_UHUB_PASSWORD","auth":"dXNlcm5hbWU6cGFzc3dvcmQ="}}}
```

## PV&PVC&StorageClass

Kubernetes 目前主要使用 PersistentVolume、PersistentVolumeClaim、StorageClass 三个 API
对象来进行持久化存储，下面分别介绍下这三个API对象。

### PV

PV 的全称是PersistentVolume（持久化卷）。PersistentVolume 是 Volume 的一种类型，是对底层存储的一种抽象。PV
由集群管理员进行创建和配置，与Node一样，PV 也是属于集群级别的资源。PV 包含存储类型、存储大小和访问模式。PV 的生命周期独立于 Pod，即使用它的Pod被 销毁时，PV 可以依然存在。

PersistentVolume 通过插件机制实现与共享存储的对接。Kubernetes
目前支持以下插件类型，其中FlexVolume和CSI是Kubernetes的标准插件，用于集成各云厂商的存储设备，UK8S便是基于CSI和flexVolume来集成UDisk、UFS、UFile等UCloud存储介质。

- FlexVolume

- CSI

- NFS

- RBD (Ceph Block Device)

- CephFS

- Glusterfs

- HostPath

- Local

### PVC

PVC 的全称是PersistentVolumeClaim（持久化卷声明），PVC 是用户对存储资源的一种请求。PVC 和 Pod 比较类似，Pod 消耗的是节点资源，PVC 消耗的是 PV
资源。Pod 可以请求 CPU 和内存，而 PVC 可以请求特定的存储空间和访问模式。对于真正使用存储的用户不需要关心底层的存储实现细节，只需要直接使用 PVC 即可。

### StorageClass

由于不同的应用程序对于存储性能的要求也不尽相同，比如：读写速度、并发性能、存储大小等。如果只能通过 PVC 对 PV
进行静态申请，显然这并不能满足任何应用对于存储的各种需求。为了解决这一问题，Kubernetes 引入了一个新的资源对象：StorageClass，通过 StorageClass
的定义，集群管理员可以先将存储资源定义为不同类型的资源，比如快速存储、慢速存储、共享存储（多读多写）、块存储（单读单写）等。

当用户通过 PVC 对存储资源进行申请时，StorageClass 会使用 Provisioner（不同存储资源对应不同的 Provisioner）来自动创建用户所需
PV。这样应用就可以随时申请到合适的存储资源，而不用担心集群管理员没有事先分配好需要的 PV。

## UK8S支持存储挂载的地域

|  国内   | 北京  | 上海  | 广州  | 香港  | 台北  |
| :---: | :-: | :-: | :-: | :-: | :-: |
| UDisk | 支持  | 支持  | 支持  | 支持  | 支持  |
|  UFS  | 支持  | 支持  | 支持  | 支持  | --  |
| UFile | 支持  | 支持  | 支持  | 支持  | 支持  |

|  亚太   | 东京  | 首尔  | 曼谷  | 新加坡 | 雅加达 | 胡志明市 |
| :---: | :-: | :-: | :-: | :-: | :-: | :--: |
| UDisk | 支持  | 支持  | 支持  | 支持  | 支持  |  支持  |
|  UFS  | --  | --  | --  | --  | --  |  --  |
| UFile | 支持  | 支持  | 支持  | 支持  | 支持  |  支持  |

| 北美与欧洲 | 洛杉矶 | 华盛顿 | 法兰克福 | 伦敦  |
| :---: | :-: | :-: | :--: | :-: |
| UDisk | 支持  | 支持  |  支持  | 支持  |
|  UFS  | --  | --  |  --  | --  |
| UFile | 支持  | 支持  |  支持  | --  |

|  其他   | 孟买  | 迪拜  | 圣保罗 | 拉各斯 |
| :---: | :-: | :-: | :-: | :-: |
| UDisk | 支持  | --  | --  | 支持  |
|  UFS  | --  | --  | --  | --  |
| UFile | 支持  | 支持  | --  | 支持  |

