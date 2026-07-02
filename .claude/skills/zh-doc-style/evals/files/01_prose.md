# CoreDNS 配置说明

> coredns 是 kubernetes 集群默认的dns服务,负责集群内的服务发现.

## 概述

在 uk8s 中,每个pod启动时都会把 coredns 的地址写入 /etc/resolv.conf。如果你的业务对dns解析延迟敏感,建议开启 nodelocaldns 缓存,它能把常见查询的p99延迟从10ms降到1ms左右。

## 修改副本数

默认情况下 coredns 有2个副本,当集群节点超过50个时,建议按每128个节点1个副本的比例扩容。可以通过下面的命令查看当前副本数:

```shell
kubectl -n kube-system get deploy coredns
```

注意:调整副本数后需要观察 apiserver 的负载,避免 coredns 频繁重启导致解析抖动。

## 常见问题

1. 解析超时: 检查 networkpolicy 是否放行了53端口(tcp 和 udp)。
2. 域名不生效: 确认 configmap 中的 Corefile 配置正确,并且重启了对应的pod。
