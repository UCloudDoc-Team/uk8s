
## 关于应用商店

UK8S为方便用户快速部署常用的应用组件，提供了应用商店功能，用户可以通过进入UK8S集群查看到应用商店，使用Helm进行安装部署。
![](/images/helm/shop.png)

### 关于Helm
Helm是Kubernetes的包管理工具，用于简化Kubernetes应用的部署和管理。初期学习理解时可以将Helm比作Linux下的yum/apt-get，这两款软件都是Linux系统下的包管理工具。本文通过安装Helm使用应用商店进行介绍。

### Helm组件及相关术语

Helm2.x是一款C/S架构软件，分为两个部分，分别是Helm的客户端(Helm)和Helm服务端(Tiller)。外部的使用依赖就是Chart仓库。

在Helm3.x中，剔除了Helm服务端(Tiller)，直接使用Helm调用api server完成应用的创建及管理。

#### Helm
Helm是一个命令行下的客户端工具，主要用于Kubernetes应用程序Chart的创建、打包、发布以及管理CHart仓库。

#### Tiller

Tiller在 Helm3 中已经废弃。

Tiller 是 Helm2 的服务端，通常运行在您的kubernetes集群中。Tiller 用于接收 Helm 的请求，并根据 Chart 生成 Kubernetes 的部署文件，然后提交给 Kubernetes 创建应用。

#### Chart
Chart是用来封装 Kubernetes 原生应用程序的一系列 YAML 文件集合。可以在你部署复杂应用的时候直接通过部署chart实现快速部署。


#### Helm工作原理

##### Helm3

HElm3中删除了Tiller，只有客户端使用，调用`~/.kube/config`来访问api server进行创建。

目前Helm3.3版本中完全兼容Helm2中的语法，更新语法会在使用中返回提示。

##### Helm2

<!-- ![](/images/helm/helm.jpg) -->

Helm客户端负责管理已经添加的仓库，即应用商店，发送给Tiller进行具体命令执行。

Tiller服务端负责转化Chart为一条Release，发送给k8s API Server进行部署安装。


