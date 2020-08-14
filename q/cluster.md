
## 集群常见问题

### 单个集群最多能添加多少个节点？

A：当前单个UK8S集群对应节点数量可查看[集群节点配置推荐](uk8s/introduction/node_requirements)。

### UK8S完全兼容原生Kubernetes API吗？

A：完全兼容。

### UK8S创建Pod失败，使用kubectl describe pod pod-name发现报错为294，是啥原因？

A：UK8S在创建Pod、LoadBalancer Service、PVC等资源时，都需要扮演云账户的身份调用UCloud API来完成相关操作。但如果您的云账户开启了[API白名单](https://console.ucloud.cn/uapi/apikey)，则贵司账户的API调用地址必须在“允许访问的IP/IP段”中，否则插件调用API报错（如申请PodIP），则Pod创建失败。

您需要在API白名单中，将10.10.10.10这个IP地址加入到“允许访问的IP/IP段”中即可，该IP地址为UK8S插件调用API时的内网代理地址。

### UK8S对Node上发布的容器有限制吗？如何修改？

A：UK8S为保障生产环境Pod的运行稳定，每个Node限制了Pod数量为110个，每Core限制了Pod数量为8个，用户可以通过登陆Node节点"vim /etc/kubernetes/kubelet.conf"
修改"maxpods:110"和“podsPerCore: 8"两个值，然后执行"systemctl restart kubelet"重启kubele即可。

注：Node节点可运行Pod数量，取每个节点kubelet.conf中的"maxpods:110"和"podsPerCore: 8"两个值中的**较小值**，例如2Core节点的Pod数上限为16个（2x8=16个），16Core节点的Pod数上限为110个（16x8=128个，大于110个）。

### 集群内可以解析DNS，但无法联通外网？wget拉取数据失败。

UK8S使用VPC网络实现内网互通，默认使用了UCloud的DNS，wget获取信息需要对VPC的子网配置网关，需要在UK8S所在的区域下进入VPC产品，对具体子网配置NAT网关，使集群节点可以通过NAT网关拉取外网数据，具体操作详见[VPC创建NAT网关](https://docs.ucloud.cn/vpc/briefguide/step4) 。

### 集群删除了，EIP会一起被删除吗？

不会，通过UCloud官网删除已有UK8S集群，目前如果直接删除集群的话，只会删除master节点&node节点&以及和master节点相关联的ULB，所以EIP需要手动处理下。


### 使用vim复制粘贴导致多行出现#号？

在vim内复制多行假如复制的行带有#号会导致其他不带#号的行自动加#，解决办法，输入一下`:set paste`命令再粘贴即可。

### 使用ULB4时VServer为什么会有健康检查失效？

健康检查失败不是发生了错误，失败的节点均是没有运行对应Pod的，ULB的VServer对该节点健康检查探测会因为iptables的DROP规则而失败，这样来自用户的请求永远不会被发往这些节点上，可以确保这些请求都能被正确响应。

![](/images/q/vserver.png)