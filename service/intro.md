
## Service 介绍

本章节主要为您简要介绍 Kubernetes 中的一个重要概念 Service（即服务，本文中两者等同），以及ULB的相关知识。

###Service 介绍

Service 是 Kubernetes 集群中的一个资源对象，用于定义如何访问一组带有相同特征的Pods。通常情况下，Service 通过Label Selector 来确定目标Pods，ExternalName Services 类外，关于 Service 的详细介绍，请参阅官方文档中 [Services](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)章节

Kubernetes 提供了四种类型的 Service，分别用于不同的业务场景，默认的类型是 ClusterIp 。

**ClusterIp**

ClusterIp 是 Kubernetes 中默认的服务类型 （ServiceType），选择此种类型，对应的 Service 将被分配一个集群内部的 IP 地址，只能在集群内部被访问。

**NodePort**

在每台 Node 的固定端口上暴露服务，选择 NodePort 的服务类型，集群会自动创建一个 ClusterIp 类型的服务，负责处理Node接收到的外部流量。集群外部的 Client 可以通过<NodeIp>:<NodePort>的方式访问该服务。

**LoadBalancer**

通过集群外部的负载均衡设备来暴露服务，负载均衡设备一般由云厂商提供或者使用者自行搭建，在 UK8S中，我们通过Cloud Controller Manager插件集成了 ULB，后面会有专门的介绍。需要注意的是，创建一个 LoadBalancer 的 Service，集群会自动创建一个 NodePort 和 ClusterIp 类型的 Service，用于接收从 Ulb 接入的流量。


**ExternalName**

将服务映射到一个 DNS 域名（如example.test.ucloud.cn）,DNS 域名可通过 spec.externalName 参数配置。


### ULB 简要介绍

ULB 提供了4层（基于IP+端口）和7层（基于 URL 等应用层信息）两种负载均衡类型，下表为4层和7层 ULB 的区别：

|类型|转发模式|网络|协议|
|ULB4|报文转发|内网、外网|TCP、UDP|
|ULB7|请求代理|外网|HTTP、HTTPS、TCP|

如果你希望对 ULB 有深入的了解，请访问[ULB 产品介绍](/network/ulb/index)，

在 UK8S，我们同时支持 ULB4 及 ULB7，你可以通过注释（annotations ）的形式自行配置 ULB 参数 。

下面我们分别介绍下如何通过 ULB 在内网、外网访问 Service。