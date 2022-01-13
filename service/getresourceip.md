## 获取真实客户端IP

### 网络编程中如何获得对端IP

1. 如果是HTTP1.1协议，一般的反向代理或者负载均衡设备（如ULB7）支持X-Forwarded-For头部字段，会在用户的请求报文中加入类似**X-Forwarded-For:114.248.238.236**的头部。Web应用程序只需要解析该头部即可获得用户真实IP。

2. 如果是TCP或UDP自定义协议，可以客户端在协议字段里定义一个大端unsigned字段来保存自身IP，服务端把该字段解析出来然后调用inet_ntoa(3)等函数获得ipv4点分字符串。

3. 如果2中协议不支持填写自身IP，则服务端可以通过socket系统调用getpeername(2)来获取对端地址。下文讨论此方式。

### Kubernetes Loadbalancer ULB4碰到的问题

UK8S使用ULB4和ULB7来支持Loadbalancer类型的Service。对于ULB7，由于只支持HTTP协议且默认支持X-Forwarded-For头部，所以Web服务可以很容易获取客户端的真实IP。但对于使用ULB4接入的纯四层协议的服务来说，可能需要使用getpeername(2)来获取客户端真实IP。然而由于目前kube-proxy采用Iptables模式，后端pod内的应用程序的网络库调用getpeername(2)会无法获得正确的IP地址。以下例子可以说明问题。

部署一个简单的webserver，通过Loadbalancer ULB4外网模式接入。

```
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx
  labels:
    app: ucloud-nginx
  annotations:
    service.beta.kubernetes.io/ucloud-load-balancer-type: "outer"
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-method: "source" 
spec:
  type: LoadBalancer
  ports:
    - protocol: "TCP"
      port: 80
      targetPort: 12345
  selector:
    app: ucloud-nginx

---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx
  labels:
    app: ucloud-nginx
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/uk8s/uk8s-helloworld:stable
    ports:
     - containerPort: 12345
```

部署完毕后，Service状态如下所示，可以通过EIP 117.50.3.206访问该服务。

```
# kubectl  get svc ucloud-nginx
NAME           TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)        AGE
ucloud-nginx   LoadBalancer   172.17.179.247   117.50.3.206   80:43832/TCP   112s
```

服务本身的源码非常简单，只返回客户端地址，如下所示。

```
package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"net/http/httputil"
)

func main() {
	log.Println("Server hello-world")
	http.HandleFunc("/", AppRouter)
	http.ListenAndServe(":12345", nil)
}

func AppRouter(w http.ResponseWriter, r *http.Request) {
	dump, _ := httputil.DumpRequest(r, false)
	log.Printf("%q\n", dump)
	io.WriteString(w, fmt.Sprintf("Guest come from %v\n", r.RemoteAddr))
	return
}
```

在外网通过浏览器访问该服务，如下所示。

![](/images/service/guestcome.png)

结果显示用户的访问IP地址是一台云主机的内网IP地址，显然不正确。

### 原因解释

Loadbalancer创建成功后，ULB4的VServer将UK8S集群中的每个Node云主机节点作为自身的RS节点，RS端口为Service申明的Port值（注意不是NodePort）。ULB4将访问流量转发到其中一个RS后，RS根据本机上kube-proxy生成的iptables规则将流量DNAT到后端Pod中，如下所示。

![](/images/service/ulb4.jpg)

图中ULB4先将流量转发到Node1中，Node1中根据iptables DNAT规则，将流量转发给Node2中的Pod。
需要注意的是，Node1将IP包转发到Node2前，对这个包有一次SNAT操作。准确地说，是一次MASQUERADE操作，规则如下。

```
-A KUBE-POSTROUTING -m comment --comment "kubernetes service traffic requiring SNAT" -m mark --mark 0x4000/0x4000 -j MASQUERADE
```

这条规则将源地址改成Node1的本机地址，即10.9.31.26。当然，这个 SNAT
操作只针对本Service转发出来的包，否则普通的IP包也受到影响了，而判定IP包是否由本Service转发出来的依据是改包上是有有个"0x4000"标志，这个标志则是在DNAT操作前打上去的。

由于IP请求包的源地址被修改，Pod内的程序网络库通过getpeername(2)调用获取到的对端地址是Node1的IP地址而不是客户端真实的地址。

**为什么需要对流出的包做SNAT操作呢？**

原因比较简单。参考下图，当Node1上的Pod处理完请求后，需要发送响应包，如果没有SNAT操作，Pod收到的请求包源地址就是client的IP地址，这时候Pod会直接将响应包发给client的IP地址，但对于client程序来说，它明明没有往PodIP发送请求包，却收到来自Pod的IP包，这个包很可能会被client丢弃。而有了SNAT，Pod会将响应包发给Node1，Node1再根据DNAT规则产生的conntrack记录，将响应包通过返回给client。

```
       client
        \ ^
         \ \
          v \
           ulb4
            \ ^
             \ \
              v \
  node 1 <--- node 2    
   | ^   SNAT
   | |   --->
   v |
endpoint
```

### 如何获取源IP？

对于Pod需要明确知道客户端来源地址的情况，我们需要显示地将Service的spec.externalTrafficPolicy设置成Local,如下修改。

```
apiVersion: v1
kind: Service
metadata:
  name: ucloud-nginx
  labels:
    app: ucloud-nginx
  annotations:
    service.beta.kubernetes.io/ucloud-load-balancer-type: "outer"
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-method: "source"
spec:
  type: LoadBalancer
  ports:
    - protocol: "TCP"
      port: 80
      targetPort: 12345
  selector:
    app: ucloud-nginx
  externalTrafficPolicy: Local
```

重新部署服务后，再用浏览器访问，可以发现Pod正确获取了浏览器的访问IP。

![](/images/service/realip.png)

而这个机制的原理也很简单，当设置了externalTrafficPolicy为Local时，Node上的iptables规则会设置只将IP包转发到在本机上运行的Pod，如果本机上无对应Pod在运行，此包将被DROP。如下图，这样Pod可以直接使用client的源地址进行回包而不需要SNAT操作。

```
     client
      \ ^
       \ \
        v \ 
       ulb4
      ^ /   \
     / /     \  VServer健康检查失败
    / v       X
  node 1     node 2
   ^ |
   | |
   | v
endpoint
```

对于其他未运行Service对应Pod的Node节点来说，ULB
VServer对其健康检查探测会因为iptables的DROP规则而失败，这样来自用户的请求永远不会被发往这些节点上，可以确保这些请求都能被正确响应。

![](/images/service/vserver.png)
