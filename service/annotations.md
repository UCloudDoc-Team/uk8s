=====Service Annotations====
{{indexmenu_n>0}}

本文主要描述用于创建LoadBalancer 类型的Service时，与ULB相关的Annotations说明。

> 备注：目前除了EIP带宽值以外，其他参数暂时不支持update，请谨慎配置。


### 内网ULB4

<code>
   "service.beta.kubernetes.io/ucloud-load-balancer-type" 
   # 负载均衡器类型，必须指定
   "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol"  
   # TCP和UDP均代表ULB4，HTTPS和HTTP均代表ULB7；
    
   "service.beta.kubernetes.io/ucloud-load-balancer-vserver-method"   
   # VServer负载均衡模式
   "service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-type"  
   # VServer会话保持方式
   "service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-info" 
   # 用户自定义String，会话保持方式为UserDefined有效
   "service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout"  
   # 空闲连接的回收时间
</code>

**Annotations 详解**


* service.beta.kubernetes.io/ucloud-load-balancer-type 


负载均衡器的网络类型，枚举值为Inner或Outer，默认为Outer。对于需要被VPC内网访问的Service而言，此key必须指定，且value必须为Inner


* service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol 

TCP和UDP均代表ULB4，HTTPS和HTTP均代表ULB7；vserver的实际protocol由该值和Service protocol共同决定。如果Service的protocol为tcp，且vserver-protocol为tcp或udp，则最终vserver为tcp；如果Service的protocol为tcp，而vserver-protocol为HTTPS或HTTP，则Vserver的协议为HTTP或HTTPS。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-method 

VServer的负载均衡模式，枚举值为Roundrobin（轮询）、Source（源地址）、ConsistentHash（一致性哈希）、SourcePort（源地址计算端口）、ConsistentHashPort（端口一致性哈希），默认为Roundrobin。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-type

VServer会话保持方式,枚举值为None（关闭），ServerInsert（自动生成KEY），UserDefined（用户自定义KEY），默认为None。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-info

用户自定义KEY，会话保持方式为UserDefined时有效

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout 

ListenType为PacketsTransmit时表示连接保持的时间，单位为秒，取值范围：[60，900]，0表示禁用连接保持，默认为60。




### 外网ULB4
<code yaml>
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol: "TCP"  
    # TCP和UDP均代表ULB4，HTTPS和HTTP均代表ULB7；
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-method   
    # VServer负载均衡模式
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-type 
    # VServer会话保持方式
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-info
    # 用户自定义String，会话保持方式为UserDefined有效
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout  
    # 空闲连接的回收时间

</code>
**Annotations 详解**

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol 

TCP和UDP均代表ULB4，HTTPS和HTTP均代表ULB7；

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-method 

VServer的负载均衡模式，枚举值为Roundrobin（轮询）、Source（源地址）、ConsistentHash（一致性哈希）、SourcePort（源地址计算端口）、ConsistentHashPort（端口一致性哈希），默认为Roundrobin。如Vserver实例的协议为UDP，则不需要指明。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-type

VServer会话保持方式,枚举值为None（关闭），ServerInsert（自动生成KEY），UserDefined（用户自定义KEY），默认为None。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-info

用户自定义KEY，会话保持方式为UserDefined时有效

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout 

ListenType为PacketsTransmit时表示连接保持的时间，单位为秒，取值范围：[60，900]，0表示禁用连接保持，默认为60。

### 外网ULB7

<code yaml>
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol: "HTTPS" 
    # 协议类型，TCP和UDP均表示ULB4,HTTPS和HTTP均表示ULB7
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert: "ssl-b103etqy"
    # ssl证书id
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port: "443"
    # 开启ssl协议的端口，多个用","分隔开，必须和ssl-cert同时指定
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-method    
    # VServer负载均衡模式
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-type  
    ## VServer会话保持方式
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-info 
    ## 用户自定义String，会话保持方式为UserDefined有效
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout   
    ## 空闲连接的回收时间
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type 
    ## 健康检查类型
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-domain 
    ## HTTP检查域名
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-path 
    ##HTTP检查路径
</code>

**Annotations 详解**

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol 

ULB类型，TCP和UDP均表示ULB4,HTTPS和HTTP均表示ULB7

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert

SSL证书Id

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-method 

VServer的负载均衡模式，枚举值为Roundrobin（轮询）、Source（源地址），默认为Roundrobin。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-type

VServer会话保持方式,枚举值为None（关闭），ServerInsert（自动生成KEY），UserDefined（用户自定义KEY），默认为None。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-session-persistence-info

用户自定义KEY，会话保持方式为UserDefined时有效

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-client-timeout 

ListenType为PacketsTransmit时表示连接保持的时间，单位为秒，取值范围：[60，900]，0表示禁用连接保持，默认为60。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type 

健康检查方式，枚举值为Port或Path,默认为Port。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-domain 

健康检查方式为Path时有效，指http检查域名。

* service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-path 

健康检查方式为Path时有效，指http检查路径。

### 外网ULB绑定的EIP注释

<code yaml>
"service.beta.kubernetes.io/ucloud-load-balancer-eip-paymode": "ShareBandwidth" 
 # 支持Traffic、Bandwidth、ShareBandwidth，默认为Bandwidth
"service.beta.kubernetes.io/ucloud-load-balancer-eip-sharebandwidthid": "bwshare-d8dklw" 
 # 共享带宽id
"service.beta.kubernetes.io/ucloud-load-balancer-eip-bandwidth": "10" 
 # 共享带宽模式下无需指定，或者配置为0，Bandwidth下默认为10 
"service.beta.kubernetes.io/ucloud-load-balancer-eip-chargetype": "month"
 # 付费模式，支持Month，Year，Dynamic
"service.beta.kubernetes.io/ucloud-load-balancer-eip-quantity": "1" 
 # 付费时长，默认为1，chargetype为Dynimic时无效
</code>
