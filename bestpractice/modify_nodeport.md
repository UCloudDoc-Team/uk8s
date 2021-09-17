# NodePort 相关参数修改

## 1. API Server NodePort Range 修改

UK8S 集群中，APIServer 相关参数，保存在 Master 节点 `/etc/kubernetes/apiserver` 文件中，请逐台在 Master 节点上，进行如下操作。

**备份该配置文件**，修改该文件中 `--service-node-port-range` 至需要的参数。

```
KUBE_API_ARGS=" --... \
                --... \
                --service-node-port-range=300000-32767 \
                --... \
                --..."
```

修改完成后，通过 ```systemctl restart kube-apiserver```，重启 APIServer

> ⚠️ 如果集群中的 Service 已经分配了目标 NodePort Range 之外的端口，修改之后通过 `systemctl status kube-apiserver` 查看 APIServer 状态会有类似以下 warning 事件产生，warning 事件不影响该端口使用，如希望避免该 warning，需要重建该 Service。

```bash
# systemctl status kube-apiserver
● kube-apiserver.service - Kubernetes API Server
   Loaded: loaded (/usr/lib/systemd/system/kube-apiserver.service; enabled; vendor preset: disabled)
   Active: active (running) since 四 2021-09-16 15:10:17 CST; 19h ago
     Docs: https://github.com/GoogleCloudPlatform/kubernetes
...
9月 17 10:16:27 10-9-88-175 kube-apiserver[129226]: E0917 10:16:27.623534  129226 repair.go:156] the port 43966 for service uk8s-prometheus/uk8s-monitor is not within the port range 30000-32767; please recreate
9月 17 10:16:27 10-9-88-175 kube-apiserver[129226]: E0917 10:16:27.624596  129226 repair.go:185] the node port 34840 appears to have leaked: cleaning up
9月 17 10:16:27 10-9-88-175 kube-apiserver[129226]: E0917 10:16:27.625663  129226 repair.go:185] the node port 43966 appears to have leaked: cleaning up
9月 17 10:16:27 10-9-88-175 kube-apiserver[129226]: E0917 10:16:27.626740  129226 repair.go:185] the node port 49513 appears to have leaked: cleaning up
9月 17 10:19:27 10-9-88-175 kube-apiserver[129226]: E0917 10:19:27.645040  129226 repair.go:156] the port 34840 for service grafana/uk8s-monitor is not within the port range 30000-32767; please recreate
9月 17 10:19:27 10-9-88-175 kube-apiserver[129226]: E0917 10:19:27.645070  129226 repair.go:156] the port 49513 for service uk8s-alertmanager/uk8s-monitor is not within the port range 30000-32767; please recreate
```

## 2. 修改节点 ip_local_port_range

查看当前系统开放端口范围，命令如下：

```
# cat /proc/sys/net/ipv4/ip_local_port_range 
12000 65535
```

如需修改，请更改 `/etc/sysctl.conf` 文件中 `net.ipv4.ip_local_port_range` 字段

```
net.ipv4.ip_local_port_range = 32768 60999
```

修改完成后，执行 `sysctl -p` 生效配置，并再次验证：

```
# cat /proc/sys/net/ipv4/ip_local_port_range 
32768 60999
```