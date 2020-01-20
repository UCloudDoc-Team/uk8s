
## 使用必读

> 注意：通过UK8S创建的云主机、云盘、EIP等资源，删除资源请不要通过具体的产品列表页删除，否则可能导致UK8S运行不正常或数据丢失风险，可以通过UK8S将资源释放或解绑删除。

UK8S为容器应用提供编排、调度的能力，应用本身是运行在UCloud的IAAS类产品上，如UHost、UDisk、EIP、ULB等，为了帮助你更好地使用UK8S，你需要知道并同意：

1. 你需要授权给 UK8S 部分产品的管理权限，以便你在操作集群时可以利用到 UCloud的其他产品，如创建一个 PVC时，集群帮你创建一块 UDisk；

2. 通过集群创建的诸如EIP、UDisk等资源，会产生相应的费用，详见[UK8S价格](/compute/uk8s/price)；

3. 组成UK8S集群的基础设施，如UHost、UDisk等，你可以在UCloud Console页面查看到，请勿随意更改或删除；


### 授权给UK8S云产品的管理权限
要使用UK8S服务，你需要给UK8S授权一系列产品权限，授权成功后，UK8S才能以你的名义创建和管理一系列云资源，请确保你的账号有以下产品的增删改查权限，否则集群工作可能异常。

UK8S会使用到以下产品的全部操作权限，例如代替你创建、删除云主机，由此产生的费用由你负责，请知悉。

1. 云主机的所有操作权限（action:*UHostInstance）

2. 云硬盘的所有操作权限（action:*UDisk）

3. 负载均衡的所有操作权限（action:*ULB）

4. EIP的所有操作权限（action:*EIP）

5. VPC的所有操作权限（action:*VPC）

### 请勿随意操作由UK8S创建的资源

如上文所述，UK8S会以你的名义创建一批云资源，例如UHost、UDisk等，这些云资源是UK8S集群所依赖的基础设施，一旦更改，可能对集群操作无法预估的影响，请勿随意改动。

**如何识别由UK8S创建的云资源？**

由UK8S创建的云资源名称，都遵循明确的命名规范，具体详见[命名规范](/compute/uk8s/introduction/restriction),简要说明如下：

1. UHost名称：[cluster-id]-[nodetype]-[randomcode]，如名称为uk8s-uxl1l3l0-n-4rd91的云主机，是"uk8s-uxl1l3l0"这个UK8S集群的Node节点。

2. ULB名称：[cluster-id]-[master]-ulb，如名称为uk8s-uxl1l3l0-master-4rd91的ULB，是内网ApiServer的入口，切勿删除。

