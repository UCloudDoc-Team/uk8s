## kube-proxy模式切换

在UK8S集群创建时我们会对集群创建生成默认的kube-proxy模式，在集群中新增的Node节点都会依赖这个集群默认kube-proxy模式进行新增，您可以参考以下操作进行集群kube-proxy模式的切换。


### kube-proxy模式切换操作

1. UK8S集群是您通过UCloud控制台创建的独立的集群，UK8S集群创建时会根据您选择的kube-proxy模式进行创建。已如下集群为例，集群kube-proxy模式默认是IPVS。

![](/images/userguide/kubeproxy-overview.png)

2. 创建完成后可以在集群概览中对kube-proxy模式进行修改，此修改只针对修改后的节点添加，对于集群原有节点不会修改。我们在此修改为iptables模式。

![](/images/userguide/kubeproxy-edit.png)

3. 用户可以在集群节点中查看到节点的kube-proxy模式，针对集群的kube-proxy模式进行查看，如没有可以在页面的设置中点击展示该字段。

![](/images/userguide/kubeproxy-cluster.png)

> 注：2019年12月17日前创建的节点默认没有节点的kube-proxy信息。

4. 切换集群节点的kube-proxy模式我们采用新增新节点，新节点ready后删除一个老节点的循环操作进行集群全部Node节点的kube-proxy模式切换。切换过程中老节点的Pod会调度到新的节点上。循环操作直至集群全部节点替换完成。

![](/images/userguide/kubeproxy-new.png)



### 注意事项

1. 请注意您的集群是否是多可用区的集群，如果是的话新增的Node和原Node最好保持在同一可用区。

2. 如果您是针对Node节点的IP已经做了ACL策略或者对节点IP有要求，或是对于Node节点付费存在异议，请不要使用此方案，进入每个Node节点进行kubelet参数修改，如需要此种方式调整集群的kube-proxy模式请联系UCloud售后团队获取操作文档。

3. K8S集群的节点最好统一使用一种kube-proxy模式，如果进行了切换，请将集群所有Node进行切换。

4. Master节点不在K8S调度范围内，不用进行切换。
