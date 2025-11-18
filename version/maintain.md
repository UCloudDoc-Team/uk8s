## 集群版本维护说明

UK8S是基于原生的Kubernetes提供的容器管理服务。该产品支持的集群版本会参考Kubernetes社区新版本发布节奏发布更新。以下为UK8S服务的Kubernetes版本支持机制：

### 版本支持

从2023年10月起，UK8S仅发布支持Kubernetes偶数号的三个大版本，平台支持策略如下：

#### 集群创建

您可以创建UK8S控制台支持的三个Kubernetes双数大版本的集群。
比如，控制台支持版本为 `1.20.6`、`1.22.5`和`1.24.12`三个时，当UK8S发布支持`1.26.7`后，`1.20.6`版本停止维护，您将无法创建该版本。

#### 集群升级

版本升级仅支持相邻大版本的升级，不支持跨版本升级，不支持回退版本。

#### 技术支持

UK8S控制台支持的三个版本，提供相应技术支持，如答疑、在线指导、排查问题等；过期版本的Kubernetes集群存在一定风险性，且过期版本不保证技术支持时效性，建议您及时升级Kubernetes版本。

> 对于过期版本，UK8S仅提供重大缺陷修复(影响集群的维护及删除，影响节点或Pod资源的创建、删除、维护，及重大漏洞等)，不提供功能缺陷修复，不提供新特性。

#### 插件升级

`CloudProvider`、`CSI`、`CNI`等插件，仅在上述版本的集群中提供插件升级功能。如果您需要使用最新的插件特性，请及时升级集群版本。
参考[CloudProvider插件更新](/uk8s/service/cp_update)、[CSI存储插件升级](/uk8s/volume/CSI_update)、[CNI网络插件升级](/uk8s/network/cni_update)。

#### 镜像版本

依据CentOS官方公告所知，其将停止维护CentOS Linux项目，UCloud所提供的基础镜像CentOS Linux源于CentOS官方，故在官方停止维护后UCloud也将停止对该基础镜像的维护。详细请参考[CentOS Linux停止维护后的应对方案](/uhost/introduction/image/Regarding_CentOS_EOL)
