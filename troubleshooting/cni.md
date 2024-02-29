# CNI 相关常见问题

## 1. CNI 插件升级为什么失败了？

1. 检查节点是否设置了污点及禁止调度（master 节点的默认污点不计算在内），带有污点的节点需要选择强制升级（不会对节点有特殊影响）。
2. 如果强制升级失败的，请重新点击 cni 强制升级。
3. 执行`kubectl get pods -n kube-system |grep plugin-operation`找到对应插件升级的 pod，并 describe pod 查看 pod
   失败原因。

## 2. 为什么我的集群连不上外网?

UK8S 使用 VPC 网络实现内网互通，默认使用了 UCloud 的 DNS，wget 获取信息需要对 VPC 的子网配置网关，需要在 UK8S 所在的区域下进入VPC产品，对具体子网配置 NAT
网关，使集群节点可以通过 NAT 网关拉取外网数据，具体操作详见[VPC创建NAT网关](https://docs.ucloud.cn/vpc/briefguide/step4) 。