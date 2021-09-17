# 通过内网ULB访问Service

## 1. 使用提醒

1. 请勿修改由UK8S创建的ULB及Vserver的名称和备注，否则会导致Service异常无法访问。

2. 如 ULB 为 UK8S 在创建 Service 时同步创建，删除 Service 时 ULB 会同步删除，请勿将 ULB 关联其他 Vserver，如需多个 Service 共用 ULB，可先创建 ULB，并在创建 Service 时关联已有 ULB，详情请见[使用已有 ULB](/uk8s/service/ulb_designation)。

3. 除外网EIP外，ULB相关参数目前均不支持Update，如不确认如何填写，请咨询UCloud 技术支持。

## 2. 使用UDP协议前必读

1. 目前ULB4针对UDP协议的健康检查支持ping和port两种模式，默认为ping，强烈推荐改为port；

2. port健康检查的后端实现是对UDP端口发送UDP报文( "Health Check" 字符串)和针对RS IP发送ICMP Ping报文。 如果超时时间内回复了UDP报文则认为健康；如果超时时间没收到UDP回包，则以Ping的探测结果为准，因此您的应用程序需要响应UDP健康检查报文。

3. **需要注意的是UDP回包长度不要超过1440，以避免可能的分片导致ULB4无法收到健康检查响应，导致健康检查失败。**

## 3. 操作指南

### 3.1 TCP应用通过内网ULB4对外暴露

对于TCP协议的服务，只需要在metadata.annotations 指定 load-balancer-type为inner，其他参数都有默认值，可不填写，具体如下：


```yaml
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
     # ULB类型，默认为outer，支持outer、inner
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"  
     # 用于声明ULB协议类型，并非应用协议，tcp和udp均代表ULB4，https和http均代表ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "tcp"       
     # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"
     # 控制创建ULB所在子网，填写子网ID
    "service.beta.kubernetes.io/ucloud-load-balancer-subnet-id": "subnet-xxxx" 

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

### 3.2 UDP应用通过内网ULB4对外暴露服务

如果你的应用是UDP协议，则务必显式声明健康检查的类型为port(端口检查)，否则默认为ping，可能导致ULB误认为后端业务不正常。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ucloud-inner-udp-new
  labels:
    app: ucloud-inner-udp-new
  annotations:
     # ULB类型，默认为outer，支持outer、inner
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"  
     # 用于声明ULB的Vserver类型，tcp和udp均代表ULB4，https和http均代表ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "udp"       
     # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"
     # 控制创建ULB所在子网，填写子网ID
    "service.beta.kubernetes.io/ucloud-load-balancer-subnet-id": "subnet-xxxx" 
spec:
  type: LoadBalancer
  ports:
    - name: udp
      protocol: UDP
      port: 53
      targetPort: 53
  selector:
    app: ucloud-inner-udp-new
---
apiVersion: v1
kind: Pod
metadata:
  name: test-inner-udp
  labels:
    app: ucloud-inner-udp-new
spec:
  containers:
  - name: dns
    image:  uhub.service.ucloud.cn/library/coredns:1.4.0
    ports:
    - name: udp
      containerPort: 53
      protocol: UDP

```

### 3.3 通过内网ULB7对外暴露服务


```yaml

apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    # 代表ULB类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"
    # 表示ULB协议类型，http与https等价，表示ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "https"
    # 声明要绑定的SSL证书Id，需要先将证书上传至UCloud；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert": "ssl-b103etqy"
    # 声明使用SSL协议的Service端口，多个用","分隔；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port": "443,8443"    
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
```