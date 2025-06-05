# 监控相关常见问题


## 1. 无法采集`kube-scheduler`的监控信息

监控组件无法采集到`kube-scheduler`的监控信息，原因可能是prometheus配置了通过https端口(10259)去采集`/metrics`，但是`kube-scheduler`未支持通过https端口暴露`/metrics`接口。

修复方式：依次登录到3台master节点上，修改 /usr/lib/systemd/system/kube-scheduler.service 文件，加上两行参数: `--authentication-kubeconfig` 和 `--authorization-kubeconfig`。
```
[Service]
EnvironmentFile=-/etc/kubernetes/config
ExecStart=/usr/local/bin/kube-scheduler \
            $KUBE_LOGTOSTDERR \
            $KUBE_LOG_LEVEL \
            --config=/etc/kubernetes/kube-scheduler.conf \
            --authentication-kubeconfig=/etc/kubernetes/kubelet.kubeconfig \
            --authorization-kubeconfig=/etc/kubernetes/kubelet.kubeconfig
```

然后执行`systemctl restart kube-scheduler`。

## 2. 监控node-exporter服务OOM如何调整

使用命令查看node-exporter重启原因； 确定字段`status.containerStatuses.lastState.terminated.reason`是否是OOM，如果是OOM，需要调整资源。

```shell
## 其中<pod-name> 换成自己查询到的pod名称； 例如：uk8s-monitor-prometheus-node-exporter-sbncp
$ kubectl -n uk8s-monitor get po <pod-name> -o yaml 
```

调整node-exportor资源情况；命令中的cpu、memory可以修改成自己想要的资源大小；

```shell
$ kubectl -n uk8s-monitor set resources daemonset uk8s-monitor-prometheus-node-exporter  --limits=cpu=500m,memory=1Gi --requests=cpu=250m,memory=512Mi
```

验证是否修改成功，查看daemonset的资源是否被设置为修改后数据。
```shell
$ kubectl -n uk8s-monitor get daemonset uk8s-monitor-prometheus-node-exporter -o yaml 
```

## 3. 监控存储扩容

#### 扩容PVC
通过控制台部署的prometheus使用的块存储，块存储支持在线扩容。使用如下命令查看是否使用块存储：
```shell
$ kubectl -n uk8s-monitor get pvc | grep "prometheus-uk8s-prometheus-0" |grep "csi-udisk"

prometheus-uk8s-prometheus-db-prometheus-uk8s-prometheus-0           Bound    pvc-1584d2af-4f12-476d-abc1-0a4711feca2e   100Gi      RWO            ssd-csi-udisk   9m3s
```

使用如下命令编辑存储大小：
```shell
$ kubectl -n uk8s-monitor edit pvc prometheus-uk8s-prometheus-db-prometheus-uk8s-prometheus-0  
```

接着在 PVC 的配置里修改spec.resources.requests.storage字段，将其调整为更大的值，示例如下：
```yaml
spec:
  resources:
    requests:
      storage: 200Gi  # 把这里改成你想要的大小，要比原来数据大
```

扩容操作完成后，可通过以下命令查看 PVC 的状态，查看status.capacity.storage字段，确认其已更新为新的容量大小。

```shell
$ kubectl -n uk8s-monitor get pvc prometheus-uk8s-prometheus-db-prometheus-uk8s-prometheus-0 -o yaml
```

#### 扩容保留数据大小

如果扩容后想保留更多的数据，请调整prometheus的CR： `uk8s-prometheus` 的参数`retentionSize`。这个参数是Prometheus服务保留数据大小的参数。

执行命令编辑CR：`uk8s-prometheus`
```
kubectl -n uk8s-monitor edit prometheus uk8s-prometheus
```

接着在配置里修改spec.retentionSize字段，将其调整为更大的值，示例如下：
```yaml
spec:
  retentionSize: 150GB
```

#### 检查

⚠️ 检查监控日志，如果监控日志在扩容前已经存在 `no space left on device` 错误，请重启所有promethues的Pod，确保数据恢复。

删除Pod重启，如果有多个，逐一执行命令，等待第一个Pod恢复后，再删除下一个。
```
$ kubectl -n uk8s-monitor delete po prometheus-uk8s-prometheus-0

# 查看监控日志，监控是否启动成功
$ kubectl -n uk8s-monitor logs -f prometheus-uk8s-prometheus-0 

...
msg="Starting Prometheus" version="(version=2.18.2, branch=HEAD, revision=a6600f564e3c483cc820bae6c7a551db701a22b3)"
...
msg="Starting TSDB ..."
....
msg="TSDB started"
...
msg="Loading configuration file" filename=/etc/prometheus/config_out/prometheus.env.yaml
...
msg="Completed loading of configuration file" filename=/etc/prometheus/config_out/prometheus.env.yaml
...
msg="Server is ready to receive web requests."
...
```

最后在监控页面查看监控数据是否正常。

## 3. Prometheus CPU、内存扩容

如果在使用Prometheus过程中，遇到资源受限问题，可以通过如下方式调整资源。

使用命令编辑Prometheus对象`uk8s-prometheus`：

```shell
$ kubectl -n uk8s-monitor edit prometheus uk8s-prometheus
```

接着在配置里修改spec.resources字段，将其调整为更大的值，示例如下：
```yaml
spec:
  resources:
    limits:
      cpu: 1000m      # 调整为自己需要的CPU
      memory: 2048Mi  # 调整为自己需要的内存
    requests:
      cpu: 1000m      # 调整为自己需要的CPU
      memory: 2048Mi  # 调整为自己需要的内存
```

修改后，Prometheus对应Pod会重新启动。启动后查看Pod的资源是否被设置为修改后数据。

```shell
## 其中<pod-name> 换成自己查询到的pod名称； 例如：prometheus-uk8s-prometheus-0
$ kubectl -n uk8s-monitor get po <pod-name> -o yaml 
```

