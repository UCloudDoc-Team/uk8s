## 改变 CoreDNS 部署方式

UK8S 默认为 CoreDNS 服务配置了 Pod 反亲和性，两个服务副本需要分散在两个不同节点上。这会导致您在开启节点自动扩缩容之后，集群缩容只能缩到最小两节点。

如果您希望集群可以缩容至单节点，可以按如下方式修改 CoreDNS 部署方式。

1. 执行 `kubectl edit deploy coredns -n kube-system`

2. 将 `podAntiAffinity` 配置按如下方式替换

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coredns
  namespace: kube-system
spec:
  template:
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
             topologyKey: kubernetes.io/hostname
             labelSelector:
               matchExpressions:
                 - key: k8s-app
                   operator: In
                   values:
                     - kube-dns
```
