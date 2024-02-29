# kubectl 常见问题

## 1. kubectl top 命令报错

该情况一般有以下两种可能

1. kube-system下面metrics-server Pod没有正常工作，可以通过`kubectl get pods -n kube-system`进行查看
2. `metrics.k8s.io`
   API地址被错误重定向，可以执行`kubectl get apiservice v1beta1.metrics.k8s.io`查看重定向到的service名称，并确认service当前是否可用及是否对外暴露了`v1beta1.metrics.k8s.io`接口。默认重定向地址为`kube-system/metrics-server`

情况二一般出现在部署prometheus，且prometheus提供的接口不支持v1beta1.metrics.k8s.io时。如果不需要自定义HPA指标，其实不需要此重定向操作。如果属于情况二，可以按照下面步骤操作。

1. 确认配置中的的prometheus
   service可用，并根据需要[自定义HPA指标](/uk8s/monitor/prometheus/autoscale_on_custom_metrics#启用custommetricsk8sio服务)
2. 重新部署执行下面yaml文件，回退到普通metrics server，Grafana等不依赖此api。
3. 注意，如果您之前已经使用了自定义HPA指标，且处于线上环境，建议您仅确认prometheus service可用即可。回退到普通metrics
   server可能导致之前的自定义HPA指标失效，请谨慎操作。

```
apiVersion: apiregistration.k8s.io/v1beta1
kind: APIService
metadata:
  name: v1beta1.metrics.k8s.io
spec:
  service:
    name: metrics-server
    namespace: kube-system
  group: metrics.k8s.io
  version: v1beta1
  insecureSkipTLSVerify: true
  groupPriorityMinimum: 100
  versionPriority: 100
```