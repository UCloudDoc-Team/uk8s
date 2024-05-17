# 通过内网ULB访问Service

## 1. 使用提醒

* cloudprovider 版本 < `22.07.1`

如果您的cloudprovider版本低于`22.07.1`，请勿修改由UK8S创建的ULB及Vserver的名称和备注，否则会导致Service异常无法访问。如果版本等于或高于`22.07.1`，则允许修改ULB的名称和备注（注意Vserver的依然不可更改）。如果您有修改ULB名称和备注的需求，请升级您的cloudprovider到最新版本，详见[CloudProvider 插件更新](/uk8s/service/cp_update)。

* 相关ULB删除

如 ULB 为 UK8S 在创建 Service 时同步创建，删除 Service 时 ULB 会同步删除，请勿将 ULB 关联其他 Vserver，如需多个 Service 共用 ULB，可先创建 ULB，并在创建 Service 时关联已有 ULB，详情请见[使用已有 ULB](/uk8s/service/ulb_designation)。


* 参数修改

除外网EIP外，ULB相关参数目前均不支持Update修改，如不确认如何填写，请咨询UCloud 技术支持。

## 2. 使用UDP协议前必读

* 监控检查

目前ULB4针对UDP协议的健康检查支持ping和port两种模式，默认为ping，强烈推荐改为port；

* ping 健康检查须知

ping检查会发送目标IP为ulb-ip的ICMP Ping报文到后端节点。在UK8S的实现中，后端节点仅配置了针对UDP端口的网络包转发规则，而没有在网卡上绑定ulb-ip，因此无法响应以上ping报文，默认情况下ping健康检查会失败。如果需要使用ping健康检查，请参考 [ULB文档 - 报文转发模式服务节点配置](/ulb/guide/realserver/editrealserver)为后端节点绑定ulb-ip;   

* port 健康检查须知

port健康检查的后端实现是对UDP端口发送UDP报文( "Health Check" 字符串)和针对RS IP发送ICMP Ping报文。如果超时时间内回复了UDP报文则认为健康；如果超时时间没收到UDP回包，则以Ping的探测结果为准，因此您的应用程序需要响应UDP健康检查报文。

* **回包长度**

**需要注意的是UDP回包长度不要超过1440，以避免可能的分片导致ULB4无法收到健康检查响应，导致健康检查失败。**


## 3. 选择ULB4还是ULB7

ULB支持“报文转发(ULB4)”及“请求代理（ULB7）”两种转发模式，外网模式下推荐使用ULB4，因为ULB4的性能更好；请求代理（ULB7）转发模式建议选择应用型负载均衡ALB，传统型负载均衡CLB在使用过程中会受到一些[传统型负载均衡配额限制](/ulb/intro/limit)，目前ALB是收费，具体价格请参考[ULB计费说明](/ulb/alb/buy/charge)。

## 4. 操作指南

### 4.1 通过ULB7对外暴露服务（http/https）

> ⚠️ 使用 ALB 需要 [CloudProvider](/uk8s/service/cp_update) 版本 >= 24.03.13。

UK8S在集群内可以直接使用 LoadBalancer 类型的Service，如果需要对外提供http/https协议，建议选择应用型负载均衡ALB；用户可以通过Service的"annotations"来配置ULB类型以及其他参数；更多参数信息可参考[ULB参数说明](/uk8s/service/annotations)。

负载均衡所使用的 SSL 证书的管理，请参见 ULB 文档：[添加证书](/ulb/guide/certificate/addcertificate)

如果用户选择ULB类型为外网时，还需要注意关于外网带宽设置，EIP计费模式的选择；

```
# 代表ULB网络类型，outer为外网，inner为内网；outer为默认值，此处可省略。
"service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
# bandwidth下默认为2Mpbs,建议显式声明带宽大小，避免费用超标。
"service.beta.kubernetes.io/ucloud-load-balancer-eip-bandwidth": "2" 
# 付费模式，支持month，year，dynamic，默认为month
"service.beta.kubernetes.io/ucloud-load-balancer-eip-chargetype": "month" 
# 付费时长，默认为1，chargetype为dynimic时无效    
"service.beta.kubernetes.io/ucloud-load-balancer-eip-quantity": "1"   
```

下面是内网ULB7的使用例子：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    # 代表ULB类型，outer为外网，inner为内网；outer为默认值，此处可省略；
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"
    # 选择ULB类型，“application”表示使用应用型负载均衡ALB，其他类型参考：ULB参数说明；
    "service.beta.kubernetes.io/ucloud-load-balancer-listentype": "application"
    # 表示ULB协议类型，http与https等价，表示应用型负载均衡ULB7；如果选择了https协议，还配置证书与端口；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "https"
    # 声明要绑定的SSL证书Id，需要先将证书上传至UCloud；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert": "ssl-qsmo0c7o9y1"
    # 声明使用SSL协议的Service端口，多个用","分隔；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port": "443,8443"   
    # ALB目前是计费，默认是按月收费，用户可以调整付费方式；
    "service.beta.kubernetes.io/ucloud-load-balancer-paymode": "month"
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

### 4.2 通过ULB4对外暴露服务（TCP）

对于TCP协议的服务，如果内网暴露只需要在metadata.annotations 指定 load-balancer-type为inner，外网load-balancer-type为outer，其他参数都有默认值，可不填写，具体如下：

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

### 4.3 通过ULB4对外暴露服务（UDP）

如果你的应用是UDP协议，则务必显式声明健康检查的类型为port（端口检查），否则默认为ping，可能导致ULB误认为后端业务不正常。如果需要外网暴露请注意修改 ucloud-load-balancer-type 为 outer


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
     # 表示ULB协议类型，tcp和udp均代表ULB4，https和http均代表ULB7；
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

### 4.4 通过ULB4对外暴露服务（TCP和UDP协议混用）

24.03.5以后的 CloudProvider 插件，当"service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol"为tcp/udp或省略时, ULB4同时支持TCP和UDP两种协议。下文示例中，对外暴露了两个端口，其中80端口使用TCP协议，53端口使用UDP协议。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx-out-tcp-new
  labels:
    app: ucloud-nginx-out-tcp-new
  annotations:
    # 代表ULB网络类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"
    # 表示ULB协议类型，tcp、udp与tcp/udp等价，表示ULB4；使用tcp/udp或省略时时，同时支持TCP和UDP协议
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "tcp/udp"
    # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"    
spec:
  type: LoadBalancer
  ports:
    - name: tcp-default
      protocol: TCP
      port: 80
      targetPort: 80
    - name: udp
      protocol: UDP
      port: 53
      targetPort: 53 
  selector:
    app: ucloud-nginx-out-tcp-new
---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx-out-tcp1
  labels:
    app: ucloud-nginx-out-tcp-new
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
    ports:
    - containerPort: 80
      protocol: TCP
  - name: dns
    image:  uhub.service.ucloud.cn/library/coredns:1.4.0
    ports:
    - name: udp
      containerPort: 53
      protocol: UDP
```



