# 使用UK8S日志插件功能

UK8S 推出了一个新的插件功能，旨在帮助用户快速部署 UK8S 集群所需要的相关插件。

支持UK8S版本：1.14.6 及以后（2019年9月17日之后创建）

ELK 插件安装需要挂载 UDisk，UK8S 支持挂载 UDisk 的地域请查看[链接](uk8s/volume/intro)

## 1. ELK日志插件

**插件-日志ELK**是UK8S基于ELK打造的一站式日志服务，包括Elasticsearch（可选）、Logstash、Filebeat 和 Kibana（可选）多个组件，实现了集群内日志的自动采集、过滤和存储，并内置了日志检索功能。

关于 ELK 组件介绍请参考[ELK日志解决方案](uk8s/log/elastic_filebeat_kibana_solution)

用户进入集群后可以选择为集群安装完整的一套ELK组件或者安装Filebeat等组件关联用户所使用的UES，通过UK8S插件部署的完整ELK组件可以在UCloud页面进行统一化日志查询展示。

![](../images/log/plugin_ELK.png)


## 2. 安装完整ELK日志组件

**Step 1**. 用户在插件页中，点击安装插件进行选择完整安装ELK，在安装过程中用户可以对以下选项进行选择。

![](../images/log/install_ELK.png)

可选项：

* Elasticsearch

这里 Elasticsearch 我们选择新建，将在 UK8S 集群中进行 Elasticsearch 的部署，选择关联则是进行外挂ES（UES）进行关联，这里我们默认进行集群内安装。

* Kibana

用户可以根据自己的需要进行安装 Kibana 的安装，安装后将可以通过应用中查看对外暴露的 Kibana 进行日志查看，提供了 EIP 和 Ingress 两种方式对外暴露，如集群内部没有安装 Ingress Controller 服务的话 Ingress 方式将无法正常提供外部访问。用户可以不进行安装在 UCloud 控制台进行日志查看，这里我们默认选择安装。

> 注意：请确保集群中 Node 节点大于 3 台，单台 Node 节点空余资源大于 4C8G，确保足够资源进行安装ELK服务。

**Step 2**. 点击安装，进入安装页面，可以动过**鼠标悬停**查看安装状态，或者进入**工作负载-应用**中查看安装状态，安装可能将持续10分钟左右。

![](../images/log/installing.png)

**Step 3**. 安装完成后可以在控制台看到日志仪表盘，查看组件健康状态、日志信息统计。

![](../images/log/installed.png)

**Step 4**. 点击日志查询tab页可以进行日志查询，提供了具体的容器选择、时间区间和关键字等检索方式，方便用户进行日志查询。

![](../images/log/logsearch.png)

## 3. 关联UES安装

1. UES是UCloud提供的高可用Elasticsearch集群，使用UK8S关联UES前请创建UES服务，详情请参考[UES操作文档](https://docs.ucloud.cn/ues/README)，这里我们建立好了一个UES集群，在UES集群详情中的节点信息，选择任意一节点，记录节点IP地址。

![](../images/log/UES_list.png)


2. 用户在插件页中，点击安装插件进行选择关联UES安装ELK，在安装过程中用户可以对以下选项进行选择。

![](../images/log/UES_ELK.png)

> 注意：UES需要与UK8S集群属于同一个子网内，用户安装时需要选择具体子网，填写第一步选择节点的IP地址加9200端口号。

3. 安装完成后可以在UK8S中进行集群内部日志查询，UES集群其他日志查询请至UES集群提供的Kibana进行查询。

![](../images/log/installedUES.png)

