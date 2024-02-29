# Containerd 常见问题

## 1. containerd-shim进程泄露

- 目前发现使用docker的k8s集群，有可能会遇到containerd-shim进程泄露，尤其是在频繁创建删除Pod或者Pod频繁重启的情况下。
- 此时甚至有可能导致docker inspect某个容器卡住进一步导致kubelet PLEG timeout 异常。 此时以coredns
  Pod为例，说明如何查看是否存在containerd-shim进程泄露。如下示例，正常情况下，一个containerd-shim进程会有一个实际工作的子进程。子进程消失时，containerd-shim进程会自动退出。如果containerd-shim进程没有子进程，则说明存在进程泄露。

遇到containerd-shim进程泄露的情况，可以按照如下方式进行处理

- 确认泄露的进程id，执行`kill pid`。注意，此时无需加`-9`参数，一般情况下简单的kill就可以处理。
- 确认containerd-shim进程退出后，可以观察docker及kubelet是否恢复正常。
- 注意，由于kubelet此时可能被docker卡住，阻挡了很多操作的执行，当docker恢复后，可能会有大量操作同时执行，导致节点负载瞬时升高，可以在操作前后分别重启一遍kubelet及docker。

```sh
[root@xxxx ~]# docker ps |grep coredns-8f7c8b477-snmpq
ee404991798d   uhub.service.ucloud.cn/uk8s/coredns                        "/coredns -conf /etc…"   4 minutes ago   Up 4 minutes             k8s_coredns_coredns-8f7c8b477-snmpq_kube-system_26da4954-3d8e-4f67-902d-28689c45de37_0
b592e7f9d8f2   uhub.service.ucloud.cn/google_containers/pause-amd64:3.2   "/pause"                 4 minutes ago   Up 4 minutes             k8s_POD_coredns-8f7c8b477-snmpq_kube-system_26da4954-3d8e-4f67-902d-28689c45de37_0
[root@xxxx ~]# ps aux |grep ee404991798d
root       10386  0.0  0.2 713108 10628 ?        Sl   11:12   0:00 /usr/bin/containerd-shim-runc-v2 -namespace moby -id ee404991798d70cb9c3c7967a31b3bc2a50e56b072f2febf604004f5a3382ce2 -address /run/containerd/containerd.sock
root       12769  0.0  0.0 112724  2344 pts/0    S+   11:16   0:00 grep --color=auto ee404991798d
[root@xxxx ~]# ps -ef |grep 10386
root       10386       1  0 11:12 ?        00:00:00 /usr/bin/containerd-shim-runc-v2 -namespace moby -id ee404991798d70cb9c3c7967a31b3bc2a50e56b072f2febf604004f5a3382ce2 -address /run/containerd/containerd.sock
root       10421   10386  0 11:12 ?        00:00:00 /coredns -conf /etc/coredns/Corefile
root       12822   12398  0 11:17 pts/0    00:00:00 grep --color=auto 10386
```

## 2. 1.19.5 集群kubelet连接containerd失败

在1.19.5集群中，有可能出现节点not
ready的情况，查看kubelet日志，发现有大量`Error while dialing dial unix:///run/containerd/containerd.sock`相关的日志。这是1.19.5版本中一个已知bug，当遇到containerd重启的情况下，kubelet会失去与containerd的连接，只有重启kublet才能恢复。具体可以查看[k8s官方issue](https://github.com/kubernetes/kubernetes/issues/95727)。\
如果您遇到此问题，重启kubelet即可恢复。同时目前uk8s集群已经不支持创建1.19.5版本的集群，如果您的集群版本为1.19.5，可以通过升级集群的方式，升级到1.19.10。