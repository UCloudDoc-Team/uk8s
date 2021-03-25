
## ULB 参数说明

本文主要描述用于创建LoadBalancer 类型的Service时，与ULB相关的Annotations说明。

> 备注：
> 1. 目前除了外网 ULB 绑定的 EIP 的带宽值以外，其他参数暂时不支持修改，请谨慎配置。
> 2. 外网 ULB 绑定的 EIP 的带宽值，必须通过 Annotations 修改，Annotations 将会覆盖控制台修改的配置。


### 内网ULB4

```yaml
    # 负载均衡器类型，必须指定，枚举值为inner或outer，此处应为inner;
    "service.beta.kubernetes.io/ucloud-load-balancer-type" 
    # tcp和udp均代表ULB4，https和http均代表ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol"  
    # VServer负载均衡模式
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-method"   
    # 空闲连接的回收时间
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout"  
    # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"
    # 控制创建ULB所在子网，填写子网ID，不填写使用VPC默认子网
    "service.beta.kubernetes.io/ucloud-load-balancer-subnet-id": "subnet-xxxx" 
```

**Annotations 详解**


* service.beta.kubernetes.io/ucloud-load-balancer-type 


负载均衡器的网络类型，枚举值为inner或outer，默认为outer。对于需要被VPC内网访问的Service而言，此key必须指定，且value必须为inner


* service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol 

tcp和udp均代表ULB4，https和http均代表ULB7；vserver的实际protocol由该值和Service protocol共同决定。如果Service的protocol为tcp，且vserver-protocol为tcp或udp，则最终vserver为tcp；如果Service的protocol为tcp，而vserver-protocol为https或https，则Vserver的协议为http或https。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-method 

VServer的负载均衡模式，枚举值为roundrobin（轮询）、source（源地址）、consistenthash（一致性哈希）、sourceport（源地址计算端口）、consistenthashport（端口一致性哈希），默认为roundrobin。


* service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout 

listentype为packetstransmit时表示连接保持的时间，单位为秒，取值范围：[60，900]，0表示禁用连接保持，默认为0。

* service.beta.kubernetes.io/ucloud-load-balancer-subnet-id

控制创建ULB所在子网，填写子网ID，不填写使用VPC默认子网

### 外网ULB4
```yaml
    # tcp和udp均代表ULB4，https和http均代表ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "TCP"  
    # VServer负载均衡模式
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-method   
    # 空闲连接的回收时间
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout  
    # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"


```
**Annotations 详解**

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol 

tcp和udp均代表ULB4，https和http均代表ULB7；

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-method 

VServer的负载均衡模式，枚举值为roundrobin（轮询）、source（源地址）、consistenthash（一致性哈希）、sourceport（源地址计算端口）、consistenthashport（端口一致性哈希），默认为roundrobin。如Vserver实例的协议为udp，则不需要指明。


* service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout 

ListenType为packetstransmit时表示连接保持的时间，单位为秒，取值范围：[60，900]，0表示禁用连接保持，默认为0。

### 外网ULB7

```yaml
    # 协议类型，tcp和udp均表示ULB4,https和http均表示ULB7
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol: "HTTPS" 
    # ssl证书id
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert: "ssl-b103etqy"
    # 开启ssl协议的端口，多个用","分隔开，必须和ssl-cert同时指定
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port: "443"
    # VServer负载均衡模式
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-method    
    ## VServer会话保持方式
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-type  
    ## 用户自定义String，会话保持方式为userdefined有效
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-info 
    ## 空闲连接的回收时间
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout   
    ## 健康检查类型
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type 
    ## HTTP检查域名
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-domain 
    ## HTTP检查路径
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-path 
```

**Annotations 详解**

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol 

ULB类型，tcp和udp均表示ULB4,https和http均表示ULB7

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert

SSL证书Id

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-method 

VServer的负载均衡模式，枚举值为roundrobin（轮询）、source（源地址），默认为roundrobin。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-type

VServer会话保持方式,枚举值为none（关闭），serverinsert（自动生成KEY），userdefined（用户自定义KEY），默认为none。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-info

用户自定义KEY，会话保持方式为userdefined时有效

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout 

ListenType为RequestProxy时表示空闲连接的回收时间，单位为秒，取值范围：[60，900]，0表示禁用连接保持，默认为60。取值范围为60-900时，persistence-type不能为none。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type 

健康检查方式，枚举值为port或path,默认为port。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-domain 

健康检查方式为path时有效，指http检查域名。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-path 

健康检查方式为path时有效，指http检查路径。

### 外网ULB绑定的EIP注释

```yaml
    # 计费模式，支持traffic（流量计费）、bandwidth（带宽计费）、sharebandwidth（共享带宽），默认为bandwidth
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-paymode": "sharebandwidth" 
    # 共享带宽id
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-sharebandwidthid": "bwshare-d8dklw" 
    # 外网带宽，共享带宽模式下无需指定，或者配置为0，bandwidth下默认为2Mbps，外网带宽必须通过 annotation 修改，直接控制台修改将不生效
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-bandwidth": "2" 
    # 付费模式，支持month（按月付费），year（按年付费），dynamic（按时付费）
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-chargetype": "month"
    # 付费时长，默认为1，chargetype为dynamic时无需填写。
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-quantity": "1" 
```