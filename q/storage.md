# 存储插件相关问题

## 1. K8S 1.17 版本升级到 1.18 过程中云盘 Detach 问题

我们发现在 UK8S 集群从 1.17 升级至 1.18 的过程中，部分挂载 PVC 的 Pod 会出现 IO 错误。查相关日志发现是因为挂载的盘被卸载导致 IO 异常。

社区在 1.18 版本为了解决 Dangling Attachments 引入该问题。参见 [Recover CSI volumes from dangling attachments](https://github.com/kubernetes/kubernetes/commit/4cd106a920cde9c2929d9d0e20e2e96b875b8e2d)

K8S 处理挂盘和卸盘的实现中，单个 Node 可以选择由 kubelet 和 controller-manager 进行管理挂盘和卸盘，上面的代码在解决 dangling attachments 问题时引入了一个新的问题，由 kubelet 管理挂盘的 Node 节点，在 controller-manager 重启后，该节点的磁盘会被强制卸载掉。

为了解决该问题，需要将由 kubelet 负责挂盘的节点改为由 controller-manager 负责挂盘。UK8S 添加的节点已经默认使用 controller-manager 负责挂盘，后续添加节点无需再手动更改

### 规避方法

#### 检查 Kubelet 配置

**在升级前**，检查所有节点的 `/etc/kubernetes/kubelet.conf` 的配置。如果 `enableControllerAttachDetach` 的值为 `false` 则需要把该值修改为 `true`。

然后执行命令 `systemctl restart kubelet` 重启 Kubelet。

#### 检查 Node 状态

执行命令 `kubectl get no $IP -o yaml` 查看 Node 的 `status` 中 `volumesAttached` 是否有数据，且数据是否与 `volumesInUse` 的数据一致。

Node `annotations` 中应该有 `volumes.kubernetes.io/controller-managed-attach-detach: "true"` 的记录。

如确认上述数据一致，且 Annotations 中有相应记录，则可以正常进行升级。如有问题，请联系技术支持。


## 2. Flexv 插件导致 pod 删除失败

### 现象描述

使用flexv插件自动创建pv绑定到pod，删除pod时，有可能导致pod 处于Terminating状态，不能正常删除。
* kubernetes版本: 1.13
* 插件版本：Flexvolume-19.06.1

### 问题原因

kubelet重启后找不到volume对应的Flexvolume插件。kubelet在重启之后如果发现了orphan pod（正常的pod不会导致这个问题），就会通过pod记录volume的路径来推断出使用的插件，但是flexv会在插件前面加入flexvolume-字段，导致kubelet推断出的名字和flexv提供的名字匹配不上。kubelet日志中会报**no volume plugin matched** 的错误，进而导致pod卡在Terminating的状态。


具体可以查看下面issue
* https://github.com/kubernetes/kubernetes/issues/80972
* https://github.com/kubernetes/kubernetes/pull/80973

### 解决方案

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

5. 删除pvc，删除pvc之后需要手动在控制台卸载掉对应的udisk。udisk的id为pv名字的最后几位，例如pv名字是pvc-58f9978e-3133-11ea-b4d6-5254000cee42-bsm-olx0uqti， 则对应的udisk名字就是bsm-olx0uqti。也可以通过describe pv拿到spec.flexVolume.options中的diskId字段。
