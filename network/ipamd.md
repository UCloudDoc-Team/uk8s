# IPAMD

IPAMD的全称是`IP Address Manager Deamon`，它是一个独立于CNI的守护进程，用于管理IP地址的分配和回收。

IPAMD是一个可选组件，**如果部署IPAMD，最高可以提升90%的Pod创建速度**，大大减少CNI的延迟。这主要通过IP池子来实现。另外，如果要使用固定IP，则必须部署IPAMD，关于固定IP可以参考我们的另一篇文档：[static IP](https://docs.ucloud.cn/uk8s/network/static_ip)

IPAMD在Kubernetes中通过DeamonSet的形式部署，不需要对CNI进行额外的配置，CNI会自动感知IPAMD的存在。

在新版本的UK8S集群中，我们将会默认为您部署IPAMD，您可以通过下面的命令查看IPAMD状态：

```bash
kubectl -n kube-system get ds cni-vpc-ipamd
```

如果是老的集群，可以通过升级cni来部署IPAMD，详见[CNI升级](./cni_update.md)。

您可以登录任一集群中的master节点，通过下面的命令来查看集群中IPAMD的IP数量以及池子的状态：

```bash
ipamctl status
```

`ipamctl`是用于管理IPAMD的命令，通过它您可以快速了解集群中IPAMD的使用情况。

## IP池子

IPAMD对于CNI延迟的优化主要在于IP池子的设计。IP池子是一个预分配的VPC IP列表。IP池子有两个比较重要的参数：`高水位`和`低水位`，IPAMD会定期检查池子中IP数量：

- 如果IP数量小于`低水位`，会尝试分配IP直到数量大于等于低水位。低水位默认为5。
- 如果IP数量大于`高水位`，会尝试释放IP直到数量小于等于高水位。高水位默认为50。

总体来说，IPAMD会尽量将池子中的IP数量控制在低水位和高水位之间。

IP池子的数据会被持久化储存在本地sqlite3数据库中，以在IPAMD程序重启之后能够恢复。

### 创建Pod

在创建Pod的时候，CNI会调用IPAMD取用新的IP，IPAMD会检查池子：

- 如果池子中有空闲的IP，将其中最早创建的IP分配给该Pod。
- 如果池子中没有空闲IP了，调用VPC获取一个新的IP分配给该Pod。

IPAMD会优先选择最早未使用的IP给新的Pod使用（类似LRU），以最大限度避免IP被反复重用。

这里有一个异常情况是，如果vpc的子网IP耗尽了，那么在创建Pod的时候，IPAMD会进行IP的`借调`，即尝试借用其他IPAMD的IP。通过IP借调，在IP枯竭的情况下，可以最大化地利用IP资源，避免IP的分配不均。关于IP借调的详细设计，可以参考[这个PR](https://github.com/ucloud/uk8s-cni-vpc/pull/4)。

### 销毁Pod

在Pod被销毁时，会调用IPAMD将IP回收。IP在被回收前，会经过一个30s的冷却时间，处于冷却状态中的IP不会被释放或分配。在冷却结束之后，IP会被重新放回到池子中。

设计冷却时间的意义是，防止Pod销毁在被其它应用感知之前，就将IP分配给了另一个Pod。如果出现这种情况可能会导致对IP强依赖的分布式应用的混乱（例如Redis哨兵模式），分配IP时采用LRU也是为了在一定程度上避免这个问题。

## 性能测试

IPAMD在Pod数量越多时越能带来显著的性能提升，为了进行直观对比，我们分别创建10、30、50个Pod，计算它们在有IPAMD和没有IPAMD的情况下的创建时间。

因为IPAMD有慢启动的问题，所以我们增加了一组IPAMD池子处于低水位和高水位的对照。IP池子的低水位配置为5，高水位配置为50。

|         | 无IPAMD | IP池子处于低水位 | IP池子处于高水位 |
| ------- | ------- | ---------------- | ---------------- |
| 10个Pod | 93s     | 68s              | 12s              |
| 30个Pod | 283s    | 205s             | 30s              |
| 50个Pod | 355s    | 315s             | 80s              |

**可以看到，在IPAMD运行一段时间之后，池子处于高水位时，会带来巨大的性能提升，最高可以达到90%。**因此，对于Pod数量较大，并且频繁创建和销毁的场景，IPAMD可以带来显著的性能提示。