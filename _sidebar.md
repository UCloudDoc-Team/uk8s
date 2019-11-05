* 容器云  UK8S
    * [概览](../overview)
    * 产品简介
        * [产品概念11](../introduction/whatisuk8s.md)
        * [使用须知](../introduction/restriction)
        * [名词解释](compute/uk8s/introduction/concept)
        * 漏洞修复记录
            * [HTTP/2漏洞升级说明](compute/uk8s/introduction/vulnerability/cve2019-9512-9514)
            * [Runc容器逃逸漏洞修复说明](compute/uk8s/introduction/vulnerability/cve-2019-5736)
        * [集群节点配置推荐](compute/uk8s/introduction/node_requirements)
    * [产品价格](compute/uk8s/price)
    * 操作指南
        * [使用必读](compute/uk8s/userguide/before_start)
        * [创建集群](compute/uk8s/userguide/createcluster)
        * [删除集群](compute/uk8s/userguide/deletecluster)
        * [查看集群](compute/uk8s/userguide/describecluster)
        * [添加节点](compute/uk8s/userguide/addnode)
    * 使用kubectl操作集群
        * [kubectl命令行简介](compute/uk8s/manageviakubectl/intro_of_kubectl)
        * [安装及配置kubectl](compute/uk8s/manageviakubectl/connectviakubectl)
        * [使用web kubectl](compute/uk8s/manageviakubectl/webterminal)
        * [创建PVC](compute/uk8s/manageviakubectl/createpvc)
        * [创建Service](compute/uk8s/manageviakubectl/createservice)
    * 存储卷
        * [Volume 介绍](compute/uk8s/volume/intro)
        * [在UK8S中使用UDISK](compute/uk8s/volume/udisk)
        * [在UK8S中使用已有UDISK](compute/uk8s/volume/statusudisk)
        * [在UK8S中使用UFS](compute/uk8s/volume/ufs)
        * [动态PV 使用UFS](compute/uk8s/volume/dynamic_ufs)
    * 服务发现
        * [Service 介绍](compute/uk8s/service/intro)
        * [通过内网ULB访问Service](compute/uk8s/service/internalservice)
        * [通过外网ULB访问Service](compute/uk8s/service/externalservice)
        * [使用已有的ULB](compute/uk8s/service/ulb_designation)
        * [ULB参数说明](compute/uk8s/service/annotations)
        * [获取真实客户端IP](compute/uk8s/service/getresourceip)
        * [通过ULB暴露Dashboard](compute/uk8s/service/dashboard)
        * Ingress支持
            * [Nginx Ingress](compute/uk8s/service/ingress/nginx)
            * [Traefik Ingress](compute/uk8s/service/ingress/traefik)
            * [ingress 高级用法](compute/uk8s/service/ingress/multiple_ingress)
            * [traefik 高级用法](compute/uk8s/service/ingress/traefik_annotation)
    * [集群网络](compute/uk8s/network)  
    * 应用商店
        * [关于应用商店](compute/uk8s/helm/abouthelm)
        * [安装使用应用商店](compute/uk8s/helm/init)
        * [安装应用](compute/uk8s/helm/install)
        * [管理应用](compute/uk8s/helm/manager)
        * [一键安装应用](compute/uk8s/helm/installapp)
    * 日志管理
        * [使用ELK自建UK8S日志解决方案](compute/uk8s/log/elastic_filebeat_kibana_solution)
    * 监控管理
        * Prometheus监控方案
            * [什么是Prometheus](compute/uk8s/monitor/prometheus/intro)
            * [核心概念](compute/uk8s/monitor/prometheus/concept)
            * [部署Prometheus](compute/uk8s/monitor/prometheus/installprometheus)
    * 集群管理
        * [配置自定义DNS服务](compute/uk8s/administercluster/custom_dns_service)  
    * 镜像仓库
        * [概述](compute/uk8s/dockerhub/outline)  
        * [在UK8S中使用UHub](compute/uk8s/dockerhub/using_uhub_in_uk8s)   
    * 常见问题
        * [集群常见问题](compute/uk8s/q/cluster)  
        * [镜像库常见问题](compute/uk8s/q/registry) 
        * [容器常见问题](compute/uk8s/q/container) 
    * API文档
        * [创建集群](compute/uk8s/api/createuk8s)
        * [获取集群列表](compute/uk8s/api/listuk8s)
        * [获取集群信息](compute/uk8s/api/describeuk8s)
        * [删除集群](compute/uk8s/api/deluk8s)
        * [添加云主机节点](compute/uk8s/api/adduhostnode)
        * [添加物理云主机节点](compute/uk8s/api/addphostnode)
        * [删除节点](compute/uk8s/api/delnode)
        * [获取集群kubeconfig](compute/uk8s/api/getconfig) 
    * 最佳实践
        * [基于Jenkins的CI/CD实践](compute/uk8s/bestpractice/cicd)
        * 权限管理
            * [了解RBAC](compute/uk8s/bestpractice/authorization/rbac)
            * [权限管理实践](compute/uk8s/bestpractice/authorization/practice)
        * [亲和性实践](compute/uk8s/bestpractice/affinity)
        * Kubernetes弹性伸缩
            * [概述](compute/uk8s/bestpractice/autoscaling/intro)
            * [HPA](compute/uk8s/bestpractice/autoscaling/hpa)
            * [Cluster Autoscaler](compute/uk8s/bestpractice/autoscaling/ca)
    
        
