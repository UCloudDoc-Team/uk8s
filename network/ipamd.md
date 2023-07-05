# CNI Ipamd预分配VPC IP实现原理和部署架构

## 背景与原理

受制于UCloud底层网络技术现状，Pod的VPC IP新申请后，需要先进行[arping](https://www.rfc-editor.org/rfc/rfc5227)以确保流表已经下发并且没有冲突，该过程至少需要5s的时间，最长需要15s。也就是说，Pod至少需要5s时间才能创建出来，再加上镜像拉取以及各种初始化操作，Pod创建时间基本延长到了平均10s以上。这对于要求快速拉起和销毁的Pod来说，几乎是不可接受的。

并且，因为所有Pod的创建和销毁都需要调用VPC服务，在VPC服务因为各种因素不可达时，会导致Pod无法被创建或销毁，集群处于一个几乎不可用的状态，发布流程会被完全阻塞。

为了解决上述问题，在CNI层面，可以通过预先分配好一批VPC IP，维护VPC IP池，给新创建的Pod分配IP池中的VPC IP。由于池子中的IP已经提前从UNetwork API中申请好并完成arping操作，因此能够立即分配给Pod，缩短5-15s的Pod创建时间。

此外，在VPC挂掉的情况下，池子也能绕开VPC服务独自承担Pod IP的申请和回收（在池子中IP充足时），提高集群的可用性。

## CNI预分配IP方案详解

新版CNI分成两大部分：

*  cnivpc二进制文件。作为与Kubelet通信的入口。Kubelet通过调用该二进制可执行文件实现Pod网络的创建和摘除。
*  ipamd服务。一个负责申请，维护，释放VPC IP的常驻Daemon进程，通过Unix Domain Socket向cnivpc提供分配和释放VPC IP的gRPC API。它作为DaemonSet部署在UK8S集群中。您可以将其理解为类似[Calico IPAM](https://docs.tigera.io/calico/latest/networking/ipam/get-started-ip-addresses)的组件。

总体架构如下图所示。

![ipamd](/images/ipamd.jpg)

**核心流程包括：**

1.  ipamd内部包含了一个控制循环，它会定时从BoltDB（本地数据库）中检查目前可用的VPC IP是否低于IP池的低水位。如果低于低水位，则调用UNetwork AllocateSecondaryIp API给所在Node分配IP并将IP存入BoltDB中。如果VPC IP高于高水位，则调用UNetwork DeleteSeconaryIp将BoltDB中多出来的IP释放掉。
2.  ipamd通过unix:/run/cni-vpc-ipamd.sock向cnivpc提供以下三个gRPC接口：
    * **Ping**: ipamd服务可用性探活接口。cnivpc每次申请，释放IP前都会调用该接口。如果失败，cnivpc的工作流程退化回原方案。   
    * **AddPodNetwork**：给Pod分配IP接口，如果BoltDB IP池中存在可用IP，则直接从IP池中给Pod分配IP；否则立刻向UNetwork API申请IP，这种情况下，Pod启动依然需要5-15秒。
    * **DelPodNetwork**：释放Pod IP接口。Pod被销毁后，IP会进入冷却状态，冷却30s之后，会被重新放回IP池子中。
3.  ipamd服务如果被杀，它会响应Kubelet发送来的SIGTERM信号，停止gRPC服务并删除对应的Unix Domain Socket文件。
4.  ipamd服务是可选组件，即使它异常终止了，cnivpc也能正常工作，但是会丧失预分配的能力。
5.  如果ipamd发现VPC的IP已经被分配完了，会尝试从其他同一子网的ipamd的池子中借用IP。如果其他ipamd也没有可用IP了，创建Pod会报错。

## 相关入口参数


*  **--availablePodIPLowWatermark=3**: VPC IP预分配低水位，单位：个。默认为3
*  **--availablePodIPHighWatermark=50**：VPC IP预分配高水位，单位：个。默认为50
*  **--cooldownPeriodSeconds=30**: VPC IP冷却时间，Pod IP在被归还之后，需要经过冷却后才会被重新放回池子中，这是为了确保路由被销毁，单位：秒。默认为30s

## 部署方法

直接在集群中部署[cni-vpc-ipamd.yml](https://github.com/ucloud/uk8s-cni-vpc/blob/main/deploy/ipamd.yaml)。

检查ipamd是否启动:

```
# kubectl  get pod -o wide  -n kube-system -l app=cni-vpc-ipamd
NAME                  READY   STATUS    RESTARTS   AGE   IP              NODE            NOMINATED NODE   READINESS GATES
cni-vpc-ipamd-6v6x8   1/1     Running   0          59s   10.10.135.117   10.10.135.117   <none>           <none>
cni-vpc-ipamd-tcc5b   1/1     Running   0          59s   10.10.7.12      10.10.7.12      <none>           <none>
cni-vpc-ipamd-zsspc   1/1     Running   0          59s   10.10.183.70    10.10.183.70    <none>           <none>

```

**注意：在1.20以上版本的集群中，ipamd将默认安装**

## 调试

在安装了ipamd的集群中，您可以通过`cnivpctl`命令来查看集群中池子的情况。

登录任一一台节点（可以是master或node），使用下面的命令可以列出集群中使用了ipamd的节点，以及它们池子中IP的数量：

```shell
$ cnivpctl get node
NODE            SUBNET              POOL
192.168.45.101  subnet-dsck39bnlhu  9
192.168.47.103  subnet-dsck39bnlhu  4
```

可以见到，目前我的集群有两个节点，池子中分别有9个和4个IP。

通过`cnivpctl get pool`可以进一步查看某个节点池子中所有IP：

```shell
$ cnivpctl -n 192.168.45.101 get pool
IP              RECYCLED  COOLDOWN  AGE
192.168.32.35   21h       false     21h
192.168.34.138  21h       false     21h
192.168.35.38   21h       false     21h
192.168.36.86   21h       false     21h
192.168.43.106  21h       false     21h
192.168.43.227  <none>    false     21h
192.168.45.207  21h       false     21h
192.168.45.229  <none>    false     21h
192.168.45.59   <none>    false     21h
```

不加`-n`参数，可以看到所有池子的IP，通过`-o wide`可以同时列出节点：

```shell
$ cnivpctl get pool -owide
IP              RECYCLED  COOLDOWN  AGE  NODE
192.168.32.35   21h       false     21h  192.168.45.101
192.168.34.138  21h       false     21h  192.168.45.101
192.168.35.38   21h       false     21h  192.168.45.101
192.168.36.86   21h       false     21h  192.168.45.101
192.168.43.106  21h       false     21h  192.168.45.101
192.168.43.227  <none>    false     21h  192.168.45.101
192.168.45.207  21h       false     21h  192.168.45.101
192.168.45.229  <none>    false     21h  192.168.45.101
192.168.45.59   <none>    false     21h  192.168.45.101
192.168.40.121  21h       false     21h  192.168.47.103
192.168.43.73   <none>    false     21h  192.168.47.103
192.168.44.59   <none>    false     21h  192.168.47.103
192.168.45.19   <none>    false     21h  192.168.47.103
```

通过`cnivpctl get pod`可以看到某个节点的Pod占用了哪些IP：

```shell
$ cnivpctl -n 192.168.47.103 get pod
NAMESPACE    NAME                               IP              AGE
kube-system  coredns-798fcc8f9d-jzccm           192.168.42.69   21h
kube-system  csi-udisk-controller-0             192.168.43.110  21h
kube-system  metrics-server-fff8f8668-rgfmr     192.168.36.42   21h
default      nginx-deployment-66f49c7846-gtpbk  192.168.40.14   21h
default      nginx-deployment-66f49c7846-mfgp4  192.168.34.55   21h
default      nginx-deployment-66f49c7846-s54jj  192.168.40.126  21h
kube-system  uk8s-kubectl-68bb767f87-tpzng      192.168.42.53   21h
```

这个命令的输出有点类似于`kubectl get pod`，但是只会输出占用了VPC IP的Pod，不会列出`HostNetwork`或者使用其它网络插件的Pod。

同样，不加`-n`参数，也可以列出所有Pod：

```shell
$ cnivpctl get pod -owide
NAMESPACE    NAME                               IP              AGE  NODE
kube-system  coredns-798fcc8f9d-gdrbq           192.168.41.246  21h  192.168.45.101
kube-system  coredns-798fcc8f9d-jzccm           192.168.42.69   21h  192.168.47.103
kube-system  csi-udisk-controller-0             192.168.43.110  21h  192.168.47.103
kube-system  metrics-server-fff8f8668-rgfmr     192.168.36.42   21h  192.168.47.103
default      nginx-deployment-66f49c7846-gtpbk  192.168.40.14   21h  192.168.47.103
default      nginx-deployment-66f49c7846-mfgp4  192.168.34.55   21h  192.168.47.103
default      nginx-deployment-66f49c7846-s54jj  192.168.40.126  21h  192.168.47.103
kube-system  uk8s-kubectl-68bb767f87-tpzng      192.168.42.53   21h  192.168.47.103
```

`cnivpctl`除了以上常用命令，还有一些高级用法，例如：

- `cnivpctl get unuse`：列出泄漏的IP。
- `cnivpctl pop <node> [ip]`：从指定节点的池子中弹出一个IP。
- `cnivpctl push <node> [ip]`：分配一个新的IP给指定节点的池子。
- `cnivpctl release <node> [ip]`：释放指定节点中泄漏的IP（危险操作，谨慎执行）。

关于这个命令更详细的用法，参考`cnivpctl -h`。

### 常见疑问

### Q：如何配置VPC IP池水位大小？

A: 可以通过ipamd程序入口参数--availablePodIPLowWatermark和--availablePodIPHighWatermark配置，例如:

```
      containers:
        - name: cni-vpc-ipamd
          image: uhub.service.ucloud.cn/uk8s/cni-vpc-ipamd:0.0.1
          args:
            - "--availablePodIPLowWatermark=3"
            - "--availablePodIPHighWatermark=50"
            - "--calicoPolicyFlag=true"
            - "--cooldownPeriodSeconds=30"
```

**注意:** 如果VPC IP池水位较低，节点突然被调度到大量Pod时，VPC IP池可用IP耗尽后新Pod使用的IP为最新从UNetwork API中申请的VPC IP，此时Pod依然需要经历数秒才能访问托管区；如果VPC IP水位池较高，集群节点数量较大，可能会导致子网空间IP耗尽，无法分配新VPC IP。

另外，请确保availablePodIPLowWatermark小于等于availablePodIPHighWatermark，否则ipamd启动会报错！

### Q: VPC服务挂了之后，我的Pod创建和销毁会受到影响，该怎么配置ipamd来消除这种影响？

A: 是的，如果没有ipamd，VPC服务一旦出问题，您的集群Pod创建和销毁将会无法进行。ipamd被设计出来一部分原因就是为了解决这个问题。

但是，如果ipamd配置不合理，池子中常驻的IP数量太小，VPC挂了之后，ipamd还是无法完全承担Pod的IP分配任务。

如果您对集群的可用性要求较高，希望在UCloud VPC后台系统失联的情况下也能完全正常使用集群，可以调整ipamd的低水位参数`availablePodIPLowWatermark`，将其设置为您的节点最大Pod数量，例如110。这样，ipamd就会事先分配足够多的IP，能够承担当前节点所有Pod的创建和销毁。关于如何调整水位，参考上一节。

这样虽然ipamd会在一开始分配很多IP，但是稍后ipamd就能完全承担Pod IP的管理了。

**注意：**在您这么做之前，请确保节点所在子网足够大。否则ipamd会因为IP不足无法预分配期望数量的IP。

### Q: ipamd占用了我太多IP！

A: 得益于ipamd的借用机制，即使您子网的IP被ipamd消耗完了，ipamd之间也可以互相调度IP。所以不需要担心IP的调度问题。

如果您确实不希望ipamd占用这么多IP，可以修改ipamd的两个水位参数，在最极端情况下，将它们修改为0，ipamd将不会预分配任何IP。

### Q：如果节点BoltDB文件(/opt/cni/networkstorage.db)损坏，是否会导致VPC IP泄露？

A：会。如果发生这种情况，您可以登录任一节点，使用下面的命令扫描并列出某个节点上面泄漏的IP：

```bash
cnivpctl get unuse -n xx.xx.xx.xx
```

列出并确认这些IP没有被使用后，使用下面的命令清理并释放泄漏的IP：

```bash
cnivpctl release xx.xx.xx.xx
```

该命令会列出将要释放的IP供您二次确认，请确保它们没有被任何Pod使用，确认后ipamd会自动释放这些IP。

或者，您可以直接删除节点，其绑定的VPC IP会被自动释放。

### Q: ipamd运行起来似乎有问题，怎么诊断？

A：cnivpc的调用日志是Node节点的/var/log/cnivpc.log; ipamd的日志可以通过kubectl logs观察，也可以在Node节点的/var/log/ucloud/下找到。

此外，kubelet的日志也通常必不可缺, 登录Node节点执行

```
# journalctl -u kubelet --since="12:00"
```

观察kubelet运行日志。

kubectl get events也是您排查诊断问题的好帮手。

如果依然无法定位解决问题，请联系UK8S技术团队。