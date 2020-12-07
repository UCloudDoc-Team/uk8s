
## 通过外网ULB访问Service


### 1、使用提醒
1. 请勿修改由UK8S创建的ULB及Vserver的名称和备注，否则会导致Service异常无法访问。

2. 除外网EIP外，ULB相关参数目前均不支持Update，如不确认如何填写，请咨询UCloud 技术支持。

3. 外网ULB4已支持UDP协议，目前灰度中，如需使用，请联系UCloud技术支持。

### 2、使用UDP协议前必读

1. 目前ULB4针对UDP协议的健康检查支持ping和port两种模式，默认为ping，强烈推荐改为port；


2. port健康检查的后端实现是对UDP端口发送UDP报文( "Health Check" 字符串)和针对RS IP发送ICMP Ping报文。 如果超时时间内回复了UDP报文则认为健康；如果超时时间没收到UDP回包，则以Ping的探测结果为准。因此您的应用程序需要响应UDP健康检查报文。

3. **需要注意的是UDP回包长度不要超过1440，以避免可能的分片导致ULB4无法收到健康检查响应，导致健康检查失败。**


### 3、选择UL4还是ULB7

外网模式下，ULB支持“报文转发(ULB4)”及“请求代理（ULB7）”两种转发模式，推荐使用ULB4，因为ULB4的性能更好；


### 4、操作指南

#### 4.1、通过外网ULB4暴露服务(TCP)

> 使用外网ULB4来暴露服务非常简单，对于TCP协议，可不填写任何 annotations。


```yaml
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
    # 代表ULB网络类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "tcp"
    # 表示ULB协议类型，tcp与udp等价，表示ULB4；http与httpS等价，表示ULB7；tcp为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-bandwidth": "2" 
    # bandwidth下默认为2Mpbs,建议显式声明带宽大小，避免费用超标。
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
      protocol: TCP
```

#### 4.2、通过外网ULB4暴露服务（UDP协议）

相对于TCP应用，务必在annotations中显式声明健康检查的类型为port，否则ULB可能将正常工作的Pod认为不健康，导致流量转发异常。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ucloud-out-udp-new
  labels:
    app: ucloud-out-udp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
    # 代表ULB网络类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "udp"
    # 表示ULB协议类型，tcp与udp等价，表示ULB4；http与httpS等价，表示ULB7；tcp为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"
     # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
spec:
  type: LoadBalancer
  ports:
    - name: udp
      protocol: UDP
      port: 53
      targetPort: 53
  selector:
    app: ucloud-out-udp-new
---
apiVersion: v1
kind: Pod
metadata:
  name: test-out-udp
  labels:
    app: ucloud-out-udp-new
spec:
  containers:
  - name: dns
    image:  uhub.service.ucloud.cn/library/coredns:1.4.0
    ports:
    - name: udp
      containerPort: 53
      protocol: UDP 
```


### 5、重要说明

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
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "http"
    # 表示Verser的协议类型，此处为http，则所有的service端口对应的Vserver protocol 都为http，反之亦然。

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
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "https"
    # 表示ULB协议类型，http与https等价，表示ULB7；
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
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "https"
    # 表示Verser的协议类型，此处为https，则所有的service端口对应的Vserver protocol 都为https，反之亦然。
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
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "http"
    # 表示ULB协议类型，http与https等价，表示ULB7；
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

如果值为tcp或者udp则使用ULB4。

如果是http或者https，则使用ULB7。

#### 2. 一个LoadBalancer的Service是否支持多端口？

支持，UK8S会为service.spec.ports下每个ServicePort分别创建一个VServer，VServer端口为Service端口。

#### 3. 是否支持多协议？

目前UK8S同时支持HTTP和HTTPS协议。

#### 4. UK8S的LoadBalancer类型的Service是否支持UDP？

目前已支持，后续计划支持，灰度中。

#### 5. 如果Loadbalancer创建外网ULB后，用户在ULB控制台页面绑定了新的EIP，会被删除吗？

只有访问SVC的ExternalIP才能把流量导入后端Pod，访问其他EIP无效。删除SVC时，所有EIP都会被删除。

