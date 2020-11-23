# UK8S概览

UK8S是一项基于Kubernetes的容器管理服务，你可以在UK8S上部署、管理、扩展你的容器化应用，而无需关心Kubernetes集群自身的搭建及维护等运维类工作。



## 了解使用UK8S

为了让您更快上手使用，享受UK8S带来的舒适体验，我们进行了以下分类，如果您需要了解如何创建UK8S[操作指南](#操作指南)，如果您需要了解如何操作UK8S集群[控制集群](#控制集群)，如果您遇到了诸如连接外网、调用API报错等常见问题[常见问题](#常见问题)。

### <center>[产品简介](#产品简介) | [操作指南](#操作指南) | [控制集群](#控制集群) | [常见问题](#常见问题) </center>  

## 使用UCloud其他资源

在您了解了UK8S的基础操作以后，在您发布应用时会遇到应用如何拉取镜像[镜像仓库](#镜像仓库)，使用存储资源[存储相关](#存储相关)，使用ULB、EIP[网络相关](#网络相关)，使用UK8S的[应用商店](#应用商店)。

### <center>[镜像仓库](#镜像仓库) | [存储相关](#存储相关) | [网络相关](#网络相关) | [应用商店](#应用商店)  </center>

## 进阶使用UK8S

在您部署一套UK8S发布应用时，您可能还要关心如下几点。如果您需要了解CICD的建立、K8S的权限管理、K8S的亲和性、弹性伸缩等问题可以查看[最佳实践](#最佳实践)

### <center> [日志管理](#日志管理) | [监控管理](#监控管理) | [最佳实践](#最佳实践) </center>  


### 产品简介

本章节针对集群使用、名词解释以及选择推荐给予介绍，如果您需要了解k8s的一些概念可以参考[名词解释](/uk8s/introduction/concept)，如果您已经在考虑创建集群建议阅读[使用须知](/uk8s/introduction/restriction)、[集群节点配置推荐](/uk8s/introduction/node_requirements)。

对于UK8S产品来说，本身不收取服务费用，但你需要为使用UK8S过程中用到的其他云产品付费。详细请见[产品价格](/uk8s/price)

* [产品概念](/uk8s/introduction/whatisuk8s)
* [使用须知](/uk8s/introduction/restriction)
* [名词解释](/uk8s/introduction/concept)
* [漏洞修复记录](/uk8s/introduction/vulnerability/README)
* [集群节点配置推荐](/uk8s/introduction/node_requirements)
* [kube-proxy模式选择](/uk8s/introduction/kubeproxy_mode)
* [产品价格](/uk8s/price)

##### [返回顶部](#UK8S概览)

###  操作指南

集群创建需要注意的几点分别是[使用必读](/uk8s/userguide/before_start)讲解使用UK8S需要赋予的权限、[kube-proxy模式切换](/uk8s/userguide/kubeproxy_edit)kube-proxy的切换等。


* [使用必读](/uk8s/userguide/before_start)
* [创建集群](/uk8s/userguide/createcluster)
* [删除集群](/uk8s/userguide/deletecluster)
* [查看集群](/uk8s/userguide/describecluster)
* [添加节点](/uk8s/userguide/addnode)
* [kube-proxy模式切换](/uk8s/userguide/kubeproxy_edit)

##### [返回顶部](#UK8S概览)

### 控制集群

本章节主要介绍如何使用kubectl（kubernetes客户端工具）以及创建PVC和Service的操作，具体如何使用存储资源和网络资源可看具体章节。

* [kubectl命令行简介](/uk8s/manageviakubectl/intro_of_kubectl)
* [安装及配置kubectl](/uk8s/manageviakubectl/connectviakubectl)
* [使用web kubectl](/uk8s/manageviakubectl/webterminal)
* [创建PVC](/uk8s/manageviakubectl/createpvc)
* [创建Service](/uk8s/manageviakubectl/createservice)

##### [返回顶部](#UK8S概览)

### 常见问题

除了以下常见问题以外，您还可以联系我们的7*24客户服务团队，K8S专家团队提供全年无休的技术支持。

* [集群常见问题](/uk8s/q/cluster)  
* [镜像库常见问题](/uk8s/q/registry) 
* [容器常见问题](/uk8s/q/container) 
* [存储插件问题](/uk8s/q/storage)

##### [返回顶部](#UK8S概览)

### 镜像仓库

镜像库用于存储、分发Docker镜像。UK8S支持支持各类公有及私有镜像库。

* [概述](/uk8s/dockerhub/outline)  
* [UHub产品文档](uhub/README)
* [在UK8S中使用UHub](uk8s/dockerhub/using_uhub_in_uk8s)

##### [返回顶部](#UK8S概览)

### 存储相关

UK8S默认支持使用UCloud提供的UDisk（块存储）、UFS（文件存储）、UFile（对象存储）。

* [Volume介绍](/uk8s/volume/intro)
* [在UK8S中使用UDISK](/uk8s/volume/udisk)
* [在UK8S中使用已有UDISK](/uk8s/volume/statusudisk)
* [在UK8S中使用UFS](/uk8s/volume/ufs)
* [动态PV 使用UFS](/uk8s/volume/dynamic_ufs)
* [在UK8S中使用UFile](/uk8s/volume/ufile)

##### [返回顶部](#UK8S概览)

### 网络相关

UK8S默认支持使用UCloud提供的ULB、EIP等服务，您可以通过ULB暴露您的服务。

* [Service介绍](/uk8s/service/intro)
* [通过内网ULB访问Service](/uk8s/service/internalservice)
* [通过外网ULB访问Service](/uk8s/service/externalservice)
* [使用已有的ULB](/uk8s/service/ulb_designation)
* [ULB参数说明](/uk8s/service/annotations)
* [ULB名称修改的处理方法](/uk8s/service/change_ulb_name)
* [获取真实客户端IP](/uk8s/service/getresourceip)
* [通过ULB暴露Dashboard](/uk8s/service/dashboard)
* [Ingress支持](/uk8s/service/ingress/README)
* [集群网络](/uk8s/network)  
* [网络隔离](/uk8s/networkpolicy)

##### [返回顶部](#UK8S概览)

### 应用商店

UK8S为方便用户快速部署常用的应用组件，提供了应用商店功能，用户可以通过进入UK8S集群查看到应用商店，使用Helm进行安装部署。

* [关于应用商店](/uk8s/helm/abouthelm)
* [安装使用应用商店](/uk8s/helm/init)
* [安装应用](/uk8s/helm/install)
* [管理应用](/uk8s/helm/manager)
<!-- * [一键安装应用](/uk8s/helm/installapp) -->

##### [返回顶部](#UK8S概览)

### 日志管理

UK8S为方便用户使用提供了日志插件功能，同时用户也可以自行部署ELK日志收集。

* [使用ELK自建UK8S日志解决方案](/uk8s/log/elastic_filebeat_kibana_solution)
* [使用UK8S日志插件功能](/uk8s/log/ELKplugin)

##### [返回顶部](#UK8S概览)

### 监控管理

Prometheus是一套开源的系统监控报警框架。UK8S支持使用以下方案进行监控组件部署。

* [什么是Prometheus](/uk8s/monitor/prometheus/intro)
* [核心概念](/uk8s/monitor/prometheus/concept)
* [部署Prometheus](/uk8s/monitor/prometheus/installprometheus)

##### [返回顶部](#UK8S概览)

### 最佳实践

UK8S提供了关于CICD的建立、K8S的权限管理、K8S的亲和性、弹性伸缩等实践操作文档。

* [基于Jenkins的CI/CD实践](/uk8s/bestpractice/cicd)
* [权限管理](/uk8s/bestpractice/authorization/README)
* [亲和性实践](/uk8s/bestpractice/affinity)
* [Kubernetes弹性伸缩](/uk8s/bestpractice/autoscaling/README)

##### [返回顶部](#UK8S概览)