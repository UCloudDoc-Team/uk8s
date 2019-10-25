
## 创建集群

如果你是初次接触Kubernetes，我们建议你预先创建好一个新的VPC和子网，与生产环境隔离。

创建集群之前，你需要先了解下Kubernetes中的Node CIDR、Pod CIDR、Service CIDR等基本概念，[点击查看](/compute/uk8s/network)


### 一、集群授权

如果你是初次使用UK8S服务，你需要先对UK8S服务授权，详情请查看[授权给UK8S](/compute/uk8s/userguide/before_start)

![](/images/userguide/oauth.png)


### 二、配置集群网络信息

Pod与Node同处于一个VPC 子网下，因此VPC子网的网段大小决定了集群可创建的Pod数量上限，详情请查看[Kubernetes网络](/compute/uk8s/network)
![](/images/userguide/clusternet.png)

### 三、选择集群节点（云主机）配置

Master默认三个节点，生产环境的Master配置建议在4C 8G以上，且磁盘类型必须为SSD，Node节点配置请根据业务需要自行选择。
![](/images/userguide/node.png)

### 四、填写登录密码

集群的所有Node均可在云主机页面查看到，你可以使用此密码登录Master或Node，并直接操作集群，如果你对Kubernetes缺乏足够了解，不建议随意变动。
![](/images/userguide/password.png)

### 五、创建完毕

集群初始化时间在5分钟左右，创建成功后，你可以通过直接登录Master节点访问和管理集群，也可以在同VPC下的云主机上通过ApiServer管理集群。
![](/images/userguide/done.png)