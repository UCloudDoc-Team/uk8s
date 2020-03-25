
## 创建集群

如果你是初次接触Kubernetes，我们建议你预先创建好一个新的VPC和子网，与生产环境隔离。

创建集群之前，你需要先了解下Kubernetes中的Node CIDR、Pod CIDR、Service CIDR等基本概念，[点击查看](uk8s/network)


### 一、集群授权

如果你是初次使用UK8S服务，你需要先对UK8S服务授权，详情请查看[授权给UK8S](uk8s/userguide/before_start)

![](/images/userguide/oauth.png)


### 二、配置集群网络信息

Pod与Node同处于一个VPC 子网下，因此VPC子网的网段大小决定了集群可创建的Pod数量上限，详情请查看[Kubernetes网络](uk8s/network)
![](/images/userguide/clusternet.png)

### 三、选择集群节点（云主机）配置

Master默认三个节点，生产环境的Master配置建议可查看[集群节点配置推荐](uk8s/introduction/node_requirements)，在具有多个可用区的地域可以选择讲k8s集群部署在多个可用区中，需要Master分布于多个可用区，如Master处于单个可用区则不支持多可用区模式集群创建。

![](/images/userguide/master.png)

Node节点的可用区选择会根据Master的可用区选择变化，现已支持针对节点的CPU平台、硬件隔离组、最大Pod数、标签等设置。

![](/images/userguide/node2.png)

> Node节点的数据盘会mount到节点的`/data`目录，集群Node安装Docker引擎时安装在`/data`目录下，如创建时Node节点配置使用了数据盘，手动删除数据盘会导致Node节点不可用，如不需要数据盘可以在创建选择时删除，Docker引擎会安装到系统盘的`/data`目录下

### 四、填写管理信息

在管理设置中我们进行以下设置
* 开启APIServer创建外网访问
* K8S版本选择
* kube-proxy查看[kube-proxy模式选择](uk8s/introduction/kubeproxy_mode)
* 集群的所有节点的密码设置，集群中所有节点都可以在云主机页面查看到，你可以使用密码登陆这些节点进行管理。

![](/images/userguide/manager.png)


### 五、创建完毕

集群初始化时间在5分钟左右，创建成功后，你可以通过直接登录Master节点访问和管理集群，也可以在同VPC下的云主机上通过APIServer管理集群。
![](/images/userguide/done.png)