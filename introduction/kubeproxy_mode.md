## kube-proxy模式选择
kube-proxy是kubernetes中的关键组件。他的角色就是在服务Service和其后端Pod之间（Endpoint）进行负载均衡。kube-proxy 有三种运行模式，每种都有不同的实现技术：userspace、iptables或者IPVS。

userspace模式由于性能问题已经不推荐使用。这里主要介绍iptables和IPVS两种模式的比较及选择。

### 选择推荐

* 如果您是长连接服务、集群规模较大、服务多，推荐您选择IPVS。（详见后续测试数据）

* 如果您是短连接服务、集群规模中等，推荐您选择iptables。

注：在使用IPVS模式的kubernetes集群中进行滚动更新，同一个客户端发送http短链接，客户端端口会被重用，导致node收到五元组相同的报文，会触发IPVS复用Connection，导致将报文发到了一个已经彻底销毁的Pod上。

官方issue：https://github.com/kubernetes/kubernetes/issues/81775

所以如果您的服务是短连接服务涉及以上使用场景，推荐使用iptables，或使用IPVS需要参考issue进行内核参数修改。


### iptables模式

iptables是一个Linux内核功能，是一个高效的防火墙，并提供了大量的数据包处理和过滤方面的能力。它可以在核心数据包处理管线上用Hook挂接一系列的规则。iptables模式中kube-proxy在NAT pre-routing Hook中实现它的NAT和负载均衡功能。这种方法简单有效，依赖于成熟的内核功能，并且能够和其它跟 iptables 协作的应用融洽相处。

### IPVS模式

IPVS是一个用于负载均衡的Linux内核功能。IPVS模式下，kube-proxy使用IPVS负载均衡代替了iptable。这种模式同样有效，IPVS的设计就是用来为大量服务进行负载均衡的，它有一套优化过的API，使用优化的查找算法，而不是从列表中查找规则。


### 模式对比

无论是iptables模式还是IPVS模式，转发性能都与Service和对应Endpoint数量有关，理由是Node上iptables或IPVS转发规则的数量与svc和ep的数目成正比。

IPVS和iptables转发性能主要差异体现在TCP三次握手连接建立的过程，因此短连接请求场景下，两种模式的性能差异较为突出。

在Service和Endpoint的数量较少的情况下(Service数十到数百，Endpoint数百到数千)，iptables模式转发性能要略优于IPVS。

随着Service和Endpoint的数量逐渐提升，iptables模式转发性能明显下降，IPVS模式转发性能则能保持稳定。

Service数量1000左右，Endpoint数量到20000左右时，iptables模式转发性能开始低于IPVS，随着Service和Endpoint的数量继续增大（Service数千，Endpoint数万），ipvs模式性能略微下降，iptables模式性能则大幅下降。


### 测试用例

我们使用了2台Node作为测试节点，一台节点KubeProxy使用iptables模式，记为N1；另一台KubeProxy使用IPVS模式，记为N2。

在N1和N2上准备好压测客户端ab，并发连接数1000，一共需要完成10000次短连接请求。

在N1和N2上分别但不同时执行测试命令，观察ab返回的结果，重点关注以下：

```
Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        1   38   8.4     38      59
Processing:    10   41   9.7     40      67
Waiting:        1   28   9.0     28      56
Total:         51   79   7.5     78     101
```

不断变化Service数量,100，500，1000，2000，3000，4000，观察结果采集数据。

以下为UK8S团队针对IPVS和iptables进行的性能测试数据。

![](/images/introduction/s100.png)

![](/images/introduction/s500.png)

![](/images/introduction/s1000.png)

![](/images/introduction/s2000.png)

![](/images/introduction/s3000.png)

![](/images/introduction/s4000.png)

可以看出，在Service数量为100和500时，iptables转发性能要优于ipvs；Service数量达到1000时，两者大体持平；Service数量继续增大，ipvs的性能优势则越发明显。

