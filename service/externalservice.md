{{indexmenu_n>10}}
## 通过外网ULB访问Service


>  1.除EIP带宽外，ULB相关参数目前均不支持Update，如不确认如何填写，请咨询UCloud 技术支持。2.请勿修改ULB和Vserver的名称和备注，否则会导致Service无法正常更新。3.Kubernetes下LoadBalancer类型的Service，尚不支持多协议，比如TCP、UDP。




外网模式下，ULB支持“报文转发(ULB4)”及“请求代理（ULB7）”两种转发模式，两种模式配置方式大致相同，默认推荐使用ULB4。


###通过外网ULB4暴露服务

> 使用外网ULB4来暴露服务非常简单，如无特别要求，不需要填写任何 annotations。

当前LoadBalancer类型的Service暂不支持UDP，请知悉。

```
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
    # 代表ULB类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "TCP"
    # 表示ULB类型，TCP与UDP等价，表示ULB4；HTTP与HTTPS等价，表示ULB7；TCP为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-bandwidth": "10" 
    # bandwidth下默认为10Mpbs
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-chargetype": "month" 
    # 付费模式，支持month，year，dynamic，默认为month
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-quantity": "1" 
    # 付费时长，默认为1，chargetype为dynimic时无效    
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  selector:
    app: ucloud-nginx-out-tcp-new
---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx-out-tcp
  labels:
    app: ucloud-nginx-out-tcp-new
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
    ports:
    - containerPort: 80
```


### 重要说明

UK8S的cloudprovider 插件做一个大更新，大于等于19.05.3的版本支持多端口，指定ULB-id等功能，你可以通过如下命令查看cloudprovider的版本：

```
[root@10-9-53-181 ~]# /usr/local/bin/cloudprovider-ucloud version
CloudProvider-UCloud Version:	cloudprovider-19.05.3
Go Version:			go version go1.12.5 linux/amd64
Build Time:			2019-05-30-UTC/06:18:06
Git Commit ID:			2723d13b69a4d6f5b905a7f96bd7eed49617f439

```

升级指南即将发布，如有需求，请联系UCloud技术支持。

### 通过外网ULB7暴露服务(cloudprovider-ucloud version<19.05.3)

老版本的ULB7只支持单种协议，即HTTP或HTTPS。 下文示例中，对外暴露2个端口,都使用HTTP协议。

```

apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
    # 代表ULB类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-listentype": "requestproxy"
    # 代表监听器的类型为请求代理，必须填写。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "HTTP"
    # 表示Verser的协议类型，此处为HTTP，则所有的service端口对应的Vserver protocol 都为HTTP，反之亦然。

spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      name: http
    - protocol: TCP
      port: 443
      targetPort: 80
      name: httptoo
  selector:
    app: ucloud-nginx-out-tcp-new
---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx-out-tcp
  labels:
    app: ucloud-nginx-out-tcp-new
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
    ports:
    - containerPort: 80
```


### 通过外网ULB7暴露服务(cloudprovider-ucloud version>=19.05.3)


19.05.3以后的插件，外网ULB7同时支持HTTP和HTTPS两种协议，下文示例中，对外暴露了三个端口，其中80端口使用HTTP协议，443和8443使用HTTPS协议。

```

apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
    # 代表ULB类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-listentype": "requestproxy"
    # 代表监听器的类型为请求代理，5月30日后安装的集群无需填写。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "HTTPS"
    # 表示ULB类型，HTTP与HTTPS等价，表示ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert": "ssl-b103etqy"
    # 声明要绑定的SSL证书Id，需要先将证书上传至UCloud；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port": "443,8443"
    # 声明使用SSL协议的Service端口，多个用","分隔；
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 443
      targetPort: 80
      name: https
    - protocol: TCP
      port: 8443
      targetPort: 80
      name: ssl
    - protocol: TCP
      port: 80
      targetPort: 80
      name: http
  selector:
    app: ucloud-nginx-out-tcp-new
---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx-out-tcp
  labels:
    app: ucloud-nginx-out-tcp-new
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
    ports:
    - containerPort: 80
</code>

### HTTPS支持(cloudprovider-ucloud version<19.05.3)

小于19.05.3版本的插件，所有service端口只能是HTTP或HTTPS，不能混合使用。

<code yaml>

apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
    # 代表ULB类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-listentype": "requestproxy"
    # 代表监听器的类型为请求代理，插件版本小于19.05.3的版本必须填写。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "HTTPS"
    # 表示Verser的协议类型，此处为HTTPS，则所有的service端口对应的Vserver protocol 都为HTTPS，反之亦然。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert": "ssl-b103etqy"
    # 声明要绑定的SSL证书Id，需要先将证书上传至UCloud；
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 443
      targetPort: 80
      name: https
    - protocol: TCP
      port: 80
      targetPort: 80
      name: httpstoo
  selector:
    app: ucloud-nginx-out-tcp-new
---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx-out-tcp
  labels:
    app: ucloud-nginx-out-tcp-new
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
    ports:
    - containerPort: 80
```


### HTTPS支持(cloudprovider-ucloud version>=19.05.3)

外网ULB支持HTTPS协议。用户通过service.metadata.annotations中的service.beta.kubernetes.io/ucloud-load-balancer-ssl-cert来指定已经上传的TLS证书ID。

通过service.metadata.annotations中的service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port来指定HTTPS服务端口，如有多端口，用","分隔。

如果某个ServicePort 被指定为HTTPS服务端口，并且已提交TLS证书ID，则该ServicePort所对应的VServer协议为HTTPS。

使用ULB7的HTTPS协议模式时，Pod内的服务程序不需要实现HTTPS协议服务，只需要提供HTTP服务即可，ULB7发往后端的报文为解密后的HTTP协议报文。


```

apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
    # 代表ULB类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "HTTP"
    # 表示ULB类型，HTTP与HTTPS等价，表示ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert": "ssl-b103etqy"
    # 声明要绑定的SSL证书Id，需要先将证书上传至UCloud；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port": "443"
    # 声明使用SSL协议的Service端口，多个用","分隔；
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 443
      targetPort: 80
  selector:
    app: ucloud-nginx-out-tcp-new
---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx-out-tcp
  labels:
    app: ucloud-nginx-out-tcp-new
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
    ports:
    - containerPort: 80
```

### 常见问题

#### 1. 如何区别使用ULB4还是ULB7？

通过service.metadata.annotations中的service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol值来声明使用ULB4还是ULB7。

如果值为TCP或者UDP则使用ULB4。

如果是HTTP或者HTTPS，则使用ULB7。

#### 2. 一个LoadBalancer的Service是否支持多端口？

支持，UK8S会为service.spec.ports下每个ServicePort分别创建一个VServer，VServer端口为Service端口。

#### 3. 是否支持多协议？

目前UK8S同时支持HTTP和HTTPS协议。

#### 4. UK8S的LoadBalancer类型的Service是否支持UDP？

目前暂不支持，后续计划支持。

#### 5. 如果Loadbalancer创建外网ULB后，用户在ULB控制台页面绑定了新的EIP，会会被删除吗？

只有访问SVC的ExternalIP才能把流量导入后端Pod，访问其他EIP无效。删除SVC时，所有EIP都会被删除。

