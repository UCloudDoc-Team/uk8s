# Pod 使用独立子网

默认情况下，UK8S 中的 Pod 会向其所在节点的子网里请求分配 IP。如果希望 Pod 使用来自独立子网的 IP，请按以下方式进行配置。

1. 创建集群时，选择「Pod独立子网」选项，选择一个不同于节点网络的子网。如有需要使该子网下的 Pod 应用特定的安全组规则，请同时选择「指定安全组」。
![](/images/network/podnetworking-create-cluster.png)
2. 如果您需要配置多个「Pod独立子网」，使其中一个子网IP用尽时可以自动切换到其他子网，可以在集群创建后，通过集群详情页 - 「新增Pod子网」进行操作。
![](/images/network/podnetworking-add-subnet.png)

## Pod 独立子网原理介绍

Pod 独立子网模式下，集群内的节点必须开启「虚拟网卡 `UNI`」特性，且关闭「网络增强」。节点本身使用 `主UNI`，我们将自动为节点上的 Pod 分配一张 `辅助UNI`，Pod IP 都会被分配到 `辅助UNI` 上，出入节点的 Pod 流量会全部走`辅助UNI`，以此达到 Node 和 Pod 分离子网的效果。

如果同节点上需要给Pod分配来自多个子网 `subnet1`、`subnet2` 的 IP，UK8S 会自动为节点申请多个 `辅助UNI`。

![](/images/network/podnetworking-arch.png)

当开启了「Pod独立子网」模式后，UK8S会在集群中自动创建一个名为 `default` 的 `podnetworking` 自定义资源。

```yaml
apiVersion: vpc.uk8s.ucloud.cn/v1beta1
kind: PodNetworking
metadata:
  name: default
spec:
  securityGroupIds:
  - secgroup-xxx
  subnetIds:
  - subnet-xxx
```

节点上的 CNI 插件会在 Pod 启动时，按照 `default podnetworking` 资源指定的子网和安全组来申请 VPC IP。

> ⚠️ 如果您打算为 Pod 配置安全组，那么节点也应开启安全组模式。
>
> ⚠️ **请勿删除`default podnetworking`资源，否则 Pod 独立子网功能将不可用!**

如果您希望令 Pod 不使用独立子网，而使用节点所在子网分配的 IP，可以按以下方式创建 Pod:

```yaml
metadata:
  annotations:
    network.kubernetes.io/ucloud-pod-networking-disable: "true"
```

## Pod 使用指定子网

如果希望Pod使用来自非默认 Pod 子网的 IP , 请按以下方式进行配置。

1. 创建 `PodNetworking` 资源

```yaml
apiVersion: vpc.uk8s.ucloud.cn/v1beta1
kind: PodNetworking
metadata:
  name: my-pn-1
spec:
  securityGroupIds: # 可以为空，不允许后续变更
  - secgroup-xxx
  subnetIds: # 允许后续新增
  - subnet-xxx
```

2. 创建 Pod 资源

```yaml
metadata:
  annotations:
    network.kubernetes.io/ucloud-pod-networking-name: my-pn-1
```

## 独立子网数量限制

由于每个独立子网需要使用一张虚拟网卡，节点可用虚拟网卡的数量会限制该节点上可使用Pod独立子网数量。计算公式为:

节点可用独立Pod子网数 = 节点可绑定虚拟网卡数 - 1

单个节点存在可绑定的虚拟网卡数量主要由节点vCPU核数决定，参考 https://docs.ucloud.cn/vpc/guide/uni 。

如 8 vCPU 的节点，可绑定4张虚拟网卡，则该节点可以使用的pod独立子网数量最大为3个。

## 使用 ULB 注意事项

> ⚠️ 开启了Pod独立子网后，如果您的集群kube-proxy为**iptables**模式，LoadBalancer型svc无法使用CLB4，建议您[使用NLB或ALB](/uk8s/service/internalservice)。

