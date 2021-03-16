* [UK8S人工支持](#uk8s人工支持)
* [为什么我的容器一起来就退出了？](#为什么我的容器一起来就退出了)
* [docker如何调整日志等级](#docker如何调整日志等级)
* [为什么节点已经异常了，但是pod还处在running状态](#为什么节点已经异常了但是pod还处在running状态)
* [节点宕机了，pod一直卡在termnating怎么办](#节点宕机了pod一直卡在termnating怎么办)
* [Pod异常退出了怎么办？](#pod异常退出了怎么办)
* [CNI插件升级为什么失败了？](#cni插件升级为什么失败了)
* [UK8S页面概览页一直刷新不出来？](#uk8s页面概览页一直刷新不出来)
* [UK8S节点NotReady了怎么办](#uk8s节点notready了怎么办)
* [为什么我的集群连不上外网?](#为什么我的集群连不上外网)
* [为什么我的UHub登陆失败了?](#为什么我的uhub登陆失败了)
* [UHub下载失败（慢）](#uhub下载失败慢)
* [pv, pvc, sc 以及udisk的各种关系？](#pv-pvc-sc-以及udisk的各种关系)
  - [Statefulset中使用pvc](#statefulset中使用pvc)
* [volumeattachment的作用](#volumeattachment的作用)
* [如何查看pvc对应的udisk实际挂载情况](#如何查看pvc对应的udisk实际挂载情况)
* [磁盘挂载的错误处理](#磁盘挂载的错误处理)
  -  [pv和pvc一直卡在terminating/磁盘卸载失败怎么办](#pv和pvc一直卡在terminating磁盘卸载失败怎么办)
  - [pod的pvc一直挂载不上怎么办？](#pod的pvc一直挂载不上怎么办)
* [udisk-pvc使用注意事项](#udisk-pvc使用注意事项)
* [为什么在k8s节点docker直接起容器网络不通](#为什么在k8s节点docker直接起容器网络不通)
* [使用ulb4时vserver为什么会有健康检查失效](#使用ulb4时vserver为什么会有健康检查失效)
* [ulb4对应的端口为什么不是nodePort的端口](#ulb4对应的端口为什么不是nodeport的端口)



## UK8S人工支持
对于使用 UK8S 遇到的本文档未涉及的问题，如果需要人工支持，请添加下面公钥信任，并提供主机的 uhost-id
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDGIFVUtrp+jAnIu1fBvyLx/4L4GNsX+6v8RodxM+t3G7gCgaG+kHqs1xkLBWQNNMVQz2c/vA1gMNYASnvK/aQJmI9NxuOoaoqbL/yrZ58caJG82TrDKGgByvAYcT5yJkJqGRuLlF3XL1p2C0P8nxf2dzfjQgy5LGvZ1awEsIeoSdEuicaxFoxkxzTH/OM2WSLuJ+VbFg8Xl0j3F5kP9sT/no1Gau15zSHxQmjmpGJSjiTpjSBCm4sMaJQ0upruK8RuuLAzGwNw8qRXJ4qY7Tvg36lu39KHwZ22w/VZT1cNZq1mQXvsR54Piaix163YoXfS7jke6j8L6Nm2xtY4inqd uk8s-tech-support
```


## 为什么我的容器一起来就退出了？
1. 查看容器log，排查异常重启的原因
2. pod是否正确设置了启动命令，启动命令可以在制作镜像时指定，也可以在pod配置中指定
3. 启动命令必须保持在前台运行，否则k8s会认为pod已经结束，并重启pod。

## docker如何调整日志等级
1. 修改/etc/docker/daemon.json 文件，增加一行配置"debug": true
2. systemctl reload docker 加载配置，查看日志
3. 如果不再需要查看详细日志，删除debug配置，重新reload docker即可

## 为什么节点已经异常了，但是pod还处在running状态
1. 这是由于k8s的状态保护造成的，在节点较少或异常节点很多的情况下很容易出现
2. 具体可以查看文档 https://kubernetes.io/zh/docs/concepts/architecture/nodes/#reliability

## 节点宕机了，pod一直卡在termnating怎么办
1. 节点宕机超过一定时间后（一般为 5 分钟），k8s 会尝试驱逐 pod，导致 pod 变为 Termnating 状态
2. 由于此时 kubelet 无法执行删除pod的一系列操作，pod 会一直卡在 Termnating
3. 类型为 daemonset 的 pod，默认在每个节点都有调度，因此 pod 宕机不需要考虑此种类型 pod，k8s 也默认不会驱逐该类型的 pod
4. 类型为 depolyment 和 replicaset 的 pod，当 pod 卡在 termanting 时，控制器会自动拉起对等数量的 pod
5. 类型为 statefulset 的 pod，当 pod 卡在 termanting 时，由于 statefulset 下属的 pod 名称固定，必须等上一个 pod 彻底删除，对应的新 pod 才会被拉起，在节点宕机情况下无法自动拉起恢复
6. 对于使用 udisk-pvc 的 pod，由于 pvc 无法卸载，会导致新起的 pod 无法运行，请按照本文 pvc 相关内容(#如何查看pvc对应的udisk实际挂载情况)，确认相关关系

## Pod异常退出了怎么办？
1. `kubectl describe pods pod-name -n ns` 查看 pod 的相关 event 及每个 container 的 status，是 pod 自己退出，还是由于 oom 被杀，或者是被驱逐
2. 如果是 pod 自己退出，`kubectl logs pod-name -p -n ns` 查看容器退出的日志，排查原因
3. 如果是由于 oom 被杀，建议根据业务重新调整 pod 的 request 和 limit 设置（两者不宜相差过大），或检查是否有内存泄漏
4. 如果 pod 被驱逐，说明节点压力过大，需要检查时哪个 pod 占用资源过多，并调整 request 和 limit 设置
5. 非 pod 自身原因导致的退出，需要执行`dmesg`查看系统日志以及`journactl -u kubelet`查看 kubelet 相关日志。


## CNI插件升级为什么失败了？
1. 检查节点是否设置了污点及禁止调度（master 节点的默认污点不计算在内），带有污点的节点需要选择强制升级（不会对节点有特殊影响）。
2. 如果强制升级失败的，请重新点击 cni 强制升级。
3. 执行`kubectl get pods -n kube-system |grep plugin-operation`找到对应插件升级的 pod，并 describe pod 查看 pod 失败原因。

## UK8S页面概览页一直刷新不出来？
1. api-server 对应的 ulb4 是否被删除（`uk8s-xxxxxx-master-ulb4`）
2. UK8S 集群的三台 master 主机是否被删了或者关机等
3. 登陆到 UK8S 三台 master 节点，检查 etcd 和 kube-apiserver 服务是否正常，如果异常，尝试重启服务

    3.1  `systemctl status etcd`  / `systemctl restart etcd` 如果单个 etcd 重启失败，请尝试三台节点的 etcd 同时重启

    3.2  `systemctl status kube-apiserver`  / `systemctl restart kube-apiserver`

## UK8S节点NotReady了怎么办
1. `kubectl describe node node-name` 查看节点 notReady 的原因，也可以直接在 console 页面上查看节点详情。
2. 如果可以登陆节点，`journactl -u kubelet` 查看 kubelet 的日志， `system status kubelet`查看 kubelet 工作是否正常。
3. 对于节点已经登陆不了的情况，如果希望快速恢复可以在控制台找到对应主机断电重启。
4. 查看主机监控，或登陆主机执行`sar`命令，如果发现磁盘 cpu 和磁盘使用率突然上涨, 且内存使用率也高，一般情况下是内存 oom 导致的。关于内存占用过高导致节点宕机，由于内存占用过高，磁盘缓存量很少，会导致磁盘读写频繁，进一步增加系统负载，打高cpu的恶性循环
5. 内存 oom 的情况需要客户自查是进程的内存情况，k8s 建议 request 和 limit 设置的值不宜相差过大，如果相差较大，比较容易导致节点宕机。
6. 如果对节点 notready 原因有疑问，请按照[UK8S人工支持](#UK8S人工支持)联系人工支持


## 为什么我的集群连不上外网?
1. 集群若需要访问公网，进行拉取镜像等操作，需要为集群所在 VPC 绑定 NAT 网关，并配置相应规则，详见：https://docs.ucloud.cn/vpc/introduction/natgw


## 为什么我的UHub登陆失败了?
1. 请确认是在公网还是ucloud内网进行登陆的（如果ping uhub 的ip为117.50.7.5 则表示是通过公网拉取）
2. 如果在公网登陆，请在uhub的console页面确认外网访问选项打开
3. 是否使用独立密码登陆，uhub独立密码是和用户绑定的，而不是和镜像库绑定的

## UHub下载失败（慢）
2. `ping uhub.service.ucloud.cn` （如果ip为117.50.7.5 则表示是通过公网拉取，有限速）
3. `curl https://uhub.service.ucloud.cn/v2/` 查看是否通，正常会返回 UNAUTHORIZED 或 301
4. `systemctl show --property=Environment docker` 查看是否配置了代理
5. 在拉镜像节点执行`iftop -i any -f 'host <uhub-ip>'`命令，同时尝试拉取 uhub 镜像，查看命令输出（uhub-ip替换为步骤1中得到的ip）
6. 对于公网拉镜像的用户，还需要在 console 页面查看外网访问是否开启

## pv, pvc, sc 以及udisk的各种关系？
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
用户只需要设置好StorageClass，在使用pvc时，csi-udisk插件会自动完成udisk的创建挂载mount等一系列的操作，主要流程如下
1. StorageClass设置相关参数，与csi插件绑定。
2. pvc与StorageClass 进行绑定。
3. k8s观察到使用StorageClass的新建pvc，会自动创建pv，并交给csi插件完成新建udisk的工作。
4. pv与pvc绑定完成，csi插件完成后续udisk的挂载和mount等工作。
5. ucloud的csi查看可以通过`kubectl get pods -o wide -n kube-system |grep udisk` 查看（一个总的controller及每个node对应的pod）

### Statefulset中使用pvc 
1. Statefulset控制器中的pvctemplate字段，可以设置k8s集群在对应pvc不存在时自动创建pvc，使得上述流程更加自动化(pvc和pv均由UK8S来建)。
2. statefulset 只负责创建不负责删除pvc，因此对应多余的pvc，需要手动删除


## VolumeAttachment的作用
VolumeAttachment 并不由用户自己创建，因此很多用户并不清楚它的作用，但是在pvc的使用过程中，VolumeAttachment有着很重要的作用

1. volumeattachment所表示的，是k8s集群中记载的pv和某个node的挂载关系。可以执行`kubectl get volumeattachment |grep pv-name` 进行查看
2. 这个挂载关系和udisk与云主机的挂载关系往往是一致的，但是有时可能会出现不一致的情况。
3. 不一致的情况多见于udisk已经从云主机卸载，但是volumeattachment记录中仍然存在，udisk是否挂载在云主机上，可以通过[如何查看pvc对应的udisk实际挂载情况](#如何查看pvc对应的udisk实际挂载情况)来查看
4. 对于不一致的情况，可用选择手动删除对应的volumeattachment字段，并新建一个相同的volumeattachment（新建后ATTACHED 状态为false）
5. 如果不能删除，可以通过`kubectl logs csi-udisk-controller-0 -n kube-system csi-udisk` 查看csi-controller日志定位原因
6. 一般kubelet手动删除不掉的情况，可能是对应的节点已经不存在了，此时直接 edit volumeattachment 删除 finalizers字段即可
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

## 如何查看pvc对应的udisk实际挂载情况
对应关系表
|UK8S资源类型|与主机对应关系|
|--|--|
|PV|udisk的磁盘|
|volumeattachment| 磁盘与主机的挂载关系(vdb,vdc的块设备)|
|pvc| 磁盘在主机上mount的位置|
|pod| 使用磁盘的进程|
1. `kubectl get pvc -n ns pvc-name` 查看对应的VOLUME字段，找到与pvc绑定的pv，一般为（pvc-e51b694f-ffac-4d23-af5e-304a948a155a）
2. `kubectl get pv pv-name -o yaml` 在spec.csi.volumeHandle 字段，可以查看到改pv绑定的udisk盘(flexv插件为pv的最后几位)
3. 在控制台查看该udisk盘的状态,是否挂载到某个主机
4. `kubectl get volumeattachment |grep pv-name` 查看k8s集群内记录的磁盘挂载状态,[volumeattachment的作用](#volumeattachment的作用)
5. ssh到对应的主机上，`lsblk`可以看到对应的盘
6. `mount |grep pv-name` 可用查看盘的实际挂载点，有一个globalmount及一个或多个pod的mount点
```sh
[root@10-9-184-108 ~]# mount |grep pvc-e51b694f-ffac-4d23-af5e-304a948a155a
/dev/vdc on /data/kubelet/plugins/kubernetes.io/csi/pv/pvc-e51b694f-ffac-4d23-af5e-304a948a155a/globalmount type ext4 (rw,relatime)
/dev/vdc on /data/kubelet/pods/587962f5-3009-4c53-a56e-a78f6636ce86/volumes/kubernetes.io~csi/pvc-e51b694f-ffac-4d23-af5e-304a948a155a/mount type ext4 (rw,relatime)
```
## 磁盘挂载的错误处理
1. 由于磁盘内容多流程长，建议在出现问题时，首先确定当前状态[如何查看pvc对应的udisk实际挂载情况](#如何查看pvc对应的udisk实际挂载情况)
2. 如果有UK8S中状态和主机状态不一致的情况，首先进行清理，删除掉不一致的资源，之后走正常流程进行恢复 

### pv和pvc一直卡在terminating/磁盘卸载失败怎么办
1. 通过[如何查看pvc对应的udisk实际挂载情况](#如何查看pvc对应的udisk实际挂载情况) 确定当前pv和pvc的实际挂载状态
2. 手动按照自己的需求进行处理，首先清理所有使用该pv和pvc的所有pod（如果pvc已经成功删除，则不需要这一步）
3. 如果删除pvc卡在terminating，则手动umount掉对应的挂载路径
4. 如果删除volumeattachment卡在terminating，则手动在控制台卸载掉磁盘（如果卡在卸载中找主机处理）
5. 如果删除pv卡在terminating，则手动在控制台删除掉磁盘（删除pv前需要确保相关的volumeattachment已经删除完成）
6. 确保手动释放完成对应的资源后，可以通过`kubectl edit` 对应的资源,删除掉其中的finalizers字段，此时资源就会成功释放掉
7. 删除volumeattachment后，如果pod挂载报错，按照[volumeattachment的作用](#volumeattachment的作用)中提供的yaml文件，重新补一个同名的volumeattachment即可

### pod的pvc一直挂载不上怎么办？
1. `kubectl get pvc -n ns pvc-name` 查看对应的VOLUME字段，找到与pvc绑定的pv，一般为（pvc-e51b694f-ffac-4d23-af5e-304a948a155a）
2. `kubectl get pv pv-name -o yaml` 在spec.csi.volumeHandle 字段，可以查看到改pv绑定的udisk盘(flexv插件为pv的最后几位)
3. 找到udisk磁盘后，如果控制台页面中磁盘处于可用状态或者挂载的主机不是pod所在主机，可以找技术支持，查看该udisk的挂载和卸载请求的错误日志，并联系主机同时进行处理
4. 如果没有udisk相关的错误日志，联系UK8S值班人员，并提供`kubectl logs csi-udisk-controller-0 -n kube-system csi-udisk`的日志输出及pod的event

## udisk-pvc使用注意事项
1. 由于udisk不可跨可用区，因此在建立StorageClass时必须指定volumeBindingMode: WaitForFirstConsumer
2. 由于udisk不可多点挂载，因此必须在pvc中指定accessModes 为 ReadWriteOnce
3. 基于udisk不可多点挂载，多个pod不可共用同一个udisk-pvc，上一个pod的udisk-pvc未处理干净时，会导致后续pod无法创建，此时可以查看volumeattachment的状态进行确认

## 为什么在k8s节点docker直接起容器网络不通
1. UK8S使用ucloud自己的cni插件，而直接用docker起的容器并不能使用该插件，因此网络不通。
2. 如果需要长期跑任务，不建议在UK8S节点用docker直接起容器，应该使用pod
3. 如果只是临时测试，可以添加`--network host` 参数，使用hostnetwork 的模式起容器


## 使用ulb4时vserver为什么会有健康检查失效
1. 如果svc的externalTrafficPolicy为Local时，这种情况是正常的，失败的节点表示没有运行对应的Pod
2. 需要在节点上抓包 `tcpdump -i eth0 host <ulb-ip>` 查看是否正常, ulb-ip替换为svc对应的实际ip
3. 查看节点上kube-proxy服务是否正常 `systemctl status kube-proxy`
4. 执行`iptables -L -n -t nat |grep KUBE-SVC` 及 `ipvsadm -L -n`查看转发规则是否下发正常

## ulb4对应的端口为什么不是nodePort的端口
1. k8s节点上对 ulb_ip+serviceport的端口组合进行了iptables转发，所以不走nodeport
2. 如果有兴趣，可以通过在节点上执行`iptables -L -n -t nat` 或者`ipvsadm -L -n` 查看对应规则 