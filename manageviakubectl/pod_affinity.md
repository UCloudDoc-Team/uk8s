## 将pod打散

- 有些情况下我们希望将服务分散在各个节点，例子如下

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  selector:
    matchLabels:
      app: nginx # 需要下面的的标签一致
  replicas: 3
  template:
    metadata:
      labels:
        app: nginx # 需要下面的matchExpressions的标签一致
    spec:
      affinity:
        podAntiAffinity: # 反亲和
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app #  注意这里的标签要和上面的标签一致
                  operator: In
                  values:
                  - nginx
              topologyKey: "kubernetes.io/hostname"
      containers:
      - name: nginx
        image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
```

更多调度方式参考官方[文档](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/assign-pod-node/)
