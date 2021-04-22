
## 概述

### 了解K8S中的弹性伸缩

Kubernetes在多个维度、多个层次上提供不同的组件来满足不同场景下的伸缩需求，主要如下：

| 类型    | Pod  | Node                |
|:-:|:-:|:-:|
| 横向伸缩  | HPA(Horizontal Pod Autoscaler)  | Cluster Autoscaler  |
| 纵向伸缩  | VPA (Vertical Pod Autoscaler) |None        |


* **HPA:** 即容器水平伸缩（Horizontal Pod Autoscaler）负责Pod水平伸缩的组件，是所有伸缩组件中历史最悠久的，目前支持autoscaling/v1、autoscaling/v2beta1与autoscaling/v2beta2，其中autoscaling/v1只支持CPU一种伸缩指标，在autoscaling/v2beta1中增加支持custom metrics，在autoscaling/v2beta2中增加支持external metrics。

* **CA:**  即集群伸缩(Cluster Autoscaler)，负责Node节点水平伸缩的组件，1.0.0之后已是GA阶段（General Availability，即正式发布的版本），UK8S使用的为GA版本。

* **VPA:** 即Pod的纵向伸缩，根据Pod的资源利用率、历史数据、异常事件，来动态调整负载的Request值的组件，主要关注在有状态服务、单体应用的资源伸缩场景，目前（2019年8月26日）处于beta阶段，不推荐在生产环境使用。

另外，还有cluster-proportional-autoscaler伸缩组件，可根据集群的节点数目，水平调整Pod数目的组件，目前处在GA阶段，用来根据集群规模大小动态调整CoreDNS、Ingress等关键服务的规模。另外addon-resizer组件可根据集群中节点的数目，纵向调整负载的Request的组件，目前处在beta阶段。

下面我们主要来介绍下HPA和CA这两个最常用的伸缩组件。

