# RSSD云盘挂载问题

一般的云盘在挂载的时候，需要确保其跟主机处于同一个可用区下面。但是对于RSSD云盘来说，除了可用区，还需要确保它们处于同一个`RDMA集群`中。`RDMA`是一个比可用区更小的概念，它在控制台界面是隐藏的，只能通过API指定和查询。

总体来说，一个RSSD云盘对于主机有以下要求：

- 主机必须是O型，即快杰型主机。
- 主机跟云盘处于同一可用区。
- 主机跟云盘处于同一`RDMA`。

如果满足前两点但是不满足第三点，挂载会失败。失败的报错一般是（关注错误码为`17218`）：

```txt
[17218] Command failed: add_udisk.py failed
```

`RDMA`还有一个问题是，它是随时可能发生变更的，即主机可能对云盘或主机的`RDMA`进行迁移，并且变更后无法通知下游服务。

CSI在处理使用了RSSD云盘的Pod时，需要解决下面两个问题：

- 新建RSSD云盘时，确保其`RDMA`跟Pod所处的节点一致。
- 重新调度使用了RSSD云盘的Pod时，确保调度的节点是O型，并且`RDMA`跟云盘一致。

**一般来说，用户不需要关心上述问题，但是因为CSI历史设计的原因，`22.09.1`以前的CSI在处理RSSD云盘时，如果遇到`RDMA迁移`，将会发生很严重的挂载失败问题，下面我将对CSI调度RSSD云盘机制进行详细的讲解，以方便您更好地理解这个问题，并知晓为什么在使用RSSD云盘的情况下要把CSI升级到`22.09.1`及以上。**

## 静态调度

> 这是`22.09.1`以下版本CSI采用的方案。

在`22.09.1`以及以前的csi中，是通过在pv上增加`nodeAffinity`来实现的。有关节点亲和性，请见官方文档：[Assign Pods to Nodes using Node Affinity](https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes-using-node-affinity/)。

对于快杰型云主机，其node上面会保存一个拓扑label保存RDMA字段，例如：

```yaml
topology.udisk.csi.ucloud.cn/rdma-cluster-id: 9002_25GE_D_R006
```

这表示这个node处于`006`这个`RDMA集群`中。

对于RSSD云盘PV，会在其`nodeAffinity`上保存RDMA：

```yaml
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: topology.udisk.csi.ucloud.cn/rdma-cluster-id
              operator: In
              values:
                - 9002_25GE_D_R006
```

上面两个字段都是CSI写入的，并且一旦写入，就不再可以变更。在调度的时候，通过节点亲和性机制，就确保了使用RSSD云盘的Pod只会被调度到RDMA匹配的节点上面：

![](/uk8s/images/volume/rssd-pv-nodeaffiniy.png)

如果RDMA一直不发生变更，这没有问题，但是一旦发生`RDMA迁移`，UK8S无法探测到这种迁移，也就无法更新这上面的信息，就发生了数据不一致。

即使UK8S能够探测到这种迁移，因为`nodeAffinity`是`immutable`，我们也无法通过更新字段的方式来更新信息。

而如果出现数据不一致，就会发生严重的问题，假设云盘的实际RDMA为`005`，但是其在UK8S中保存的RDMA为`006`，根据节点亲和性，使用了它的Pod会被调度到RDMA为`006`的节点上面，跟实际的RDMA不匹配，最终会导致云盘挂载失败。

如果您的CSI版本低于`22.09.1`，出现了RSSD云盘挂载不上的情况，并且在CSI日志中发现`17218`错误码，那么十有八九就是因为RDMA迁移导致的问题。

**可见，我们不应该在UK8S集群中以任何方式储存RDMA信息，这样的信息是完全不可靠的。我们应该动态地获取RDMA进行调度。**

## 动态调度

> 这是`22.09.1`以及以上版本CSI采用的方案(此版本要求Kubernetes版本不低于1.18)。

在`22.09.1`及以后版本的CSI中，将不再采用节点亲和性来调度RSSD云盘，所有RDMA信息都将会动态获取并调度。在不考虑存量数据的情况下，通过动态调度即可解决RDMA迁移的问题。

要想实现动态调度，至少需要在下面两个地方插入动态逻辑：

- 创建RSSD云盘时，动态获取节点的RDMA。
- 调度RSSD云盘时，动态获取云盘和节点的RDMA进行匹配。

下面两节将分别介绍CSI如果解决上面两个问题。

### 创建RSSD云盘

创建RSSD云盘是在CSI里面实现的，因此我们只需要更改CSI创建云盘的逻辑即可：

- 将`topology.udisk.csi.ucloud.cn/rdma-cluster-id`这个拓扑标签移除。
- 新建PV时，不再写入`topology.udisk.csi.ucloud.cn/rdma-cluster-id`这个`nodeAffinity`。
- 创建RSSD云盘时，调用API获取节点的RDMA信息，并传递给RSSD云盘创建接口，见：[CreateUDisk API文档](https://docs.ucloud.cn/api/udisk-api/create_udisk?id=%e8%af%b7%e6%b1%82%e5%8f%82%e6%95%b0)。

这样，新创建的RSSD云盘将不再依赖节点亲和性进行调度了。

### 调度RSSD云盘

调度器在调度包含RSSD的Pod时，需要能动态获取RSSD的RDMA 信息，这里是需要调用UCloud API的。原生的kube-scheduler肯定是无法实现，需要通过kube-scheduler提供的扩展机制来完成。

这里说明一下，KubeScheduler提供了两种扩展调度的机制，即Extender机制和Framework机制，下面简要地说明一下它们之间的差异：

- `scheduler extender`：需要将调度插件部署在master节点上面，调度器在调度的时候会在不同的扩展点通过HTTP的方式调用扩展。
- `scheduler framework`：完全编译一个独立的调度器，可以在里面插入自己的调度逻辑。单独作为Deployment部署在集群中，要使用这个调度器，需要修改`schedulerName`配置。

一般来说官方更加推荐使用第二种方式来扩展调度器，但是我们不希望修改`schedulerName`，并且第二种方式意味着需要为不同版本的Kubernetes维护不同的调度器版本，后期维护起来也更加麻烦，因此我们使用了第一种扩展方式。

这要求在集群的master节点上单独部署一个HTTP服务，它用于实现自己的调度逻辑，然后需要在调度器的配置中增加`extenders`相关内容：

```yaml
extenders:
  - urlPrefix: http://127.0.0.1:6678/
    filterVerb: filter
    httpTimeout: 60s
```

这表示对调度的`filter`点进行扩展，扩展时调用`http://127.0.0.1:6678/filter`这个接口。

> 特别注意：extenders这个特性是在scheduler的v1beta2版本之后引入的，所以如果Kubernetes版本低于1.19，我们是无法进行扩展的。如果您使用了低版本的Kubernetes，应该先升级Kubernetes版本。

这样，就可以在扩展点内调用UCloud API，来动态获取RSSD以及node的RDMA Cluster信息，并根据这个信息对node进行过滤了：

![](/uk8s/images/volume/csi-scheduler-extender.png)

scheulder-extender会检查Pod是否使用了RSSD的PV，如果使用了，会调用UCloud API获取PV以及节点的RDMA信息，并根据这个信息过滤掉不匹配的节点。

在部署的时候，需要在您集群的master节点上面新加一个`systemd`，叫做`scheduler-extender-uk8s`，可以通过下面的命令检查服务的健康：

```shell
systemctl status scheduler-extender-uk8s
```

如果调度出现了问题，可以通过下面的命令查看日志：

```shell
journalctl -u scheduler-extender-uk8s.service -f
```

在安装1.19以及以上的集群时，uk8s会自动将`scheduler-extender-uk8s`安装到所有master节点上面，关于如何处理现有集群，请参考后面的内容。

## 通过控制台升级CSI并安装scheduler-extender

**这里一定要特别注意，新版本的csi必须配合scheduler-extender使用，所以，在升级`22.09.1`的CSI时，请到控制台操作，不要通过自行修改image完成。**

新的csi版本中将会集成scheduler-extender的版本，格式为`{csi-version}-se{scheduler-extender-version}`，例如`22.09.1-se22.08.3`表示csi的版本为`22.09.1`，scheduler-extender版本为`22.08.3`。如果集群中没有安装scheduler-extender，格式为`{csi-version}-se-unknown`，例如`21.09.1-se-unknown`。

通过这种集成版本号的方式，可以很方便地将csi跟scheduler-extender绑定在一起，并且不需要单独增加scheduler-extender插件的管理页面。

### 查询版本

查询csi版本可以通过直接查询`StatefulSet`中的`image`完成，而查询`scheduler-extender`版本比较复杂，需要登录集群的master节点并通过命令调用的方式完成，因为scheduler-extender是通过systemd部署的。

这里就需要异步任务介入了，我们需要在master节点上面部署Job来完成scheduler-extender版本的查询。原来的csi版本查询是同步完成的，这里需要修改为异步调用，跟cni的版本查询类似。

### 升级不一致问题

以后在升级csi的时候，必须首先升级或安装scheduler-extender，因为前文介绍过，新的csi必须依赖scheduler-extender才可以工作。如果scheduler-extender升级或安装失败，必须停止整个csi升级过程。

这里可能产生的不一致是scheduler-extender安装成功了，但是csi没有升级成功。这会导致集群中RSSD PV通过scheduler-extender和通过nodeAffinity的约束同时存在。而这两个约束做的事情无非都是确保RSSD PV被调度到RDMA Cluster一致的node上面，只不过一个是动态的，一个是静态的。两个约束同时存在实际上是不冲突的。

综上：

- 可以容忍scheduler-extender安装成功，csi升级失败，因为这相当于同时存在了两个约束，后续让客户重试升级csi即可。
- 不可以容忍scheduler-extender未安装的情况下升级csi，因为这相当于集群不存在对RSSD PV的约束了。

所以我们没有做升级失败的回滚，只要确保先升级scheduler-extender再升级csi即可。

除此之外，在升级csi时，我们还加了下面的约束：

- 如果集群的版本低于1.19.x，不允许升级csi，需要客户先把集群版本升级上去。
- 如果客户集群中存在包含RDMA nodeAffinity的PV，不允许升级csi，因为这需要人为介入来hack数据（详见后面处理历史存量数据的章节）。

## 处理历史存量数据

上面就解决了所有新建RSSD云盘的问题，但是缺少对于存量数据的处理。

一般想到的是，在升级完成之后把PV上面的nodeAffinity数据移除就好了，但是Kubernetes有个很蛋疼的设计，就是`nodeAffinity`是`immutable`的，无法直接进行修改。而只要`nodeAffinity`存在，kube-scheduler就会根据节点亲和性来约束PV，当磁盘迁移时，就会发生问题。

我们需要通过特殊的手段来把PV上面的nodeAffinity移除掉。这里的`手段`是非常hack的，需要直接修改etcd的数据，因此这会是一个非常非标的操作，不能集成自动化工具中，需要人工介入进行处理。

**如果您的集群中有存量RSSD云盘数据，请联系我们的技术支持，我们会手动为您修复数据。**