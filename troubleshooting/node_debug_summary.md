# Node 常见故障处理

节点作为承载工作负载的实体，是 Kubernetes 一个非常重要的对象，在实际运营过程中，节点会出现各种问题，本文简要描述下节点的各种异常状态及排查思路。

## 1. 节点状态说明

| 节点情况               | 说明                                        | 处理办法 |
| ------------------ | ----------------------------------------- | ---- |
| Ready              | True 表示节点是健康的，False 表示节点不健康，Unkown 表示节点失联 |      |
| DiskPressure       | True 表示节点磁盘容量紧张，False 反之                  |      |
| MemoryPressure     | True 表示节点内存使用率过高，False 反之                 |      |
| PIDPressure        | True 表示节点有太多进程在运行，False 反之                |      |
| NetworkUnavailable | True 表示节点网络配置不正常，False 反之                 |      |

## 2. 节点常用命令

1. 查看节点状态

```bash
kubectl get nodes
```

2. 查看节点事件

```bash
kubectl describe node ${NODE_NAME}
```

在上述两个命令看不出端倪的时候，还可以借助Linux的相关命令来辅助判断，这个时候我们就需要登录节点，通过linux相关命令来检查节点状态。

3. 检查节点联通性

   3.1 网络检查： 我们可以从集群的Master节点，使用 **Ping** 命令去检查该节点的网络是否可达； 3.2 健康检查：
   登录UCloud控制台，从云主机页面查看该节点是否处于Running状态，包括查看CPU、内存使用率，确认节点是否处于高负载；

## 3. K8S 组件故障检查

UK8S 集群默认为 3 台 Master 节点，K8S 核心组件在 3 台 Master 节点均有部署，通过负载均衡对外提供服务。如发现组件异常，请登录相应的 Master 节点（无法定位时逐台登录
Master 节点），并通过以下命令来查看节点中组件状态是否正常、错误原因是什么，及对异常组件进行重启：

```bash
systemctl status ${PLUGIN_NAME}
journalctl -u ${PLUGIN_NAME}
systemctl restart ${PLUGIN_NAME}
```

UK8S 核心组件及名称：

| 组件                 | 组件名称                    |
| ------------------ | ----------------------- |
| Kubelet            | kubelet                 |
| API Server         | kube-apiserver          |
| Controller Manager | kube-controller-manager |
| Etcd               | etcd                    |
| Scheduler          | kube-scheduler          |
| KubeProxy          | kube-proxy              |

例如，查看 APIServer 组件状态，需要执行 `systemctl status kube-apiserver`。

## 4. UK8S 页面概览页一直刷新不出来？

1. api-server 对应的 ulb4 是否被删除（`uk8s-xxxxxx-master-ulb4`）
2. UK8S 集群的三台 master 主机是否被删了或者关机等
3. 登陆到 UK8S 三台 master 节点，检查 etcd 和 kube-apiserver 服务是否正常，如果异常，尝试重启服务

- 3.1 `systemctl status etcd`  / `systemctl restart etcd` 如果单个 etcd 重启失败，请尝试三台节点的 etcd 同时重启
- 3.2 `systemctl status kube-apiserver`  / `systemctl restart kube-apiserver`

## 5. UK8S 节点 NotReady 了怎么办

1. `kubectl describe node node-name` 查看节点 notReady 的原因，也可以直接在 console 页面上查看节点详情。
2. 如果可以登陆节点，`journalctl -u kubelet` 查看 kubelet 的日志， `system status kubelet`查看 kubelet 工作是否正常。
3. 对于节点已经登陆不了的情况，如果希望快速恢复可以在控制台找到对应主机断电重启。
4. 查看主机监控，或登陆主机执行`sar`命令，如果发现磁盘 cpu 和磁盘使用率突然上涨, 且内存使用率也高，一般情况下是内存 oom
   导致的。关于内存占用过高导致节点宕机，由于内存占用过高，磁盘缓存量很少，会导致磁盘读写频繁，进一步增加系统负载，打高cpu的恶性循环
5. 内存 oom 的情况需要客户自查是进程的内存情况，k8s 建议 request 和 limit 设置的值不宜相差过大，如果相差较大，比较容易导致节点宕机。
6. 如果对节点 notready 原因有疑问，请按照[UK8S人工支持](#uk8s-人工支持)联系人工支持
