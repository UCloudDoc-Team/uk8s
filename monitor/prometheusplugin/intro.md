# 监控中心概述

监控中心是UK8S提供的产品化监控方案，提供基于Prometheus的产品解决方案，涵盖Prometheus集群的全生命周期管理，以及告警规则配置、报警设置等功能，省去了自行搭建监控服务的学习成本及运维成本。

### 实现原理

监控中心基于CoreOS 开源的Prometheus Operator实现，部署在UK8S集群中，包含三大监控模块，分别是Prometheus、Alertmanager、Grafana，高可用模式下，Prometheus及Alertmanager分别部署2个和3个副本，也支持单节点模式。

同时，为了简化监控服务部署的负担，监控中心启动后，会默认安装NodeExporter以抓取Node节点的监控数据，并添加了Scheduler、Controller Manager、etcd、kubelet等Target，零配置即可实现UK8S的健康状态监控。


### 功能一览

|功能点|功能说明|
|-----|-------|
|创建集群|一键创建Prometheus集群|
|销毁集群|销毁已创建的Prometheus集群|
|创建告警规则|创建一条告警规则，即Prometheus Rule|
|删除告警规则|删除Prometheus Rule|
|添加监控目标|添加监控目标，即Target|
|删除监控目标|删除监控目标，不再抓取其监控数据|
|添加接收人|在Alertmanager中配置邮件及微信接受人|









