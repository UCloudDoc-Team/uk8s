
## 名词解释

为了帮助你更好地使用UK8S，你需要对Kubernetes的相关组件有一个大致的了解，本文会对基础组件及概念做一个简要的介绍，如果你希望了解更多内容，请移步[Kubernetes官方文档](https://kubernetes.io/docs/concepts/)

### Kubernetes基础架构

![](/images/introduction/kubernetes-whole-arch.png)
备注：图片源自Kubernetes社区

上图是一个概要性的Kubernetes架构，包含了ApiServer，Master、Node、Hub（镜像仓库）等概念，下面我们依次做个简要介绍。

**ApiServer：** ApiServer是操作集群的唯一入口，并提供认证、授权、访问控制、API注册和发现等机制，ApiServer作为一个组件运行在Master上。

**Node：**Node是Kubernetes的工作节点，其上包含运行Pod所需要的服务。Node可以是虚拟机也可以是物理机，在UK8S，目前只支持虚拟机即UHost。

**Master：** Master也是Kubernetes的工作节点，与Node不同的是，Master通常不运行业务Pod，而是安装了用于控制和管理集群的如ApiServer、Scheduler、Controller Manager、Cloud Controller Manager、ETCD等组件。

**Hub镜像仓库** Hub提供Docker镜像的管理、存储、分发能力。



