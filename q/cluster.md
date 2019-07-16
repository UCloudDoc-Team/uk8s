=====集群常见问题=====
{{indexmenu_n>1}}

####单个集群最多能添加多少个节点？

A：当前单个UK8S集群最多能添加50个节点。

####UK8S完全兼容原生Kubernetes API吗？

A：完全兼容。

####UK8S对Node上发布的容器有限制吗？如何修改？

A：UK8S为保障生产环境Pod的运行稳定，每个Node限制了Pod数量为110个，每Core限制了Pod数量为8个，用户可以通过登陆Node节点`vim /etc/kubernetes/kubelet.conf `
修改`maxpods:110`,`podsPerCore: 8`的对应值，然后执行`systemctl restart kubelet`重启kubelet，用户可以通过UK8S页面查看到修改结果。

注：Node节点运行Pod数量计算使用每个节点kubelet.conf中的`maxpods:110`和`podsPerCore: 8`两个规则取**最小值**，例如2Core节点的Pod数上限为16个（2x8=16个），16Core节点的Pod数上限为110个（16x8=128个，大于110个）。

#### 集群内可以解析DNS，但无法联通外网？wget拉取数据失败。

UK8S使用VPC网络实现内网互通，默认使用了UCloud的DNS，wget获取信息需要对VPC的子网配置网关，需要在UK8S所在的区域下进入VPC产品，对具体子网配置NAT网关，使集群节点可以通过NAT网关拉取外网数据，具体操作详见[VPC创建NAT网关](https://docs.ucloud.cn/network/vpc/briefguide/step4) 。

#### 集群删除了，EIP会一起被删除吗？

不会，通过UCloud官网删除已有UK8S集群，目前如果直接删除集群的话，只会删除master节点&node节点&以及和master节点相关联的ULB，所以EIP需要手动处理下。