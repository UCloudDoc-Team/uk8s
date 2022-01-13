## 配置自定义DNS服务

本文主要介绍如何在UK8S集群中，使用自定义的DNS服务。

从Kubernetes
1.11起，CoreDNS取代kube-dns成为默认的DNS方案，UK8S目前支持的Kubernetes版本>=1.11，因此本文主要介绍如何修改CoreDNS的配置以达到使用自定义DNS服务的目的。

### 简介

CoreDNS是一个模块化、插件式的DNS服务器，其配置文件信息保存在Corefile内。UK8S集群管理员可通过修改ConfigMap，来配置自定义DNS服务。

在UK8S中，CoreDNS的默认Corefile配置信息如下:

```
apiVersion: v1
kind: ConfigMap
data:
  Corefile: |
    .:53 {
        errors
        health
        kubernetes cluster.local in-addr.arpa ip6.arpa {
          pods insecure
          upstream 
          fallthrough in-addr.arpa ip6.arpai
          ttl 30
        }
        prometheus :9153
        forward . /etc/resolv.conf {
          policy sequential
        }
        cache 30
        loop
        reload
        loadbalance
    }
metadata:
  name: coredns
  namespace: kube-system
```

Corefile的配置信息包含以下CoreDNS的插件：

- errors: 错误日志会以标准输出的方式打印到容器日志；

- health: CoreDNS的健康状况；

- kubernetes: kubernetes插件是CoreDNS中用来替代kube-dns的模块，将service的域名转为IP的工作由该插件完成，其中常用的参数作用如下：

  - **pods POD-MODES**: 用于设置Pod的A记录处理模式，如**1-2-3-4.ns.pod.cluster.local. in A 1.2.3.4**。**pods
    disabled**为默认值，表示不为pod提供dns记录；**pods insecure**会一直返回对应的A记录，而不校验ns；**pods
    verified**会校验ns是否正确，如果该ns下有对应的pod，则返回A记录。

  - **upstream [ADDRESS..]**: 定义用于解析外部hosts的上游dns服务器。如果不指定，则CoreDNS会自行处理，例如使用后面会介绍到的proxy插件。

  - **fallthrough [ZONE..]**: 如果指定此选项，则DNS查询将在插件链上传递，该插件链可以包含另一个插件来处理查询，例如**in-addr.arpa**。

- prometheus: CoreDNS对外暴露的监控指标，默认为http://localhost:9153/metrics。

- forward [from to]: 任何不属于Kubernetes集群内部的域名，其DNS请求都将指向forword指定的 DNS
  服务器地址。**from**一般为"."，代表所有域名，**to**可以为多个，如111.114.114.114
  8.8.8.8。需要注意的是，新版本的CoreDNS已forward插件替代proxy插件，不过使用方法是一致的，如果你的集群是proxy，建议改为forward插件，性能更好。

- reload: 允许自动加载变化了的Corefile，建议配置，这样CoreDNS可以实现热更新。

其他选项的意义请查看Kubernetes官方文档，下面我们举例说明下如何修改ConfigMap。

### 示例

#### 为特殊域配置DNS服务器

假设我们有一个ucloudk8s的服务域，自建的私有DNS Server地址为10.9.10.8，则集群管理员可以执行kubectl edit configmap/coredns -n
kube-system中添加如下所示的一段规则，这是个独立的**Server Block**,我们可以在Corefile里面为不同的域配置不同的**Server Block**。

```
ucloudk8s.com:53 {
        errors
        cache 30
        forward . 10.9.10.8
    }
```

并且，我们不希望使用/etc/resolv.conf里配置的DNS服务器作为上游服务器，而是指向自建的DNS Server，只需要直接修改之前提到的upstream和proxy选项即可

```
upstream 10.9.10.8
forward .  172.16.0.1
```

修改完毕后的configmap如下：

```
apiVersion: v1
kind: ConfigMap
data:
  Corefile: |
    .:53 {
        errors
        health
        kubernetes cluster.local in-addr.arpa ip6.arpa {
          pods insecure
          upstream 10.9.10.8
          fallthrough in-addr.arpa ip6.arpa
        }
        prometheus :9153
        forward . 10.9.10.8
        cache 30
        loop
        reload
        loadbalance
        }
    ucloudk8s.com:53 {
        errors
        cache 30
        forward . 10.9.10.8
       }
metadata:
  name: coredns
  namespace: kube-system
```

### 验证

我们在同VPC下的某台云主机中(请勿在UK8S Node节点中操作)安装一个DNS服务器，来验证自定义DNS是否正常工作。

#### 通过Docker安装DNS服务器

```
docker run -d -p 53:53/tcp -p 53:53/udp --cap-add=NET_ADMIN --name dns-server andyshinn/dnsmasq:2.75
```

#### 进入容器

```
docker exec -it dns-server /bin/sh
```

#### 配置上游DNS服务器

```
vi /etc/resolv.dnsmasq

nameserver 114.114.114.114
nameserver 8.8.8.8
```

#### 配置本地解析规则

```
vi /etc/dnsmasqhosts

110.110.110.110 baidu.com
```

#### 修改dnsmasq配置文件，指定使用上述两个我们自定义的配置文件，修改下述两个选项，并重启容器。

```
vi /etc/dnsmasq.conf

resolv-file=/etc/resolv.dnsmasq
addn-hosts=/etc/dnsmasqhosts

docker restart dns-server
```

#### 修改CoreDNS的configmap，添加如下规则。

```
baidu.com:53{
  errors
  cache 30
  forward . 10.9.10.8(测试时需修改成你的DNS地址)      

 }
```

#### 进入K8S在容器内测试，使用dig命名测试，可以看到解析地址为110.110.110.110，符合预期。

```
bash-4.4# dig baidu.com

; <<>> DiG 9.12.3-P4 <<>> baidu.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 39140
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;baidu.com.                     IN      A

;; ANSWER SECTION:
baidu.com.              5       IN      A       110.110.110.110

;; Query time: 4 msec
;; SERVER: 172.17.0.2#53(172.17.0.2)
;; WHEN: Mon May 27 09:11:50 UTC 2019
;; MSG SIZE  rcvd: 63
```

### 常见问题

#### 修改了CoreFile，但解析不成功

首先确认CoreFile是否包含了reload插件，如果没有包含，需要添加reload，并且重建CoreDNS，使其可以加载到最新的DNS规则。

其次，通过''kubectl logs COREDNS-POD-NAME -n kube-system''查看CoreDNS日志，确认CoreDNS是否正常工作，以及DNS配置是否加载成功。

如果依然不能正常工作，在容器或Pod内执行''dig @YOUR-DNS-SERVER-ADDRESS YOUR-DOMAIN''，确认您的DNS服务器是否正常工作。

如以上操作皆无效，请联系UCloud技术支持协助处理。
