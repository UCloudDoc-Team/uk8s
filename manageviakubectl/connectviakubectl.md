### 安装及配置kubectl

{{indexmenu_n>2}}

本文主要演示如何在UCloud云主机上安装配置kubectl并管理Kubernetes集群，集群Master节点已默认安装kubectl工具，如果你仅需在Master节点做一些简单测试，请跳过此环节；

**云主机环境**

操作系统：linux，windows请移步\[官方文档\](<https://kubernetes.io/docs/tasks/tools/install-kubectl/>)。

所属VPC：与集群同VPC

开通外网：是

\#\#\#一、安装kubectl

1.下载安装包，我们下载V1.13.5的kubectl安装包，其他版本请前往\[官网下载\](<https://kubernetes.io/docs/setup/release/notes/>)。

\`\`\` curl -LO
<https://storage.googleapis.com/kubernetes-release/release/v1.13.5/bin/linux/amd64/kubectl>

\`\`\` 如果您要下载最新版本的安装包，使用如下命令即可： 仅需将v1.13.5替换为$(curl -s
<https://storage.googleapis.com/kubernetes-release/release/stable.txt)即可>。
\`\`\` curl -LO
<https://storage.googleapis.com/kubernetes-release/release/$(curl> -s
<https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl>

\`\`\`

2.添加执行权限 \`\`\` chmod +x ./kubectl

\`\`\` 3.移至工作路径

\`\`\` sudo mv ./kubectl /usr/local/bin/kubectl

\`\`\` 4.输入kubectl version，发现已经安装成功。 \`\`\` \#kubectl version Client
Version: version.Info{Major:"1", Minor:"11", GitVersion:"v1.11.0",
GitCommit:"91e7b4fd31fcd3d5f436da26c980becec37ceefe",
GitTreeState:"clean", BuildDate:"2018-06-27T20:17:28Z",
GoVersion:"go1.10.2", Compiler:"gc",
[Platform:"linux/amd64](Platform:%22linux/amd64)"}

\`\`\`
**备注**：如果您需要在ubuntu或其他linux发行版安装kubectl，亦或使用yum安装，可以参见\[官方文档\](<https://kubernetes.io/docs/tasks/tools/install-kubectl/>)。

\#\#\#二、获取并配置集群凭证

你可以通过UK8S Console、SCP、API三种途径获取您创建的集群凭证。

备注：集群内访问无需凭证，可直接访问。

**1、通过Console获取集群凭证**

点击进入到\<集群详情页\>，点击“集群凭证”
![](/images/compute/uk8s/manageviakubectl/kubeconfig.png)

将集群信息复制保存到\~/.kube/config文件下即可
![](/images/compute/uk8s/manageviakubectl/kubeconfig2.png)

**2、通过SCP从Master节点下载集群凭证到本地**

首先点击进入集群详情页面，获取任意一台Master节点的IP，然后在本地机器执行以下命令：

``` shell
scp root@YOURMASTERIP:~/.kube/config ~/.kube/config
```

\#\#\#三、访问集群 你可以执行以下命令来验证kubectl是否可以成功访问集群信息；

    # kubectl cluster-info

\#\#\#四、设置命令自动补全

在kubectl所在节点执行安装 \`\`\` yum install bash-completion -y \`\`\`
kubectl支持命令自动补全，执行以下命令即可开启。 \`\`\` echo "source \<(kubectl
completion bash)" \>\> \~/.bashrc

\`\`\`
