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
