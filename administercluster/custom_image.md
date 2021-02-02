## 制作自定义镜像

### 一、前言

为了给UK8S集群提供更好的维护性，除了标准镜像外，UK8S的Node节点也支持自定义镜像，但为了提升集群的稳定性，建议使用UK8S的标准镜像来制作自定义镜像。

下面介绍下如何基于标准镜像制作自定义镜像，以及注意事项。

### 二、制作自定义镜像流程


1. 下载工具

下载uk8sctl工具，使用该工具创建一台镜像为UK8S基础镜像的云主机，可以指定镜像类型为centos或ubuntu。

```bash

wget https://github.com/XiaYinchang/uk8sctl/releases/download/v0.2.0/uk8sctl

chmod +x uk8sctl

```

2. 创建云主机

命令行示例如下，更多参数[点击此处查看](https://github.com/XiaYinchang/uk8sctl)

```bash
./uk8sctl create-base-uhost --publickey your-ucloud-public-key --privatekey you-ucloud-private-key --region cn-bj2 --project-id org-test --password your-uhost-password --image-type centos

```

3. 制作自定义镜像

云主机启动后，你可以自行配置系统环境，如安装监控插件、修改内核参数等，配置完毕后，进入到[云主机界面](https://console.ucloud.cn/uhost/uhost),建议关闭云主机并制作自定义镜像。

开始制作后，可进入到[镜像管理界面](https://console.ucloud.cn/uhost/uimage)，查看镜像制作进度，并获取镜像ID。


4. 删除云主机

自定义镜像状态为可用时，自定义镜像制作完毕，可删除通过uk8sctl创建的云主机，避免产生不必要的费用。

### 三、注意事项

UK8S 基础镜像预先配置好了部署Kubernetes的依赖项，如软件、文件目录、内核参数等，在基于UK8S基础镜像制作自定义镜像时，请谨慎修改相关配置，以免基于自定义镜像创建节点时失败。下面简要说明制作自定义镜像过程中的注意事项。

#### 3.1 系统相关

1. 默认禁用了swap，**请勿开启**；
2. 配置了journald参数Storage=persistent，**不建议修修改**；
3. 默认创建了以下目录，**请勿删除或修改**；
 + /etc/kubernetes/ssl
 + /etc/etcd/
 + /etc/docker/
 + /etc/kubelet.d/ 
 + /var/lib/kubelet
 + ~/.kube/
 + /var/lib/etcd/
 + /var/lib/etcd/default.etcd
 + /usr/libexec/kubernetes/kubelet-plugins/volume/exec/ucloud~flexv/
 + /etc/kubernetes/yaml 
4. 加载了ip_conntrack模块，**请勿修改**；

#### 3.2 软件部分
UK8S节点初始化依赖以下软件（部分），**不建议卸载**。
+ iptables
+ ipvsadm
+ socat
+ nfs-utils(用于挂载ufs)
+ conntrack

>> UK8S节点初始化时，会将预先生成的证书、配置文件、二进制文件（kube-proxy、kubelet、scheduler、docker、kubectl等）拷贝到节点，并依次启动。因此在制作自定义镜像时，无需安装K8S相关组件。

