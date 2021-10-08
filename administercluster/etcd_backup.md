# ETCD备份

ETCD备份插件是UK8S提供的ETCD数据库备份功能，ETCD备份可以有效的帮助集群进⾏故障恢复操作，可根据插件设置进⾏定时备份、指定存储等功能。

<!-- * 备份操作
* 恢复操作
* 常见问题 -->

## 1. 首次操作

如您是首次安装插件提示您需要保存密钥操作，请在任一master节点上执行以下命令，执行完成后刷新页面即可。

```
kubectl create secret generic uk8s-etcd-backup-cert -n kube-system --from-file /etc/kubernetes/ssl/etcd.pem --from-file /etc/kubernetes/ssl/etcd-key.pem
```

## 2. 备份操作

开启ETCD备份，备份系统会根据创建的设定进行备份数据留存，如下图

![](/images/administercluster/etcd_backup1.png)

1. 选择希望保留的备份数量，备份系统会根据该数字保持存储空间内ETCD备份数量的上限。
2. 添加定时备份时间，这里使用的时间表语法可以参考[CronTab格式](#4-针对计划表语法说明)。
3. 备份介质我们提供了UFile和SSHServer两种介质，这里我们创建的是UFile。
4. 选择UFile需要创建对应的UFile令牌和存储空间，**UFile令牌需要赋予上传、下载、删除、文件列表**。

![](/images/administercluster/etcd_backup1.png)

1. 如使用SSHServer需要填写具体的可以执行SSH的主机，并确保填写的账号拥有该主机目录的读写权限。

## 3. 恢复操作

> ⚠️ ETCD恢复操作，建议您仔细阅读文档后谨慎操作。

当误删除 UK8S 集群 Master 节点时，集群恢复较为麻烦，需要联系 UK8S 技术人员进行支持；对于节点故障而非误删节点的情况，处理起来相对简单一些。下面分别进行说明。

* etcd节点未删除，但节点存在故障
  * [etcd集群仍然可用](#3-1-1-etcd集群仍然可用)
  * [etcd集群不可用](#3-1-2-etcd集群不可用)
* 误删除etcd节点
  * [etcd集群仍然可用](#3-2-1-etcd集群仍然可用)
  * [etcd集群不可用](#3-2-2-etcd集群不可用)

### 3.1 etcd 节点未删除，但节点存在故障

#### 3.1.1 etcd 集群仍然可用

此时，出现故障的 etcd 节点数量小于总数的一半（uk8s 的 etcd 节点数量默认为 3，所以此时出现故障的 etcd 节点数量为 1 ）。这种情况下，不需要借助 etcd 备份即可进行集群恢复，操作步骤如下：

1. 首先对出现故障的节点进行修复，如需重装系统，则建议安装 CentOS 7.6 64 位操作系统或者联系技术支持人员安装 UK8S 定制镜像；
2. 登录到一个健康节点（本例使用节点 10.23.17.200），进行如下操作从 etcd 集群中删除故障节点；
  ```bash
    # 注意后续操作中需要替换相关参数，与你当前集群相匹配
    export ETCDCTL_API=3
    export ETCDCTL_CACERT=/etc/kubernetes/ssl/ca.pem
    export ETCDCTL_CERT=/etc/kubernetes/ssl/etcd.pem
    export ETCDCTL_KEY=/etc/kubernetes/ssl/etcd-key.pem
    # 替换 IP 地址为你的 etcd 集群节点 IP
    export ETCDCTL_ENDPOINTS=10.23.17.200:2379,10.23.207.11:2379,10.23.97.19:2379

    # 执行如下命令查看集群状态
    etcdctl endpoint health
    # 输出如下，可以看到节点 10.23.97.19 处于故障状态
    ...
    10.23.17.200:2379 is healthy: successfully committed proposal: took = 15.028244ms
    10.23.207.11:2379 is healthy: successfully committed proposal: took = 15.712076ms
    10.23.97.19:2379 is unhealthy: failed to commit proposal: context deadline exceeded
    Error: unhealthy cluster

    # 执行以下命令查看节点 ID
    etcdctl member list
    # 输出如下，可以获知故障节点 10.23.97.19 的 ID 为 45b4ced6b6a33ef5
    1d3f61116d4f3128, started, etcd3, https://10.23.207.11:2380, https://10.23.207.11:2379
    45b4ced6b6a33ef5, started, etcd2, https://10.23.97.19:2380, https://10.23.97.19:2379
    8a190c41d92119cb, started, etcd1, https://10.23.17.200:2380, https://10.23.17.200:2379

    # 执行以下命令删除故障节点
    etcdctl member remove 45b4ced6b6a33ef5
  ```
3. 登录到一个健康节点（本例使用节点 10.23.17.200），拷贝文件到已完成修复的故障节点（本例中是 10.23.97.19）；
  ```bash
    # 拷贝 etcd 相关程序
    scp /usr/bin/etcd /usr/bin/etcdctl 10.23.97.19:/usr/bin
    # 拷贝 etcd 配置文件
    scp -r /etc/etcd 10.23.97.19:/etc/etcd
    # 拷贝 kubernetes 配置文件和 etcd 证书
    scp -r /etc/kubernetes 10.23.97.19:/etc/kubernetes
    # 拷贝etcd 服务文件
    scp /usr/lib/systemd/system/etcd.service 10.23.97.19:/usr/lib/systemd/system/etcd.service
  ```
4. 登录到完成修复的故障节点（本例中是 10.23.97.19），修改 etcd 相关配置；
  ```bash
    # 备份原配置文件
    cp /etc/etcd/etcd.conf /etc/etcd/etcd.conf.bak

    # 清空原配置
    echo '' >/etc/etcd/etcd.conf

    # 设置参数
    # 替换为故障节点的 etcd name
    export FAILURE_ETCD_NAME=etcd2
    # 替换为使用的健康节点的 IP
    export NORMAL_ETCD_NODE_IP=10.23.17.200
    # 替换为故障节点的 IP
    export FAILURE_ETCD_NODE_IP=10.23.97.19
    # 执行以下命令生成新配置
    cat /etc/etcd/etcd.conf.bak | while read LINE; do
      if [[ $LINE == "ETCD_INITIAL_CLUSTER="* ]]; then
        echo $LINE >>/etc/etcd/etcd.conf
      elif [[ $LINE == "ETCD_INITIAL_CLUSTER_STATE="* ]]; then
        echo 'ETCD_INITIAL_CLUSTER_STATE="existing"' >>/etc/etcd/etcd.conf
      elif [[ $LINE == "ETCD_NAME="* ]]; then
        echo 'ETCD_NAME='$FAILURE_ETCD_NAME >>/etc/etcd/etcd.conf
      else
        echo $LINE | sed "s/$NORMAL_ETCD_NODE_IP/$FAILURE_ETCD_NODE_IP/g" >>/etc/etcd/etcd.conf
      fi
    done

    # 如有遗留数据则删除旧的 etcd 数据
    rm -rf /var/lib/etcd
    # 新建数据目录
    mkdir -p /var/lib/etcd/default.etcd
  ```
5. 登录到一个健康节点（本例使用节点 10.23.17.200），将故障节点重新加入 etcd 集群；
  ```bash
    # 注意后续操作中需要替换相关参数，与你当前集群相匹配
    export ETCDCTL_API=3
    export ETCDCTL_CACERT=/etc/kubernetes/ssl/ca.pem
    export ETCDCTL_CERT=/etc/kubernetes/ssl/etcd.pem
    export ETCDCTL_KEY=/etc/kubernetes/ssl/etcd-key.pem
    # 替换 IP 地址为你的 etcd 集群节点 IP
    export ETCDCTL_ENDPOINTS=10.23.17.200:2379,10.23.207.11:2379,10.23.97.19:2379
    # 替换为故障节点的 etcd name
    export FAILURE_ETCD_NAME=etcd2
    # 替换为故障节点的 IP
    export FAILURE_ETCD_NODE_IP=10.23.97.19
    # 执行以下命令将故障节点重新加入 etcd 集群
    etcdctl member add $FAILURE_ETCD_NAME --peer-urls=https://$FAILURE_ETCD_NODE_IP:2380
  ```
6. 登录到故障节点，启动 etcd；
  ```bash
    # 执行以下命令启动 etcd， 如无报错则启动成功
    systemctl enable --now etcd
    # 启动成功后，可以参照步骤 2 查看 etcd 集群状态。
  ```
7. 如需继续在该故障节点上恢复运行 kube-apiserver、kube-controller-manager 、kube-scheduler 服务，则需进行如下操作：
  ```bash
    # 从健康节点拷贝 hyperkube
    scp 10.23.17.200:/usr/local/bin/hyperkube /usr/local/bin/hyperkube
    # 拷贝 kube-apiserver、kube-controller-manager 、kube-scheduler 服务文件
    scp 10.23.17.200:/usr/lib/systemd/system/kube-* /usr/lib/systemd/system
    # 拷贝 kubectl
    scp 10.23.17.200:/usr/local/bin/kubectl /usr/local/bin/kubectl
    # 拷贝 kubeconfig
    scp -r 10.23.17.200:~/.kube ~

    # 替换为故障节点的 IP
    export FAILURE_ETCD_NODE_IP=10.23.97.19
    sed -i 's/\(advertise-address=\).*\( \)/\1'$FAILURE_ETCD_NODE_IP'\2/' /etc/kubernetes/apiserver

    # 启用服务
    systemctl enable --now kube-apiserver kube-controller-manager kube-scheduler

    # 配置负载均衡器的内网和外网弹性 IP
    scp 10.23.17.200:/etc/sysconfig/network-scripts/ifcfg-lo:internal /etc/sysconfig/network-scripts/ifcfg-lo:internal
    scp 10.23.17.200:/etc/sysconfig/network-scripts/ifcfg-lo:external /etc/sysconfig/network-scripts/ifcfg-lo:external
    systemctl restart network
  ```

#### 3.1.2 etcd 集群不可用
etcd 集群不可用即有一半及以上的 etcd 节点出现故障。极端情况下，如果所有节点都因故无法正常登入系统，则需联系支持人员尝试从故障节点中恢复出 etcd 和 uk8s 相关的文件或者依据数据库数据重新构建相关文件；这里仅考虑至少有一个 etcd 节点可以正常登入系统的情况，此时可使用 uk8s etcd 备份插件保存的数据进行集群恢复，操作步骤如下：
1. 保留一个可以正常登录的节点不作处理，对其它故障节点进行修复，如需重装系统，则建议安装 CentOS 7.6 64 位操作系统或者联系技术支持人员安装 UK8S 定制镜像；
2. 如果修复故障节点时未造成文件系统数据丢失，则可跳过该步骤，否则应登录到保留节点（本例为节点 10.23.166.234）拷贝文件到已完成修复的故障节点（本例中是 10.23.172.172，10.23.95.6）；
  ```bash
    # 拷贝 etcd 相关程序
    scp /usr/bin/etcd /usr/bin/etcdctl 10.23.172.172:/usr/bin
    scp /usr/bin/etcd /usr/bin/etcdctl 10.23.95.6:/usr/bin
    # 拷贝 etcd 配置文件
    scp -r /etc/etcd 10.23.172.172:/etc/etcd
    scp -r /etc/etcd 10.23.95.6:/etc/etcd
    # 拷贝 kubernetes 配置文件和 etcd 证书
    scp -r /etc/kubernetes 10.23.172.172:/etc/kubernetes
    scp -r /etc/kubernetes 10.23.95.6:/etc/kubernetes
    # 拷贝etcd 服务文件
    scp /usr/lib/systemd/system/etcd.service 10.23.172.172:/usr/lib/systemd/system/etcd.service
    scp /usr/lib/systemd/system/etcd.service 10.23.95.6:/usr/lib/systemd/system/etcd.service
  ```
3. 如果修复故障节点时未造成文件系统数据丢失，则可跳过该步骤，否则应在完成步骤 2 后分别登录到故障节点（本例中是 10.23.172.172，10.23.95.6）修改 etcd 相关配置，以下为其中一个故障节点（本例是10.23.172.172）的操作，其它故障节点应执行相同操作（注意修改参数）；
  ```bash
    # 备份原配置文件
    cp /etc/etcd/etcd.conf /etc/etcd/etcd.conf.bak

    # 清空原配置
    echo '' >/etc/etcd/etcd.conf

    # 设置参数
    # 替换为故障节点的 etcd name，这里 10.23.172.172 对应 etcd2
    export FAILURE_ETCD_NAME=etcd2
    # 替换为保留节点的 IP
    export RETAIN_ETCD_NODE_IP=10.23.166.234
    # 替换为故障节点的 IP
    export FAILURE_ETCD_NODE_IP=10.23.172.172
    # 执行以下命令生成新配置
    cat /etc/etcd/etcd.conf.bak | while read LINE; do
      if [[ $LINE == "ETCD_INITIAL_CLUSTER="* ]]; then
        echo $LINE >>/etc/etcd/etcd.conf
      elif [[ $LINE == "ETCD_NAME="* ]]; then
        echo 'ETCD_NAME='$FAILURE_ETCD_NAME >>/etc/etcd/etcd.conf
      else
        echo $LINE | sed "s/$RETAIN_ETCD_NODE_IP/$FAILURE_ETCD_NODE_IP/g" >>/etc/etcd/etcd.conf
      fi
    done
  ```
4. 在所有 etcd 节点上执行以下命令；
  ```bash
    # 停止 etcd 服务
    systemctl stop etcd
    # 如有遗留数据则删除旧的 etcd 数据
    rm -rf /var/lib/etcd
    # 新建数据目录
    mkdir /var/lib/etcd
  ```
5. 从 UFile 或备份服务器获取 etcd 备份文件并上传至所有 etcd 节点，分别在各节点上执行以下命令从备份文件恢复 etcd 数据（注意参数要匹配节点信息）；
  ```bash
    # 本例备份文件已经保存到 /root/uk8s-f1wymalx-backup-etcd-3.3.17-2020-02-11T03-56-12.db.tar.gz 路径
    # 解压缩获取备份数据
    tar zxvf uk8s-f1wymalx-backup-etcd-3.3.17-2020-02-11T03-56-12.db.tar.gz
    # 从备份数据恢复，注意调整 ETCD_NAME 和 NODE_IP 匹配节点信息
    export ETCD_NAME=etcd2
    export NODE_IP=10.23.172.172
    export ETCDCTL_API=3
    etcdctl --name=$ETCD_NAME --endpoints=https://$NODE_IP:2379 --cert=/etc/kubernetes/ssl/etcd.pem --key=/etc/kubernetes/ssl/etcd-key.pem --cacert=/etc/kubernetes/ssl/ca.pem --initial-cluster-token=etcd-cluster --initial-advertise-peer-urls=https://$NODE_IP:2380 --initial-cluster=etcd1=https://10.23.95.6:2380,etcd2=https://10.23.172.172:2380,etcd3=https://10.23.166.234:2380 --data-dir=/var/lib/etcd/default.etcd/ snapshot restore uk8s-f1wymalx-backup-etcd-3.3.17-2020-02-11T03-56-12.db
  ```
6. 在所有 etcd 节点完成步骤 5 后，在所有 etcd 节点执行以下命令启动 etcd；
  ```bash
    # 注意最开始执行该命令时有可能 hang 住，这是正常现象
    # 继续在其它节点上执行该命令，当超过半数的节点都启动后该命令就会正常退出
    systemctl enable --now etcd
  ```
7. 登录任一 etcd 节点查看集群状态；
  ```bash
    export ETCDCTL_API=3
    export ETCDCTL_CACERT=/etc/kubernetes/ssl/ca.pem
    export ETCDCTL_CERT=/etc/kubernetes/ssl/etcd.pem
    export ETCDCTL_KEY=/etc/kubernetes/ssl/etcd-key.pem
    # 替换 IP 地址为你的 etcd 集群节点 IP
    export ETCDCTL_ENDPOINTS=10.23.95.6:2379,10.23.172.172:2379,10.23.166.234:2379

    # 执行如下命令查看集群状态
    etcdctl endpoint health
  ```
8. 如需继续在故障节点上恢复运行 kube-apiserver、kube-controller-manager 、kube-scheduler 服务，可分别登录修复完成的故障节点进行如下操作：
  ```bash
    # 从保留节点拷贝 hyperkube
    scp 10.23.166.234:/usr/local/bin/hyperkube /usr/local/bin/hyperkube
    # 拷贝 kube-apiserver、kube-controller-manager 、kube-scheduler 服务文件
    scp 10.23.166.234:/usr/lib/systemd/system/kube-* /usr/lib/systemd/system
    # 拷贝 kubectl
    scp 10.23.166.234:/usr/local/bin/kubectl /usr/local/bin/kubectl
    # 拷贝 kubeconfig
    scp -r 10.23.166.234:~/.kube ~

    # 替换为故障节点的 IP
    export FAILURE_ETCD_NODE_IP=10.23.172.172
    sed -i 's/\(advertise-address=\).*\( \)/\1'$FAILURE_ETCD_NODE_IP'\2/' /etc/kubernetes/apiserver

    # 启用服务
    systemctl enable --now kube-apiserver kube-controller-manager kube-scheduler

    # 配置负载均衡器的内网和外网弹性 IP
    scp 10.23.166.234:/etc/sysconfig/network-scripts/ifcfg-lo:internal /etc/sysconfig/network-scripts/ifcfg-lo:internal
    scp 10.23.166.234:/etc/sysconfig/network-scripts/ifcfg-lo:external /etc/sysconfig/network-scripts/ifcfg-lo:external
    systemctl restart network
  ```

### 3.2 误删除etcd节点

#### 3.2.1 etcd 集群仍然可用

此时，误删除的 etcd 节点数量小于总数的一半（uk8s 的 etcd 节点数量默认为 3，所以此时误删的 etcd 节点数量为 1 ），etcd 集群仍然可以正常访问。这种情况下，不需要借助 etcd 备份即可进行集群恢复，操作步骤如下：

1. 联系技术支持人员根据误删除节点的信息创建一个配置和 IP 与被删节点相同的虚拟机；
2. 参照 _**etcd 节点未删除，但节点存在故障**_ 章节下 _**etcd 集群仍然可用**_ 子章节，将步骤 1 中创建的虚拟机作为 _已修复的故障节点_ 进行集群恢复；
3. etcd 集群修复完成后，联系技术支持人员更改数据库中误删除的虚拟机的 UHost ID 为步骤 1 中创建的虚拟机的 UHost ID。

#### 3.2.2 etcd 集群不可用

etcd 集群不可用即有一半及以上的 etcd 节点被删除。极端情况下，如果所有节点都被删除，则需联系支持人员尝试依据数据库数据重新构建相关文件；这里仅考虑至少有一个 etcd 节点可以正常登入系统的情况，此时可使用 uk8s etcd 备份插件保存的数据进行集群恢复，操作步骤如下：

1. 联系技术支持人员根据所有误删除的节点的信息创建配置和 IP 与被删节点一一对应的虚拟机；
2. 参照 _**etcd 节点未删除，但节点存在故障**_ 章节下 _**etcd 集群不可用**_ 子章节，将步骤 1 中创建的虚拟机作为 _已修复的故障节点_ 进行集群恢复；
3. etcd 集群修复完成后，联系技术支持人员更改数据库中误删除的虚拟机的 UHost ID 为步骤 1 中创建的虚拟机的 UHost ID。

## 4. 针对计划表语法说明

针对计划表语法使用和CronTab一致的语法，下面列举几种常用语法，详细语法请参考[链接](https://wiki.archlinux.org/index.php/Cron_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)#Crontab_%E6%A0%BC%E5%BC%8F)

Crontab格式（前5位为时间选项，这里我们只用到了前5位）
```
<分钟> <小时> <日> <月份> <星期> <命令>
```

每天一次，0点0分执行
```
0 0 * * *
```

每周一次，0点0分执行
```
0 0 * * 0
```

每月一次，0点0分执行
```
0 0 1 * *
```
<!-- 

如图，执行时间为UTC时间是因为CronTab的命令时间为UTC时间，方便于用户填写时间命令，实际真实执行时间用户可以进行+8小时计算。

![](/images/bestpractice/autoscaling/createcronhpa.png) -->
