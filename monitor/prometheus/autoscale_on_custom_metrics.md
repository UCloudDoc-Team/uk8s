
## 基于自定义指标的容器弹性伸缩

### 前言

HPA(Horizontal Pod Autoscaling)指Kubernetes Pod的横向自动伸缩，其本身也是Kubernetes中的一个API对象。通过此伸缩组件，Kubernetes集群便可以利用监控指标（CPU使用率等）自动扩容或者缩容服务中的Pod数量，当业务需求增加时，HPA将自动增加服务的Pod数量 ，提高系统稳定性，而当业务需求下降时，HPA将自动减少服务的Pod数量，减少对集群资源的请求量(Request)，配合Cluster Autoscaler，还可实现集群规模的自动伸缩，节省IT成本。

需要注意的是，目前默认HPA只能支持根据CPU和内存的阈值检测扩缩容，但也可以通过custom metric api 调用prometheus实现自定义metric，根据更加灵活的监控指标实现弹性伸缩。但HPA不能用于伸缩一些无法进行缩放的控制器如DaemonSet。

### 启用custom.metrics.k8s.io服务

在开始此步骤之前，请确认你已按照前述教程安装了Prometheus。

这里简单介绍下HPA的工作原理，默认情况下，其通过metrics.k8s.io这个本地服务来获取Pod的CPU、Memory指标，CPU和Memory这两者属于核心指标，而metrics.k8s.io服务对应的后端服务一般是metrics server，这是UK8S默认安装的服务。

而如果HPA要通过非CPU、内存的其他指标来伸缩容器，我们则需要部署一套监控系统如Prometheus，让prometheus采集各种指标，但是prometheus采集到的metrics并不能直接给k8s用，因为两者数据格式不兼容，因此另外一个组件prometheus-adapter，将prometheus的metrics数据格式转换成K8S API接口能识别的格式。另外我们还需要在K8S注册一个服务（即custom.metrics,k8s.io），以便HPA能通过/apis/访问。

我们申明一个v1beta1.custom.metrics.k8s.io的APIService，并提交。
```
apiVersion: apiregistration.k8s.io/v1
kind: APIService
metadata:
  name: v1beta1.custom.metrics.k8s.io
spec:
  group: custom.metrics.k8s.io
  groupPriorityMinimum: 100
  insecureSkipTLSVerify: true
  service:
    name: prometheus-adapter
    namespace: monitoring
    port: 443
  version: v1beta1
  versionPriority: 100
```
上述示例中的spec.service.prometheus-adapter在之前文档中已经安装并部署完毕。
提交部署后，我们执行“kubectl get apiservice | grep v1beta1.custom.metrics.k8s.io”，确认该服务可用状态为True。

还可以通过下述方法来查看Prometheus采集了哪些指标。

```
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/ | jq .

kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespace/default/pods/*/ | jq .

curl 127.0.0.1:8080/apis/custom.metrics.k8s.io/v1beta1/namespaces/default/pods/*/http_requests

```

### 修改原有prometheus-adapater的配置文件

为了让HPA能够用到Prometheus采集到的指标，prometheus-adapter通过使用promql来获取指标，然后修改数据格式，并把重新组装的指标和值通过自己的接口暴露。而HPA会通过/apis/custom.metrics.k8s.io/代理到prometheus-adapter的service上来获取这些指标。

如果把Prometheus的所有指标到获取一遍并重新组装，那adapter的效率必然十分低下，因此adapter将需要读取的指标设计成可配置，让用户通过configmap来决定读取Prometheus的哪些监控指标。

关于config的语法规则，详见[config-workthrough](https://github.com/kubernetes-sigs/prometheus-adapter/tree/master/docs)，这里不再赘述。 

由于我们前面已经安装了prometheus-adapter,因此我们现在只需要修改其配置文件并重启即可，原始的配置文件只包含cpu和memory两个Resource metrics，我们只需要在其前面追加需要给HPA用到的metrics即可。

```yaml

apiVersion: v1
data:
  config.yaml: |
    resourceRules:
      cpu:
        containerQuery: sum(rate(container_cpu_usage_seconds_total{<<.LabelMatchers>>,container_name!="POD",container_name!="",pod_name!=""}[1m])) by (<<.GroupBy>>)
        nodeQuery: sum(1 - rate(node_cpu_seconds_total{mode="idle"}[1m]) * on(namespace, pod) group_left(node) node_namespace_pod:kube_pod_info:{<<.LabelMatchers>>}) by (<<.GroupBy>>)
        resources:
          overrides:
            node:
              resource: node
            namespace:
              resource: namespace
            pod_name:
              resource: pod
        containerLabel: container_name
      memory:
        containerQuery: sum(container_memory_working_set_bytes{<<.LabelMatchers>>,container_name!="POD",container_name!="",pod_name!=""}) by (<<.GroupBy>>)
        nodeQuery: sum(node_memory_MemTotal_bytes{job="node-exporter",<<.LabelMatchers>>} - node_memory_MemAvailable_bytes{job="node-exporter",<<.LabelMatchers>>}) by (<<.GroupBy>>)
        resources:
          overrides:
            instance:
              resource: node
            namespace:
              resource: namespace
            pod_name:
              resource: pod
        containerLabel: container_name
      window: 1m
kind: ConfigMap
metadata:
  name: adapter-config
  namespace: monitoring
```

我们以常见的请求数为例，追加一个指标，其名称为http_request,资源类型为Pod。

```yaml
apiVersion: v1
data:
  config.yaml: |
    rules:
    - seriesQuery: '{__name__=~"^http_requests_.*",kubernetes_pod_name!="",kubernetes_namespace!=""}'
      seriesFilters: []
      resources:
        overrides:
          kubernetes_namespace:
            resource: namespace
          kubernetes_pod_name:
            resource: pod
      name:
        matches: ^(.*)_(total)$
        as: "${1}"
      metricsQuery: sum(rate(<<.Series>>{<<.LabelMatchers>>}[1m])) by (<<.GroupBy>>)
    resourceRules:
      cpu:
        containerQuery: sum(rate(container_cpu_usage_seconds_total{<<.LabelMatchers>>,container_name!="POD",container_name!="",pod_name!=""}[1m])) by (<<.GroupBy>>)
        nodeQuery: sum(1 - rate(node_cpu_seconds_total{mode="idle"}[1m]) * on(namespace, pod) group_left(node) node_namespace_pod:kube_pod_info:{<<.LabelMatchers>>}) by (<<.GroupBy>>)
        resources:
          overrides:
            node:
              resource: node
            namespace:
              resource: namespace
            pod_name:
              resource: pod
        containerLabel: container_name
      memory:
        containerQuery: sum(container_memory_working_set_bytes{<<.LabelMatchers>>,container_name!="POD",container_name!="",pod_name!=""}) by (<<.GroupBy>>)
        nodeQuery: sum(node_memory_MemTotal_bytes{job="node-exporter",<<.LabelMatchers>>} - node_memory_MemAvailable_bytes{job="node-exporter",<<.LabelMatchers>>}) by (<<.GroupBy>>)
        resources:
          overrides:
            instance:
              resource: node
            namespace:
              resource: namespace
            pod_name:
              resource: pod
        containerLabel: container_name
      window: 1m
kind: ConfigMap
metadata:
  name: adapter-config
  namespace: monitoring
```

修改完毕并提交后，如果为了立马生效，我们可以删除掉原有的prometheus-adapter的Pod，使得配置文件立马生效。

当然只有这些指标还是略微不够，社区提供了一个rules的示例： [adapater-config标准样例](https://github.com/kubernetes-sigs/prometheus-adapter/blob/master/docs/sample-config.yaml)


