## 存储插件问题

### Flexv插件导致pod删除失败

#### 现象描述

使用flexv插件自动创建pv绑定到pod，删除pod时，有可能导致pod 处于Terminating状态，不能正常删除。
* kubernetes版本: 1.13
* 插件版本：Flexvolume-19.06.1

#### 问题原因

kubelet重启后找不到volume对应的Flexvolume插件。kubelet在重启之后如果发现了orphan pod（正常的pod不会导致这个问题），就会通过pod记录volume的路径来推断出使用的插件，但是flexv会在插件前面加入flexvolume-字段，导致kubelet推断出的名字和flexv提供的名字匹配不上。kubelet日志中会报**no volume plugin matched** 的错误，进而导致pod卡在Terminating的状态。


具体可以查看下面issue
* https://github.com/kubernetes/kubernetes/issues/80972
* https://github.com/kubernetes/kubernetes/pull/80973

#### 解决方案

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
