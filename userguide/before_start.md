
# 使用必读

> 注意：通过 UK8S 创建的云主机、云盘、EIP 等资源，删除资源请不要通过具体的产品列表页删除，否则可能导致 UK8S 运行不正常或数据丢失风险，可以通过 UK8S 将资源释放或解绑删除。

UK8S为容器应用提供编排、调度的能力，应用本身是运行在 UCloud 的 IAAS 类产品上，如 UHost、UDisk、EIP、ULB等，为了帮助你更好地使用 UK8S，你需要知道并同意：

1. 你需要授权给 UK8S 部分产品的管理权限，以便你在操作集群时可以利用到 UCloud 的其他产品，如创建一个 PVC 时，集群帮你创建一块 UDisk；

2. UK8S产品本身不收取服务费用，但通过集群创建的诸如 EIP、UDisk等资源，会产生相应的费用，详见[UK8S价格](uk8s/price)；

3. 组成 UK8S 集群的基础设施，如 UHost、UDisk 等，你可以在[集群管理页面](https://console.ucloud.cn/uk8s/manage)查看到，请勿随意在其他产品列表页更改或删除；


## 授权给 UK8S 云产品的管理权限

使用 UK8S 服务前，需要您给 UK8S 授权一系列产品权限，以便集群管理服务创建和管理一系列云资源，请确保您的账号有以下产品的增删改查权限，否则集群工作可能异常。

UK8S 集群管理服务会使用到以下产品的全部操作权限，例如代替你创建、删除云主机。UK8S 产品本身不收取服务费用，但通过集群创建的诸如 EIP、UDisk 等资源，会产生相应的费用，详见 [UK8S价格](uk8s/price)

1. 云主机的所有操作权限（action:*UHostInstance）

2. 云硬盘的所有操作权限（action:*UDisk）

3. 负载均衡的所有操作权限（action:*ULB）

4. EIP的所有操作权限（action:*EIP）

5. VPC的所有操作权限（action:*VPC）

## 请勿随意操作由UK8S创建的资源

如上文所述，UK8S 会以你的名义创建一批云资源，例如 UHost、UDisk 等，这些云资源是 UK8S 集群所依赖的基础设施，一旦更改，可能对集群操作无法预估的影响，请勿随意改动。

**如何识别由UK8S创建的云资源？**

由UK8S创建的云资源名称，都遵循明确的命名规范，具体详见[命名规范](uk8s/introduction/restriction),简要说明如下：

1. UHost名称：[cluster-id]-[nodetype]-[randomcode]，如名称为uk8s-uxl1l3l0-n-4rd91的云主机，是"uk8s-uxl1l3l0"这个UK8S集群的Node节点。

2. ULB名称：[cluster-id]-[master]-ulb，如名称为uk8s-uxl1l3l0-master-4rd91的ULB，是内网ApiServer的入口，切勿删除。


## 请尽量规避将业务部署在Master节点

UK8S集群中的3台Master节点预先部署了k8s的管理服务，节点已设置为SchedulingDisabled，不建议将自己的业务调度到Master节点。