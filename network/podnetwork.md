# Pod 使用独立子网

默认情况下，UK8S 中的 Pod 会向其所在节点的子网里请求分配 IP。如果希望 Pod 使用来自独立子网的 IP，请按以下方式进行配置。

1. 创建集群时，选择「Pod独立子网」选项，选择一个不同于节点网络的子网。如有需要使该子网下的 Pod 应用特定的安全组规则，请同时选择「指定安全组」。
2. 如果您需要配置多个「Pod独立子网」，使其中一个子网IP用尽时可以自动切换到其他子网，可以在集群创建后，通过集群详情页 - 「新增Pod子网」进行操作。

## Pod 独立子网原理介绍

Pod 独立子网模式下，集群内的节点必须开启「虚拟网卡 `UNI`」特性。节点本身使用 `主UNI`，我们将自动为节点上的 Pod 分配一张 `辅助UNI`，Pod IP 都会被分配到 `辅助UNI` 上，出入节点的 Pod 流量会全部走`辅助UNI`，以此达到 Node 和 Pod 分离子网的效果。

如果您需要给Pod分配来自多个子网`subnet1`、`subnet2`的IP，UK8S会为您自动申请多个`辅助UNI`。

## Pod 使用指定子网

如果希望Pod使用来自非默认Pod子网的IP, 请按以下方式进行配置。

>  前提: 请确保cni已经升级到1.x.x及以上

1. 创建 `PodNetworking` 资源
```yaml
apiVersion: network.ucloud.cn/v1beta1
kind: PodNetworking
metadata:
  name: my-pn-1
spec:
  securityGroupIds: # 可以为空，不允许后续变更
  - sg-xxx
  subnetIds: # 允许后续新增
  - subnet-xxx
```

2. 创建 Pod 资源
```yaml
metadata:
  annotations:
    network.kubernetes.io/ucloud-pod-networking-name: my-pn-1
```

请注意，如果 Pod 落在了非虚拟网卡节点上，则不会被分配独立子网 IP。如果您的集群内同时存在虚拟网卡节点和非虚拟网卡节点，请为Pod指定使用 `ucloud.cn/uni` 资源。

```yaml
    resources:
      limits:
        ucloud.cn/uni: "0.01"
```

## 独立子网数量限制

由于每个独立子网需要使用一张虚拟网卡，节点可用虚拟网卡的数量会限制该节点上可使用Pod独立子网数量。计算公式为:

节点可用独立Pod子网数 = 节点可绑定虚拟网卡数 - 1

单个节点存在可绑定的虚拟网卡数量主要由节点vCPU核数决定，参考 https://docs.ucloud.cn/vpc/guide/uni 。

如 8 vCPU 的节点，可绑定4张虚拟网卡，则该节点可以使用的pod独立子网数量最大为3个。
