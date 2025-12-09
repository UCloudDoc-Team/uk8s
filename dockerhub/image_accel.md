# 镜像加速

在传统的容器体系中，启动一个容器需要下载并解压其所需的所有镜像数据。当镜像较小时这往往没有问题，但是镜像很大时，会导致容器的启动时间被大大延长。
为了优化使用超大镜像容器的启动速度，我们推出了镜像加速服务，它基于懒加载的模式，可以让容器的启动速度有巨大的优化。在我们的实际测试场景中，**一个25G的镜像在经过加速后，只需要20s即可启动容器。**

![chart](/images/uiac/chart.png)

在使用该功能之前，请先了解相关的技术点：

- 将镜像数据和文件系统索引事先缓存到UFS中。
- 在容器启动时，从UFS中单独加载索引数据。不加载实际数据。此时容器已经可以访问镜像rootfs。
- 容器后续想要读取实际数据时，文件系统才会根据索引中的偏移量从UFS中加载数据。
- 文件系统包含缓存，可以将热点数据缓存在内存中以提高容器访问文件系统的效率。

## 开启镜像加速

#### 提前准备


- 一个UK8S集群。版本必须 >= `1.26`。
- 一个UFS，必须跟UK8S集群在同一个VPC下面，并设置好挂载点。
- 您需要加速镜像的UHub仓库用户名和密码（需要有推送权限）。

**注意：**

> ⚠️ 在使用镜像加速的过程中，切勿更改或删除UFS，不要动里面的任何文件，否则可能会导致容器出现IO错误或节点NotReady！
>
> ⚠️ 开启镜像加速后，历史节点不会自动开启加速。**在给集群开启镜像加速后，新增的节点才能支持镜像加速。**

#### 开启加速

进入UK8S的【应用中心】，找到【容器镜像加速】，点击【立即开启】即可打开镜像加速功能。

![console](/images/uiac/console.png)

开启的时候需要填写用来存镜像数据的UFS信息以及用来推送加速镜像的UHub用户名和密码。


![save](/images/uiac/save.png)

开启之后，我们会在您的集群中安装一些镜像加速的组件，等待一段时间以后可以看到组件进入就绪状态：

![status](/images/uiac/status.png)

#### 状态展示

只有使用了特定containerd插件的节点才支持镜像加速。在控制台的【节点】列表页中，可以在支持镜像加速的节点名称旁边看到特殊的图标：



![node](/images/uiac/node.png)

在k8s中，这些节点还会被打上下面的label，方便后面配置亲和性以确保使用了加速镜像的Pod调度到支持加速的节点上：

```
node.uk8s.ucloud.cn/image_accel: true
```

## 创建加速镜像

我们需要对镜像进行加速之后才能使用，加速的具体步骤是：

- 下载原镜像，转换镜像格式，并缓存到UFS中。
- 创建一个加速镜像，并推送到UHub中。

这里有两个概念：
* 【原镜像】：需要加速的镜像
* 【加速镜像】：加速后的镜像

在实际使用中需要把Pod的镜像替换为【加速镜像】以实现镜像加速的效果。

在【容器镜像加速】界面，可以创建加速任务，以将【原镜像】转换为【加速镜像】，需要填写两个镜像地址。

>⚠️ 在开启镜像加速时填写的UHub用户需要有推送【加速镜像】的权限

![node](/images/uiac/create_task.png)

加速任务创建好了之后，可以查看任务的执行状态，当状态为【就绪】时，就可以使用【加速镜像】了：

![node](/images/uiac/list.png)

## 使用镜像加速

将原镜像替换为加速镜像，即可进行加速，下面是一个示例：

> ⚠️ 需要加速Pod添加节点亲和性以确保Pod被调度到支持加速的节点

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: default
  labels:
    app: test-pod
spec:
  containers:
  - name: test-pod
    image: uhub.service.ucloud.cn/wenqian/nginx:latest-acc
    imagePullPolicy: Always
  restartPolicy: Always
  affinity:
    nodeAffinity:
      # 这里的亲和性是必须加的，否则Pod调度到不支持加速的节点将会无法启动
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: node.uk8s.ucloud.cn/image_accel
            operator: In
            values:
            - "true"
```
