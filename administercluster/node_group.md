# 节点池

## 概述

UK8S引入了节点池概念，通过该功能可以更方便地对节点进行分组管理。本文档将介绍节点池的创建、管理等功能，帮助您更好地利用节点池功能来管理和优化您的Kubernetes集群。
   
### 默认节点池

创建集群时，所有 Master 节点进入默认节点池(名称为`DefaultNodeGroup`)，Node 节点会根据创建集群时的Node节点配置进入对应的节点池(一行Node节点配置对应一个节点池，比如有一行Node节点配置为O机型8核16G内存，则该配置下所有创建出来的Node均会进入名称为`O8C16GNodeGroup`的节点池)

节点池名称支持重复且创建后允许修改名称；默认节点池唯一，不能修改、删除以及后续增加节点，以下类型节点均不加入任何节点池：

- 所有不选择节点池的主机添加，包括添加新节点及已有主机
- 物理云主机、裸金属云主机等异型云主机   

### 创建节点池

要创建一个节点池，您需要执行以下步骤：      

1. 登录到 UCloud 控制台，并导航到 UK8S 服务。   

![](/images/administercluster/node_group1.png)   

2. 在 Kubernetes 服务页面，选择您要创建节点池的集群。      

![](/images/administercluster/node_group2.png) 

3. 在集群详情页面，选择“节点池”选项卡。

![](/images/administercluster/node_group3.png)

4. 点击“新增节点池”按钮。

5. 在创建节点池页面，填写节点池的名称、节点主机信息、规格等信息。

![](/images/administercluster/node_group4.png)

6. 点击“创建”按钮，等待节点池创建完成。
   
### 管理节点池

一旦节点池创建完成，您可以执行以下操作来管理节点池：

- 节点池增加节点：您可以根据应用程序的负载情况，手动扩容增加节点池节点已满足业务需求   
  - 通过节点池添加节点，只需几步即可完成，不再需要重复选择通用的主机规格
![](/images/administercluster/node_group5.png)
![](/images/administercluster/node_group6.png)
- 节点池详情：通过点击节点池名称或者右侧的详情，您可以看到节点池的详细配置信息以及节点池当前包含的节点信息
![](/images/administercluster/node_group10.png)
- 更新节点池配置：如果您需要更改节点池的配置，可以选择更新配置，需要注意的是地域、VPC不支持修改；修改节点池配置不会对目前节点池下的现有节点进行任何调整，只生效于后续从该节点池新增的节点。
![](/images/administercluster/node_group9.png)
- 删除节点池：如果您不再需要某个节点池，可以选择删除它；删除节点池时请确保该节点池下的所有节点已被移除，若仍有节点存在则不可删除。
  - 目标节点池下有节点时，移除操作为禁止状态
![](/images/administercluster/node_group7.png)
  - 目标节点池下无节点时，移除操作可用	
![](/images/administercluster/node_group8.png)
