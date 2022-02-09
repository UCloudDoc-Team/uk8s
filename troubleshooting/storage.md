# 存储常见问题

## 1. PV PVC StorageClass 以及 UDisk 的各种关系？

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: udisk-ssd-test
provisioner: udisk.csi.ucloud.cn #存储供应方，此处不可更改。
---
apiVersion: v1
kind: PersistentVolumeClaim
spec:
  storageClassName: ssd-csi-udisk
```

用户只需要设置好 StorageClass，在使用 pvc 时，csi-udisk 插件会自动完成 UDisk 的创建挂载 mount 等一系列的操作，主要流程如下

1. StorageClass 设置相关参数，与 CSI 插件绑定。
2. pvc 与 StorageClass 进行绑定。
3. K8S 观察到使用 StorageClass 的新建 pvc，会自动创建 pv，并交给 CSI 插件完成新建 UDisk 的工作。
4. pv 与 pvc 绑定完成，CSI 插件完成后续 UDisk 的挂载和 mount 等工作。
5. UCloud 的 CSI 插件查看可以通过`kubectl get pods -o wide -n kube-system |grep udisk` 查看（一个总的 controller 及每个
   node 对应的 pod）

### 1.1 Statefulset 中使用 PVC

1. Statefulset 控制器中的 pvctemplate 字段，可以设置 K8S 集群在对应 pvc 不存在时自动创建pvc，使得上述流程更加自动化(pvc和pv均由UK8S来建)。
2. Statefulset 只负责创建不负责删除 pvc，因此对应多余的 pvc 需要手动删除

## 2. VolumeAttachment 的作用

VolumeAttachment 并不由用户自己创建，因此很多用户并不清楚它的作用，但是在 pvc 的使用过程中，VolumeAttachment 有着很重要的作用

1. VolumeAttachment所表示的，是 K8S 集群中记载的 pv 和某个 Node
   的挂载关系。可以执行`kubectl get volumeattachment |grep pv-name` 进行查看
2. 这个挂载关系和 UDisk 与云主机的挂载关系往往是一致的，但是有时可能会出现不一致的情况。
3. 不一致的情况多见于 UDisk 已经从云主机卸载，但是 VolumeAttachment 记录中仍然存在，UDisk
   是否挂载在云主机上，可以通过[如何查看 PVC 对应的 UDisk 实际挂载情况](#3-如何查看-pvc-对应的-udisk-实际挂载情况)来查看
4. 对于不一致的情况，可用选择手动删除对应的 VolumeAttachment 字段，并新建一个相同的 VolumeAttachment（新建后 ATTACHED 状态为 false）
5. 如果不能删除，可以通过`kubectl logs csi-udisk-controller-0 -n kube-system csi-udisk` 查看 csi-controller
   日志定位原因
6. 一般 kubelet 手动删除不掉的情况，可能是对应的节点已经不存在了，此时直接  edit volumeattachment 删除 finalizers 字段即可

```sh
[root@10-9-112-196 ~]# kubectl get volumeattachment |grep pvc-e51b694f-ffac-4d23-af5e-304a948a155a
NAME                                                                   ATTACHER              PV                                         NODE           ATTACHED   AGE
csi-1d52d5a7b4c5c172de7cfc17df71c312059cf8a2d7800e05f46e04876a0eb50e   udisk.csi.ucloud.cn   pvc-e51b694f-ffac-4d23-af5e-304a948a155a   10.9.184.108   true       2d2h
```

```yaml
apiVersion: storage.k8s.io/v1
kind: VolumeAttachment
metadata:
  annotations:
    csi.alpha.kubernetes.io/node-id: 10.9.184.108 # 绑定的节点ip，填写报错pod所在节点
  finalizers:
  - external-attacher/udisk-csi-ucloud-cn
  name: csi-1d52d5a7b4c5c172de7cfc17df71c312059cf8a2d7800e05f46e04876a0eb50e # 名称，按照pod报错名称填写
spec:
  attacher: udisk.csi.ucloud.cn
  nodeName: 10.9.184.108 #绑定的节点ip，填写报错pod所在节点
  source:
    persistentVolumeName: pvc-e51b694f-ffac-4d23-af5e-304a948a155a # 绑定的pv，填写pod使用的pv
```

## 3. 如何查看 PVC 对应的 UDisk 实际挂载情况

对应关系表

| UK8S资源类型         | 与主机对应关系                   |
| ---------------- | ------------------------- |
| PV               | UDisk 的磁盘                 |
| VolumeAttachment |  磁盘与主机的挂载关系(vdb,vdc 的块设备) |
| PVC              |  磁盘在主机上mount的位置           |
| pod              |  使用磁盘的进程                  |

1. `kubectl get pvc -n ns pvc-name` 查看对应的 VOLUME 字段，找到与 pvc 绑定的
   pv，一般为（pvc-e51b694f-ffac-4d23-af5e-304a948a155a）
2. `kubectl get pv pv-name -o yaml` 在 spec.csi.volumeHandle 字段，可以查看到改 pv 绑定的 UDisk盘(flexv 插件为 pv
   的最后几位)
3. 在控制台查看该udisk盘的状态,是否挂载到某个主机
4. `kubectl get volumeattachment |grep pv-name` 查看 K8S 集群内记录的磁盘挂载状态
5. ssh 到对应的主机上，`lsblk`可以看到对应的盘
6. `mount |grep pv-name` 可用查看盘的实际挂载点，有一个 globalmount 及一个或多个 pod 的 mount 点

```sh
[root@10-9-184-108 ~]# mount |grep pvc-e51b694f-ffac-4d23-af5e-304a948a155a
/dev/vdc on /data/kubelet/plugins/kubernetes.io/csi/pv/pvc-e51b694f-ffac-4d23-af5e-304a948a155a/globalmount type ext4 (rw,relatime)
/dev/vdc on /data/kubelet/pods/587962f5-3009-4c53-a56e-a78f6636ce86/volumes/kubernetes.io~csi/pvc-e51b694f-ffac-4d23-af5e-304a948a155a/mount type ext4 (rw,relatime)
```

## 4. 磁盘挂载的错误处理

1. 由于磁盘内容多流程长，建议在出现问题时，首先确定当前状态[如何查看 PVC 对应的 UDisk 实际挂载情况](#3-如何查看-pvc-对应的-udisk-实际挂载情况)
2. 如果有UK8S中状态和主机状态不一致的情况，首先进行清理，删除掉不一致的资源，之后走正常流程进行恢复 

### 4.1 PV 和 PVC 一直卡在 terminating/磁盘卸载失败怎么办

1. 通过[如何查看 PVC 对应的 UDisk 实际挂载情况](#3-如何查看-pvc-对应的-udisk-实际挂载情况)确定当前 pv 和 pvc 的实际挂载状态
2. 手动按照自己的需求进行处理，首先清理所有使用该 pv 和 pvc 的所有 pod（如果 pvc 已经成功删除，则不需要这一步）
3. 如果删除 pvc 卡在 terminating，则手动 umount 掉对应的挂载路径
4. 如果删除 VolumeAttachment 卡在 terminating，则手动在控制台卸载掉磁盘（如果卡在卸载中找主机处理）
5. 如果删除 pv 卡在 terminating，则手动在控制台删除掉磁盘（删除 pv 前需要确保相关的 VolumeAttachment 已经删除完成）
6. 确保手动释放完成对应的资源后，可以通过`kubectl edit` 对应的资源,删除掉其中的 finalizers 字段，此时资源就会成功释放掉
7. 删除 VolumeAttachment 后，如果 pod
   挂载报错，按照[VolumeAttachment 的作用](#2-volumeattachment-的作用)中提供的yaml文件，重新补一个同名的 VolumeAttachment 即可

### 4.2 Pod 的 PVC 一直挂载不上怎么办？

1. `kubectl get pvc -n ns pvc-name` 查看对应的 VOLUME 字段，找到与 pvc 绑定的
   pv，一般为（pvc-e51b694f-ffac-4d23-af5e-304a948a155a）
2. `kubectl get pv pv-name -o yaml` 在 spec.csi.volumeHandle 字段，可以查看到改 pv 绑定的 UDisk 盘(flexv 插件为 pv
   的最后几位)
3. 找到 UDisk 磁盘后，如果控制台页面中磁盘处于可用状态或者挂载的主机不是 pod 所在主机，可以找技术支持，查看该 UDisk的挂载和卸载请求的错误日志，并联系主机同时进行处理
4. 如果没有
   UDisk相关的错误日志，联系UK8S值班人员，并提供`kubectl logs csi-udisk-controller-0 -n kube-system csi-udisk`的日志输出及
   pod 的event

## 5. UDisk-PVC 使用注意事项

1. 由于 UDisk 不可跨可用区，因此在建立 StorageClass 时必须指定 volumeBindingMode: WaitForFirstConsumer
2. 由于 UDisk 不可多点挂载，因此必须在 pvc 中指定 accessModes 为 ReadWriteOnce
3. 基于 UDisk 不可多点挂载，多个 pod 不可共用同一个 udisk-pvc，上一个 pod 的 udisk-pvc 未处理干净时，会导致后续 pod 无法创建，此时可以查看
   VolumeAttachment 的状态进行确认

## 6. K8S 1.17 版本升级到 1.18 过程中云盘 Detach 问题

我们发现在 UK8S 集群从 1.17 升级至 1.18 的过程中，部分挂载 PVC 的 Pod 会出现 IO 错误。查相关日志发现是因为挂载的盘被卸载导致 IO 异常。

社区在 1.18 版本为了解决 Dangling Attachments 引入该问题。参见
[Recover CSI volumes from dangling attachments](https://github.com/kubernetes/kubernetes/commit/4cd106a920cde9c2929d9d0e20e2e96b875b8e2d)

K8S 处理挂盘和卸盘的实现中，单个 Node 可以选择由 kubelet 和 controller-manager 进行管理挂盘和卸盘，上面的代码在解决 dangling attachments
问题时引入了一个新的问题，由 kubelet 管理挂盘的 Node 节点，在 controller-manager 重启后，该节点的磁盘会被强制卸载掉。

为了解决该问题，需要将由 kubelet 负责挂盘的节点改为由 controller-manager 负责挂盘。UK8S 添加的节点已经默认使用 controller-manager
负责挂盘，后续添加节点无需再手动更改

### 6.1 规避方法

#### 检查 Kubelet 配置

**在升级前**，检查所有节点的 `/etc/kubernetes/kubelet.conf` 的配置。如果 `enableControllerAttachDetach` 的值为 `false`
则需要把该值修改为 `true`。

然后执行命令 `systemctl restart kubelet` 重启 Kubelet。

#### 检查 Node 状态

执行命令 `kubectl get no $IP -o yaml` 查看 Node 的 `status` 中 `volumesAttached` 是否有数据，且数据是否与 `volumesInUse`
的数据一致。

Node `annotations` 中应该有 `volumes.kubernetes.io/controller-managed-attach-detach: "true"` 的记录。

如确认上述数据一致，且 Annotations 中有相应记录，则可以正常进行升级。如有问题，请联系技术支持。

## 7. Flexv 插件导致 pod 删除失败

### 7.1 现象描述

使用flexv插件自动创建pv绑定到pod，删除pod时，有可能导致pod 处于Terminating状态，不能正常删除。

- kubernetes版本: 1.13
- 插件版本：Flexvolume-19.06.1

### 7.2 问题原因

kubelet重启后找不到volume对应的Flexvolume插件。kubelet在重启之后如果发现了orphan
pod（正常的pod不会导致这个问题），就会通过pod记录volume的路径来推断出使用的插件，但是flexv会在插件前面加入flexvolume-字段，导致kubelet推断出的名字和flexv提供的名字匹配不上。kubelet日志中会报**no
volume plugin matched** 的错误，进而导致pod卡在Terminating的状态。

具体可以查看下面issue

- https://github.com/kubernetes/kubernetes/issues/80972
- https://github.com/kubernetes/kubernetes/pull/80973

### 7.3 解决方案

手动umount掉当前pod使用的路径，并进行清理操作。

> 谨慎操作，本操作是代替kubelet手动进行资源清理，请阅读结束下面所有步骤再进行操作.

1. 找到不能正常umount的pv。
2. 登录到node节点上查看mount记录。

```
mount | grep pv-name
```

3. 记录上一步匹配到的所有路径**path**,手动umount掉pv在当前节点下的路径。

```
umount path
```

4. 在上一步umount中，会有一个以/var/lib/kubelet/pods开头的目录，umount之后需要手动删除该目录。

5. 删除pvc，删除pvc之后需要手动在控制台卸载掉对应的udisk。udisk的id为pv名字的最后几位，例如pv名字是pvc-58f9978e-3133-11ea-b4d6-5254000cee42-bsm-olx0uqti，
   则对应的udisk名字就是bsm-olx0uqti。也可以通过describe pv拿到spec.flexVolume.options中的diskId字段。

## 8. 其他常见存储问题汇总

### 8.1 一个PVC可以挂载到多个 pod 吗？

UDisk不支持多点读写，如需要多点读写请使用UFS。

### 8.2 Pod删除后，如何复用原先的云盘？

可以使用静态创建PV的方法进行原有云盘绑定的方法进行复用原有云盘，详见[在UK8S中使用已有UDISK](/uk8s/volume/udisk#22-使用已有-UDisk)

## 9. 挂载Udisk的Pod调度问题

相较于普通Pod，使用Udisk的Pod调度涉及到了UDisk自身挂载规则的限制，更为复杂。具体限制如下

- 普通云盘和SSD云盘挂载要求必须与云主机处于相同可用区
- RSSD云盘挂载要求与云主机处于相同RDMA区域（RDMA区域范围小于可用区）
- RSSD云盘仅可以挂载到快杰云主机

> ⚠️ **RSSD UDisk调度要求同一个RDMA区域，RDMA区域范围小于可用区，而主机目前不支持指定RDMA区域创建机器。因此使用RSSD UDisk，在Pod漂移的情况下，有可能出现Pod无法调度的问题。请您使用前务必确认可以接受该风险。**

UDisk挂载限制在实际UK8S的使用中主要体现到以下两个方面
- 自动创建PV的过程中，如何判定创建哪个可用区/RDMA区域的云盘
- 当Pod需要重新调度时，如何保证新调度的节点满足云盘挂载的要求

UK8S提供的csi-udisk插件，依赖K8S提供的CSI插件能力，帮助用户实现了尽可能少的介入，下面以SSD UDisk为例进行讲解。
### 9.1 创建PVC时自动创建UDisk
从上面的文档中可以了解到，当PVC创建完成时，CSI会自动创建PV以及UDisk，并完成绑定工作。但是创建哪个可用区的UDisk呢，如果随意选择，则会导致后续Pod调度完成后无法挂载云盘。

为此K8S提供了`WaitForFirstConsumer`机制。当`StorageClass`中指定了`volumeBindingMode: WaitForFirstConsumer`参数时，CSI不会立刻创建PV及云盘，以下为`WaitForFirstConsumer`模式下的工作流程。

- 手动创建PVC
- 创建Pod，并且在Pod绑定上一步中定义的PVC
- 等待Pod进行调度完成
- CSI查询Pod所在云主机的可用区，创建相同可用区的云盘，并创建相应PV进行绑定
- CSI更新PV中的`spec.csi.volumeHandle`字段，记录创建的云盘ID
- CSI更新PV中的`spec.nodeAffinity`字段，记录云盘所在的可用区等信息

按照以上逻辑，可以保证Pod调度后创建的云盘顺利挂载到对应主机

### 9.2 Pod重建后调度流程
首次运行后，如果遇到服务更新，或者节点故障等原因触发Pod重建，会进行重新调度，以下为调度流程

- 清理旧Pod，完成UDisk从旧节点上清理卸载工作
- 创建新Pod
- K8S调度器会按照PV中的`spec.nodeAffinity`字段，校验节点是否可以调度
- 如果所有节点都不满足磁盘调度要求，会记录`had volume node affinity conflict`类型的EVENT到Pod，并重复上一步流程
- K8S调度器按照上一步过滤的结果，在可调度的节点范围内，继续按照普通Pod调度流程进行调度

## CSI组件工作原理
CSI是K8S定义的[标准存储接口](https://kubernetes.io/zh/docs/concepts/storage/volumes/#csi)，可以对接云厂商的多种存储。 
UCloud目前实现了UDisk以及UFile/US3的CSI插件。CSI组件分为两大类，分别为Controller以及Daemonset。

目前所有csi组件的pod均默认运行在`kube-system`下面，可以通过执行`kubectl get pods -n kube-system -o wide |grep csi` 进行查看。如果遇到存储挂载问题，可以优先查看CSI controller是否工作正常，以及节点上是否存在对应CSI的Daemonset类型的Pod。

接下来对CSI组件进行简要介绍。

### CSI controller
CSI controller 负责的是全局资源的管理，通过list/watch k8s资源信息，执行对应的操作。    
其中UDisk CSI controller 会负责磁盘创建和删除，磁盘到云主机的卸载及挂载操作。而US3 CSI controller 由于无需处理挂载操作，仅仅负责校验一些StorageClass中的基础信息。    
### CSI Daemonset
CSI Daemonset组件调度到各个节点上，负责单个节点的一些工作。与Controller模式不同，CSI Daemonset通过unix socket地址与kubelet进行通信，接收kubelet请求信息执行对应的操作。
通常CSI unix socket地址为`/var/lib/kubelet/plugins/csi-name/csi.sock`   
UDisk/US3 CSI Daemonset 主要负责存储的Mount以及Umount操作   

### 其它功能
在基础的存储管理以及挂载功能外，CSI还提供了多种其它能力。目前CSI UDisk 则实现了磁盘动态扩容（需要Controller与Daemonset）以及磁盘Metrics信息收集(需要CSI Daemonset)。
