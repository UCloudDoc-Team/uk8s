# UK8S 核心组件故障恢复

## 1. APIServer、Controller Manager、Scheduler 组件的故障恢复

APIServer、Controller Manager、Scheduler 是 Kubernetes 的核心管理组件，在 UK8S 集群中，默认配置三台 Master 节点，每台 Master
节点上均部署安装了这些核心组件，各个组件通过负载均衡对外提供服务，确保集群的高可用。

当某个组件出现故障时，请逐台登录三台 Master 节点，通过 `systemctl status ${PLUGIN_NAME}` 确认组件状态，如组件不可用，可通过以下步骤进行恢复：

```bash
# 将一台健康 Master 节点的内网 IP 配置为环境变量，便于从健康节点拷贝相关文件
export IP=10.23.17.200

# 从健康节点拷贝 APIServer、Controller Manager、Scheduler 组件二进制安装包
## 1.16 及以下 UK8S 版本，K8S 组件统一安装在 hyperkube 文件中
scp root@IP:/usr/local/bin/hyperkube /usr/local/bin/hyperkube
## 1.17 及以后 UK8S 版本，K8S 组件以独立二进制文件形式安装
scp root@IP:/usr/local/bin/{kube-apiserver,kube-controller-manager,kube-scheduler} /usr/local/bin/

# 拷贝 APIServer、Controller Manager、Scheduler 组件服务文件
scp root@IP:/usr/lib/systemd/system/{kube-apiserver.service,kube-controller-manager.service,kube-scheduler.service} /usr/lib/systemd/system/

# 拷贝 APIServer、Controller Manager、Scheduler 组件配置文件
scp root@IP:/etc/kubernetes/{apiserver,controller-manager,kube-scheduler.conf} /etc/kubernetes/

# 拷贝 kubectl 二进制文件
scp root@IP:/usr/local/bin/kubectl /usr/local/bin/kubectl

# 拷贝 kubeconfig
scp -r root@IP:~/.kube ~/

# 修改 APIServer 配置参数
vim /etc/kubernetes/apiserver # 将 advertise-address 参数配置为故障节点 IP

# 启用服务
systemctl enable --now kube-apiserver kube-controller-manager kube-scheduler

# 配置 APIServer 负载均衡器的内外网 IP（仅在开启外网 APIServer 功能情况下需要配置外网 IP）
scp root@IP:/etc/sysconfig/network-scripts/ifcfg-lo:internal /etc/sysconfig/network-scripts/ifcfg-lo:internal
scp root@IP:/etc/sysconfig/network-scripts/ifcfg-lo:external /etc/sysconfig/network-scripts/ifcfg-lo:external
systemctl restart network
```

## 2. Kubelet、Kube-proxy 的故障恢复

Kubelet、Kube-proxy 部署在每个 Master / Node 节点上，分别负责节点注册及流量转发。

> 注：2020.6.12 以前创建的 UK8S 集群中，Master 节点上默认不安装 Kubelet，不能通过 `kubectl get node` 显示。

```bash
# 将一台健康节点的内网 IP 配置为环境变量，便于从健康节点拷贝相关文件
export IP=10.23.17.200

# 从健康节点拷贝 Kubelet、Kube-proxy 组件二进制安装包
## 1.16 及以下 UK8S 版本，K8S 组件统一安装在 hyperkube 文件中，如在上一环节中已执行过此操作可忽略
scp root@IP:/usr/local/bin/hyperkube /usr/local/bin/hyperkube
## 1.17 及以后 UK8S 版本，K8S 组件以独立二进制文件形式安装
scp root@IP:/usr/local/bin/{kubelet,kube-proxy} /usr/local/bin/

# 准备目录
mkdir -p /opt/cni/net.d
mkdir -p /opt/cni/bin
mkdir -p /var/lib/kubelet

# 配置文件拷贝、服务文件
scp root@$IP:/etc/kubernetes/{kubelet,kubelet.conf,kube-proxy.conf,ucloud} /etc/kubernetes/
scp root@$IP:/usr/lib/systemd/system/{kubelet.service,kube-proxy.service} /usr/lib/systemd/system/
scp root@$IP:/etc/kubernetes/set-conn-reuse-mode.sh /etc/kubernetes/
scp root@$IP:/etc/rsyslog.conf /etc/
scp root@$IP:/opt/cni/bin/{cnivpc,loopback,host-local} /opt/cni/bin/
scp root@$IP:/opt/cni/net.d/10-cnivpc.conf /opt/cni/net.d/

# 修改配置参数
# 修改 --node-ip、--hostname-override 为待修复节点 IP
# 修改 --node-labels 中 topology.kubernetes.io/zone、failure-domain.beta.kubernetes.io/zone 为待修复节点可用区（cn-bj2-02）
# 修改 --node-labels 中 UHostID、node.uk8s.ucloud.cn/resource_id 为待修复节点资源 ID（uhost-xxxxxxxx） 
vim /etc/kubernetes/kubelet

# 禁用swap
swapoff -a

# 启用服务
systemctl enable --now kubelet kube-proxy
```

## 3. 容器引擎的恢复

### 3.1 Docker 容器引擎

```bash
# 将一台健康 Master 节点的内网 IP 配置为环境变量，便于从健康节点拷贝相关文件
export IP=10.23.17.200

# 准备目录
mkdir -p /data/docker
rm -rf /var/lib/docker
ln -s /data/docker /var/lib/docker

# 安装包下载及安装
wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-19.03.14-3.el7.x86_64.rpm
wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.4.3-3.2.el7.x86_64.rpm
wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-cli-19.03.14-3.el7.x86_64.rpm
yum install *.rpm -y

# 拷贝配置及服务文件
scp root@$IP:/usr/lib/systemd/system/docker.service /usr/lib/systemd/system/
scp root@$IP:/etc/docker/daemon.json /etc/docker/

# 启用服务
systemctl enable --now docker
```

### 3.2 Containerd 容器引擎

```bash
# 将一台健康 Master 节点的内网 IP 配置为环境变量，便于从健康节点拷贝相关文件
export IP=10.23.17.200

# 准备目录
mkdir -p /etc/containerd 
mkdir -p /data/containerd
mkdir -p /data/log/pods
ln -s /data/containerd /var/lib/containerd
ln -s /data/log/pods /var/log/pods

# 安装包下载及安装
wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.4.3-3.2.el7.x86_64.rpm
yum install containerd.io-1.4.3-3.2.el7.x86_64.rpm

# 拷贝配置文件
scp root@$IP:/etc/containerd/{config.toml,containerd.toml} /etc/containerd/
scp root@$IP:/usr/lib/systemd/system/containerd.service /usr/lib/systemd/system/
scp root@$IP:/usr/local/bin/crictl /usr/local/bin/
scp root@$IP:/etc/crictl.yaml /etc/

# 启用服务
systemctl start containerd
```
