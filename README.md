# 概览

* [新手引导](/uk8s/readme2)
* 产品简介
    * [产品概念](/uk8s/introduction/whatisuk8s)
    * [使用须知](/uk8s/introduction/restriction)
    * [名词解释](/uk8s/introduction/concept)
    * [漏洞修复记录](/uk8s/introduction/vulnerability/README)
    * [集群节点配置推荐](/uk8s/introduction/node_requirements)
* 操作指南
    * [使用必读](/uk8s/userguide/before_start)
    * [创建集群](/uk8s/userguide/createcluster)
    * [删除集群](/uk8s/userguide/deletecluster)
    * [查看集群](/uk8s/userguide/describecluster)
    * [添加节点](/uk8s/userguide/addnode)
    * kube-proxy 相关
        * [kube-proxy模式选择](/uk8s/userguide/kubeproxy_mode)
        * [kube-proxy模式切换](/uk8s/userguide/kubeproxy_edit)
    * [Docker VS Containerd](/uk8s/userguide/docker_vs_containerd)    
* 集群管理
    * 通过 Kubectl 管理集群
        * [kubectl命令行简介](/uk8s/manageviakubectl/intro_of_kubectl)
        * [安装及配置kubectl](/uk8s/manageviakubectl/connectviakubectl)
        * [使用web kubectl](/uk8s/manageviakubectl/webterminal)
        * [集群更新凭证](/uk8s/manageviakubectl/reset_token)
        * [创建PVC](/uk8s/manageviakubectl/createpvc)
        * [创建Service](/uk8s/manageviakubectl/createservice)
        * [StatefulSet示例](/uk8s/manageviakubectl/sts_example)
    * [集群版本升级](/uk8s/administercluster/cluster_version_update)
    * [Virtual Kubelet 虚拟节点](/uk8s/administercluster/virtual_kubelet)
    * Kubernetes弹性伸缩
        * [概述](/uk8s/administercluster/autoscaling/intro)
        * [弹性伸缩（HPA）](/uk8s/administercluster/autoscaling/hpa)
        * [定时伸缩（CronHPA）](/uk8s/administercluster/autoscaling/cronhpa)
        * [集群伸缩（CA）](/uk8s/administercluster/autoscaling/ca)    
    * [配置自定义DNS服务](/uk8s/administercluster/custom_dns_service)      
    * [ETCD备份](/uk8s/administercluster/etcd_backup)    
    * [制作自定义镜像](/uk8s/administercluster/custom_image)
    * [自定义数据及初始化脚本](/uk8s/administercluster/cloud_init)
    * [GPU共享插件](/uk8s/administercluster/gpu-share)
* 集群网络
    * [集群网络](/uk8s/network/uk8s_network)
    * [网络隔离](/uk8s/network/networkpolicy)
    * [固定 IP 使用方法](/uk8s/network/static_ip)
    * [CNI 网络插件升级](/uk8s/network/cni_update)    
* 集群存储
    * [Volume 介绍](/uk8s/volume/intro)
    * [在UK8S中使用UDISK](/uk8s/volume/udisk)
    * [UDisk 动态扩容](/uk8s/volume/expandvolume)
    <!-- * [在UK8S中使用已有UDISK](/uk8s/volume/statusudisk) -->
    * [在UK8S中使用UFS](/uk8s/volume/ufs)
    <!-- * [动态PV使用UFS](/uk8s/volume/dynamic_ufs)-->
    * [在UK8S中使用US3](/uk8s/volume/ufile)
    * [CSI 存储插件升级](/uk8s/volume/CSI_update)
    * [Flexvolume 升级 CSI](/uk8s/volume/flexv_csi)
* 服务发现
    * [Service 介绍](/uk8s/service/intro)
    * [通过内网ULB访问Service](/uk8s/service/internalservice)
    * [通过外网ULB访问Service](/uk8s/service/externalservice)
    * [使用已有的ULB](/uk8s/service/ulb_designation)
    * [ULB参数说明](/uk8s/service/annotations)
    * [ULB属性修改的处理方法](/uk8s/service/change_ulb_name)
    * [获取真实客户端IP](/uk8s/service/getresourceip)
    * [通过ULB暴露Dashboard](/uk8s/service/dashboard)
    * [CloudProvider插件升级](/uk8s/service/cp_update)
    * [Ingress支持](/uk8s/service/ingress/README)
* 日志监控方案
    * [使用ELK自建UK8S日志解决方案](/uk8s/log/elastic_filebeat_kibana_solution)
    * [使用UK8S日志插件功能](/uk8s/log/ELKplugin)
    * [Prometheus监控方案](/uk8s/monitor/prometheus/README)
    * 监控中心操作指南
        * [概述](/uk8s/monitor/prometheusplugin/intro.md)
        * [开启监控](/uk8s/monitor/prometheusplugin/startmonitor.md)
        * [添加告警目标](/uk8s/monitor/prometheusplugin/addmonitortarget.md)
        * [添加接收人](/uk8s/monitor/prometheusplugin/addreceiver.md)
* 镜像仓库
    * [概述](/uk8s/dockerhub/outline)  
    * [在UK8S中使用UHub](/uk8s/dockerhub/using_uhub_in_uk8s)   
* 常见问题及排障指南
    * [入门必读](/uk8s/troubleshooting/startguide)
    * [UK8S 集群常见问题](/uk8s/troubleshooting/k8s_debug_summary)
    <!--* [集群常见问题](/uk8s/q/cluster)-->  
    * [Pod 常见故障处理](/uk8s/troubleshooting/pod_debug_summary)
        <!--* [概述](/uk8s/troubleshooting/pod_debug_summary)-->
    * [Node 常见故障处理](/uk8s/troubleshooting/node_debug_summary)
        <!--* [概述](/uk8s/troubleshooting/node_debug_summary)
        * [预防OOM](/uk8s/troubleshooting/prevent_oom)-->
    * [存储常见问题](/uk8s/q/storage)
    * [镜像及镜像仓库常见问题](/uk8s/q/registry) 
    <!--* [容器常见问题](/uk8s/q/container) -->
    * [集群ULB误删处理](/uk8s/troubleshooting/ulb_undelete)
* 最佳实践
* 最佳实践
    * [API Server 审计功能](/uk8s/bestpractice/apiserver_audit)
    * CI/CD 实践
        * [Docker & Jenkins](/uk8s/bestpractice/cicd)
        * [Kaniko & Jenkins](/uk8s/bestpractice/cicd_containerd)
    * [RBAC 权限管理实践](/uk8s/bestpractice/rbac_practice)
    * [亲和性实践](/uk8s/bestpractice/affinity)
* [产品价格](/uk8s/price)

<!--* 应用商店
    * [关于应用商店](/uk8s/helm/abouthelm)
    * [安装使用应用商店](/uk8s/helm/init)
    * [安装应用](/uk8s/helm/install)
    * [管理应用](/uk8s/helm/manager)
     * [一键安装应用](/uk8s/helm/installapp) -->
     