## cloudwatch 云监控

cloudwatch 是云平台中产品及资源进行监控的服务，详情[参考](https://docs.ucloud.cn/cloudwatch/README)，uk8s支持cloudwatch。

## 开启 cloudwatch

- 在开启监控界面选择cloudwatch开启，如果没有则需要联系技术支持开通。

![alt text](../images/monitor/cloudwatch/cloudwatch-1.png)

- 大约1分钟之后部署完成如下，表示部署完成，点击对应的按钮跳转到cloudwatch查看对应的监控

![alt text](../images/monitor/cloudwatch/cloudwatch-2.png)

## 指标说明

| 指标名称                         | 指标单位 | 采集频率 | 指标分组 |
| ---------------------------------|----------|----------|----------|
| 集群CPU使用量                    | 核       | 1min     | 集群     |
| 集群CPU使用率                    | %        | 1min     | 集群     |
| 集群内存使用量                   | Mbytes   | 1min     | 集群     |
| 集群内存使用率                   | %        | 1min     | 集群     |
| 集群内存使用量(working set)      | Mbytes   | 1min     | 集群     |
| 集群网络入流量                   | Mbytes   | 1min     | 集群     |
| 集群网络出流量                   | Mbytes   | 1min     | 集群     |
| 集群网络入包量                   | 个/s     | 1min     | 集群     |
| 集群网络出包量                   | 个/s     | 1min     | 集群     |
| 集群磁盘读取次数                 | 次       | 1min     | 集群     |
| 集群磁盘写入次数                 | 次       | 1min     | 集群     |
| 集群 磁盘写入大小                | Mbytes   | 1min     | 集群     |
| 集群 磁盘读取大小                | Mbytes   | 1min     | 集群     |
| 集群 Pod数量                     | 个       | 1min     | 集群     |
| Node数量                         | 个       | 1min     | 集群     |
| 工作负载 CPU 使用量              | 核       | 1min     | 工作负载 |
| 工作负载 CPU 使用率              | %        | 1min     | 工作负载 |
| 工作负载 内存使用量              | Mbytes   | 1min     | 工作负载 |
| 工作负载 内存利用率              | %        | 1min     | 工作负载 |
| 工作负载 内存使用量(working set) | Mbytes   | 1min     | 工作负载 |
| 工作负载 内存使用率(working set) | %        | 1min     | 工作负载 |
| 工作负载 内存使用量(不含cache)   | Mbytes   | 1min     | 工作负载 |
| 工作负载 内存使用率(不含cache)   | %        | 1min     | 工作负载 |
| 工作负载 网络入带宽              | bps      | 1min     | 工作负载 |
| 工作负载 网络出带宽              | bps      | 1min     | 工作负载 |
| 工作负载 网络入流量              | Mbytes   | 1min     | 工作负载 |
| 工作负载 网络出流量              | Mbytes   | 1min     | 工作负载 |
| 工作负载 网络入包量              | 个/s     | 1min     | 工作负载 |
| 工作负载 网络出包量              | 个/s     | 1min     | 工作负载 |
| 工作负载 磁盘读取次数            | 次       | 1min     | 工作负载 |
| 工作负载 磁盘写入次数            | 次       | 1min     | 工作负载 |
| 工作负载 磁盘写入大小            | Mbytes   | 1min     | 工作负载 |
| 工作负载 磁盘读取大小            | Mbytes   | 1min     | 工作负载 |
| 工作负载 Pod数量                 | 个       | 1min     | 工作负载 |
| 工作负载 Pod重启数               | 次       | 1min     | 工作负载 |
| PodCPU 使用量                    | 核       | 1min     | Pod      |
| PodCPU 使用率(占节点)            | %        | 1min     | Pod      |
| PodCPU 使用率(占Request)         | %        | 1min     | Pod      |
| PodCPU 使用率(占limit)           | %        | 1min     | Pod      |
| Pod内存使用量                    | Mbytes   | 1min     | Pod      |
| Pod内存使用率                    | %        | 1min     | Pod      |
| Pod内存使用量(不含cache)         | Mbytes   | 1min     | Pod      |
| Pod内存使用量(working set)       | Mbytes   | 1min     | Pod      |
| Pod内存利用率(working set)       | %        | 1min     | Pod      |
| Pod内存利用率(不含cache)         | %        | 1min     | Pod      |
| Pod网络入带宽                    | bps      | 1min     | Pod      |
| Pod网络出带宽                    | bps      | 1min     | Pod      |
| Pod网络入流量                    | Mbytes   | 1min     | Pod      |
| Pod网络出流量                    | Mbytes   | 1min     | Pod      |
| Pod网络入包量                    | 个/s     | 1min     | Pod      |
| Pod网络出包量                    | 个/s     | 1min     | Pod      |
| Pod磁盘读取次数                  | 次       | 1min     | Pod      |
| Pod磁盘写入次数                  | 次       | 1min     | Pod      |
| Pod磁盘写入大小                  | Mbytes   | 1min     | Pod      |
| Pod磁盘读取大小                  | Mbytes   | 1min     | Pod      |
| Pod重启次数                      | 次       | 1min     | Pod      |
