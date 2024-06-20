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
