# 自定义数据及初始化脚本

## 自定义数据

自定义数据是指主机初次启动或每次启动时，系统自动运行的配置脚本，该脚本可由控制台/API等传入元
数据服务器，并由主机内的cloud-init程序获取，脚本遵循标准CloudInit语法。该脚本会阻塞UK8S的安装脚本，即只有该脚本执行完毕后，才会开始K8S相关组件的安装，如Kubelet、Scheduler等。

## 初始化脚本

该脚本只在UK8S启动后执行一次，且是在K8S相关组件安装成功后执行。遵循标准shell语法， 执行结果会存入到/var/log/message/目录下。

用户可以通过自定义数据和初始化脚本在创建时对集群进行自定义安装自有服务，比如内核修改、磁盘监控等。详细[使用方法](https://docs.ucloud.cn/uhost/guide/metadata/userdata)

![](../images/administercluster/cloud_init.png)

## 注意事项

使用初始化脚本修改 `/etc/sysctl.conf` 时，请勿修改以下参数，会影响创建的集群正常使用。

```
net.ipv4.ip_local_port_range = 12000 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.conf.eth0.proxy_arp = 1
net.ipv4.ip_forward = 1
vm.max_map_count = 262144
net.netfilter.nf_conntrack_max = 1048576
kernel.unknown_nmi_panic = 0
kernel.sysrq = 1
fs.file-max = 1000000
vm.swappiness = 10
fs.inotify.max_user_watches = 10000000
net.core.wmem_max = 327679
net.core.rmem_max = 327679
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
fs.inotify.max_queued_events = 327679
kernel.shmmax = 68719476736
kernel.shmall = 4294967296
net.ipv4.neigh.default.gc_thresh1 = 2048
net.ipv4.neigh.default.gc_thresh2 = 4096
net.ipv4.neigh.default.gc_thresh3 = 8192
net.ipv6.conf.all.disable_ipv6 = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.conf.all.arp_ignore = 0
net.netfilter.nf_conntrack_tcp_timeout_syn_sent = 6
kernel.pid_max = 1024000
net.ipv4.ip_local_port_range = 12000 65535
net.ipv4.tcp_tw_reuse = 1
```
