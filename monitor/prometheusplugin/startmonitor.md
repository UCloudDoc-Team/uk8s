# 开启监控中心

监控中心支持单节点模式和高可用两种模式，需要注意的是，开启监控需要消耗一定的CPU、内存资源，因此，如果开启勾选了高可用模式，请注意：

1. 至少有2个Node节点的可用资源大于Prometheus的容器配置。（建议可用资源大于4C8G）

2. 至少有3个Node节点的可用资源大于Alertmanager的容器配置。（建议可用资源大于1C2G）

3. 由于Prometheus和Alertmanager均需要持久性存储，因此会产生额外的UDisk费用。其中Prometheus为2块100G UDisk，Alertmanager为3块
   UDisk。

### 开启监控

建议参数配置如下：

1. Prometheus 数据盘大小： 100G以上，如果集群规模大于100台，建议磁盘大小扩展到500G；
2. Prometheus 数据保留时长： 建议240小时；
3. Grafana配置： 用户名和密码均可自定义；

![](/images/prometheus/startmonitor.png)

### 监控开启外网

开启外网时通过选择 LB 类型创建 LB 资源或者使用已有资源调用 API 开启外网时，默认使用 CLB7。使用已有资源时，应确保端口没有冲突（监控开启外网会占用80、9090、9093端口）。CLB7 可免费使用，但存在[一定限制](https://cms-docs.ucloudadmin.com/ulb/intro/limit)，推荐使用 ALB，具体可在 [CLB文档](https://cms-docs.ucloudadmin.com/ulb/intro/whatisulb) 和 [ALB文档](https://cms-docs.ucloudadmin.com/ulb/alb/intro/whatisalb) 中查看详情。