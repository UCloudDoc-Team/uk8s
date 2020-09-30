
# 安装使用应用商店

本文分别使用Helm的3.3.1和2.14.1版本进行讲解和演示使用。

[Helm3安装](#helm3安装)
[Helm2安装](#helm2安装)

如果您已经安装了Helm的客户端(和服务端)，您可以直接添加应用商店进行使用，添加命令如下：
```
helm repo add ucloud http://helm.ucloud.cn
```

## 先决条件

1. 已创建UK8S集群
2. 已安装配置kubectl连接到kubernetes集群(UK8S master默认安装kubectl)
3. 已配置集群网关

## 版本对应关系

Helm对应支持的k8s版本信息，请遵循k8s版本选择对应的Helm安装

|Helm版本|支持的Kubernetes版本|
|---|---|
|3.3.x|1.18.x - 1.15.x|
|2.14.x|1.14.x - 1.13.x|

## Helm3安装

> 使用此文档请在master节点安装。

1. 下载Helm
```
wget http://k8s.cn-bj.ufileos.com/helm-v3.3.1-linux-amd64.tar.gz
```

2. 解压程序包
```
tar -zxvf helm-v3.3.1-linux-amd64.tar.gz
```

3. 将压缩包中的Helm二进制文件移动到目标位置

```
mv linux-amd64/helm /usr/local/bin/helm
```
4. 执行客户端命令查看是否安装成功

```
helm help
```
### 设置Helm命令的自动补全

为了方便Helm命令的使用，Helm提供了自动补全功能，执行如下命令
```
echo "source <(helm completion bash)" >> ~/.bashrc
```


## Helm2安装

### 安装Helm客户端

1. 下载Helm
```
wget http://helm-releases.cn-bj.ufileos.com/helm-v2.14.1-linux-amd64.tar.gz
```
2. 解压程序包
```
tar -zxvf helm-v2.14.1-linux-amd64.tar.gz
```
3. 将压缩包中的Helm二进制文件移动到目标位置
```
mv linux-amd64/helm /usr/local/bin/helm
```
4. 执行客户端命令查看是否安装成功
```
helm help
```

### 设置Helm命令的自动补全

为了方便Helm命令的使用，Helm提供了自动补全功能，执行如下命令
```
echo "source <(helm completion bash)" >> ~/.bashrc
```

### 安装Tiller服务端

通过Helm客户端进行Tiller安装，Helm会将Tiller安装到kubectl默认情况下连接到的kubernetes集群(kubectl config view)。

1. 安装Tiller服务端
```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/helm/tiller.yaml
```
2. 通过Helm客户端进行关联
```
helm init --upgrade -c --stable-repo-url http://helm.ucloud.cn
```
3. 验证是否安装成功
```
#查看helm安装版本
$ helm version
Client: &version.Version{SemVer:"v2.14.1", GitCommit:"5270352a09c7e8b6e8c9593002a73535276507c0", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.14.1", GitCommit:"5270352a09c7e8b6e8c9593002a73535276507c0", GitTreeState:"clean"}
```

这里我们针对Helm的安装进行了简化，可以研读一下第一步中的tiller.yaml，yaml中我们进行了Tiller的**serviceaccount**和**clusterrolebinding**创建，对Tiller设置了历史版本**200**的限制，设置了存储为**secret**等，如果您希望修改这些参数，可以在第二步中增加参数进行修改。

### 主要使用参数介绍(可以通过helm init --help进行查看)：

```
1. --service-account设置ServiceAccount为tiller。
2. --upgrade如果已经安装了tiller则进行升级。
3. --history-max    helm发布应用会将应用的release存为configmap用于历史查询和回滚等操作，设置记录最大值便于维护，如不对最大历史纪录进行限制，将无限期地保留历史纪录。
4. -i 等同于 --tiller-image 指定Tiller使用镜像，注意Tiller镜像需要和Helm镜像一致。
5. --stable-repo-url 定义初始商店地址。
6. --override 'spec.template.spec.containers[0].command'='{/tiller,--storage=secret}'    helm发布应用会默认存储为configmap，这个参数用于启用secret存储历史纪录，增加了应用发布的安全性。
7. --kube-context 用于安装到kubectl非默认的kubernetes集群，如果你的kubectl配置了多集群，可以使用cat ~/.kube/config |grep current-context 选择你需要安装Tiller的集群，此处没有使用。
8. --tiller-namespace   安装到特定的namespace，此处没有限制，则安装到kube-system。
```