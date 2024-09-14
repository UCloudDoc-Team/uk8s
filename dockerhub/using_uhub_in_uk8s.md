# 在UK8S中使用UHub

本文主要说明如何在UK8S中使用UHub或你自己搭建的私有容器镜像来创建应用。

Kubernetes支持为Pod指定Secret来拉取私有仓库中的镜像，下面我们演示如何使用从UHub中拉取镜像来创建一个Nginx应用；

## 一、生成秘钥Secret

镜像仓库中关于账号与密码的信息是配置在Kuernetes中的Secret资源中，可以创建一个docker-registry类型的Secret保存账号密码；使用以下命令创建Secret，注意将其中的大写字母值替换为你自己的信息；
* `MYSECRET`：Secret资源名称，改为自己定义名称；这里以mysecret为例
* `YOUR_UCLOUD_USERNAME@EMAIL.COM`：镜像仓库登陆账号，可以是控制台账号，也可以是镜像仓库独立账号
* `YOUR_UHUB_PASSWORD`：镜像仓库登陆账号对应的密码

```
# kubectl create secret docker-registry <MYSECRET> \
--docker-server=uhub.service.ucloud.cn \
--docker-username=<YOUR_UCLOUD_USERNAME@EMAIL.COM> \
--docker-password=<YOUR_UHUB_PASSWORD>
```

其中uhub.service.ucloud.cn是UCloud提供的仓库域名，如果自己搭建的仓库，请调整为自己的仓库域名；

## 二、查看生成的秘钥信息

我们看到一个名为mysecret的秘钥已经生成；

```
# kubectl get secret
NAME                  TYPE                                  DATA      AGE
default-token-sfv7s   kubernetes.io/service-account-token   3         8d
mysecret              kubernetes.io/dockerconfigjson        1         3h
```

## 三、在Pod中使用

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
     app: nginx
spec:
  containers:
    - name: nginx
      image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
  imagePullSecrets:
    - name: mysecret  # 这里就是上面创建的Secret名称
```

使用上述的yaml文件创建一个Nginx应用


```
# kubectl create -f pod.yml
```


## 五、查看Pod信息

通知打印的日志，我们可以看到Kubernetes成功地从UHub拉取镜像。

```
# kubectl describe pods/nginx
.....
Events:
  Type    Reason     Age   From                  Message
  ----    ------     ----  ----                  -------
  Normal  Scheduled  1min    default-scheduler     Successfully assigned default/nginx to 10.25.95.46
  Normal  Pulling    1min    kubelet, 10.25.95.46  pulling image "uhub.service.ucloud.cn/ucloud/nginx:1.9.2"
  Normal  Pulled     1min    kubelet, 10.25.95.46  Successfully pulled image "uhub.service.ucloud.cn/ucloud/nginx:1.9.2"
  Normal  Created    1min    kubelet, 10.25.95.46  Created container
  Normal  Started    1min    kubelet, 10.25.95.46  Started container
```
