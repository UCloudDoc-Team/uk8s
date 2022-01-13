## 集群网络

### 概述

在我们创建一个Kubernetes集群时，为了让集群正常工作，我们需要为三类资源对象规划网段，分别是Node，Pod，Service，他们都需要唯一的网络标示。作为一个生产级别的容器编排与调度系统，Kubernetes要求各网络方案必须满足以下三点要求：

1. Pod与Pod之间网络互通，且不需要经过NAT转换。

2. Pod与Node之间网络互通，且不需要经过NAT转换。

3. Pod内部容器看到的IP，与外部应用看到的IP，应该是一样的。

基于这个准则实现的网络插件，意味着Pod必须有一个独立的IP，这与虚拟机时代的网络模型完全一致，让业务从虚拟机迁移到Kubernetes，包括协同工作提供了良好的基础。

### UK8S网络模型

Kubernetes自身只提供了网络规范和开放接口，Kubernetes用户可以安装开源的网络插件或者自行开发CNI插件，对于UK8S而言，自行开发CNI插件，需要解决以下几个网络问题。

1. Pod与Pod之间的通信问题。

2. Pod与UHost、UDB等云资源之间的通信问题。

3. Pod与Service之间的通信。Kubernetes社区提供了IPtables和IPVS两套方案，UK8S使用的IPtables方案，如果对这块的具体原理感兴趣，可以查看官方文档，此处不再赘述。

4. 集群外部与Service之间的通信。Kubernetes提供了LoadBalancer类型的Service，UK8S已支持，具体请参见[Service](/uk8s/service/intro)

综合以上几点，与第三方插件通常用的overlay方案不同，而我们结合公有云的特点，使用了underlay方案。

Pod 与Node 同属一个子网，IP都由SDN网络分配，Service 的ClusterIP 只在集群内部使用，用户只需要分配一个与VPC子网不重叠的网段即可，网段示意图如下:
![](/images/clusternetnew.png)

经测试，该网络方案下，Pod之间的网络通信性能与虚拟机之间相差无几。

### 集群通信

**一、集群内部通信**

1. 集群内Pod与Pod内网互通；

2. 集群内Pod与Node内网互通；

3. 集群内Pod与Service内网互通；

**二、与云资源通信**

1. 集群内Pod与UHost、UDB、UMem等资源内网互通（同VPC，下同）；

2. 集群内Pod与PHost内网互通；

3. 集群内Pod与混合云内网互通；
