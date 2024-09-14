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