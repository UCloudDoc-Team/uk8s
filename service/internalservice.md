
## 通过内网ULB访问Service

### 1、使用提醒


1. **请勿修改由UK8S创建的ULB及Vserver的名称和备注，否则会导致Service异常无法访问。**

2. 除外网EIP外，ULB相关参数目前均不支持Update，如不确认如何填写，请咨询UCloud 技术支持。

3. 内网ULB4已支持UDP协议，目前灰度中，如需使用，请联系UCloud技术支持。

4. 暂不支持内网ULB7。


### 2、使用UDP协议前必读

1. 目前ULB4针对UDP协议的健康检查支持ping和port两种模式，默认为ping，强烈推荐改为port；

2. port健康检查的后端实现是对UDP端口发送UDP报文( "Health Check" 字符串)和针对RS IP发送ICMP Ping报文。 如果超时时间内回复了UDP报文则认为健康；如果超时时间内回复了ICMP端口不可达报文，则认为不健康；如果超时时间没收到UDP回包，则以Ping的探测结果为准。因此您的应用程序需要响应UDP健康检查报文。

3. **需要注意的是UDP回包长度不要超过1440，以避免可能的分片导致ULB4无法收到健康检查响应，导致健康检查失败。**


### 3、操作指南


#### 3.1 TCP应用通过内网ULB4对外暴露

对于TCP协议的服务，只需要在metadata.annotations 指定 load-balancer-type为inner，其他参数都有默认值，可不填写，具体如下：


```yaml
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"  
     # ULB类型，默认为outer，支持outer、inner
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "tcp"       
     # 用于声明ULB协议类型，并非应用的协议。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"
     # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
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

#### 3.2 UDP应用通过内网ULB4对外暴露服务

如果你的应用是UDP协议，或者UDP和TCP混用，则务必显示声明健康检查的类型为port(端口检查)，而非ping。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"  
     # ULB类型，默认为outer，支持outer、inner
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "tcp"       
     # 用于声明ULB的Vserver类型，tcp和udp均代表ULB4，https和http均代表ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"
     # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
spec:
  type: LoadBalancer
  ports:
    - name: udp
      protocol: UDP
      port: 1002
      targetPort: 1002
    - name: tcp
      protocol: TCP
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
