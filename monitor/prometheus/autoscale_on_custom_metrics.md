## 基于自定义指标的容器弹性伸缩

### 前言

HPA(Horizontal Pod Autoscaling)指Kubernetes
Pod的横向自动伸缩，其本身也是Kubernetes中的一个API对象。通过此伸缩组件，Kubernetes集群便可以利用监控指标（CPU使用率等）自动扩容或者缩容服务中的Pod数量。

- 当业务需求增加时，HPA将自动增加服务的Pod数量
，提高系统稳定性
- 当业务需求下降时，HPA将自动减少服务的Pod数量，减少对集群资源的请求量(Request)，配合Cluster Autoscaler，还可实现集群规模的自动伸缩，节省IT成本

需要注意的是，目前默认HPA只能支持根据CPU和内存的阈值检测扩缩容，不过Kubernetes也可以通过custom metric api
调用prometheus实现自定义metric，根据更加灵活的监控指标实现弹性伸缩。

> 注：HPA不能用于伸缩一些无法进行缩放的控制器，如：DaemonSet。

## 原理

这里简单介绍下HPA的工作原理，默认情况下，其通过metrics.k8s.io这个本地服务来获取Pod的CPU、Memory指标，CPU和Memory这两者属于核心指标，而metrics.k8s.io服务对应的后端服务一般是metrics
server，metrics
server服务在UK8S会默认安装。

如果HPA要通过非CPU、内存的其他指标来伸缩容器，则需要部署一套监控系统如Prometheus，让prometheus采集各种指标，但是prometheus采集到的metrics并不能直接给k8s用，因为两者数据格式不兼容，还需要一个组件prometheus-adapter，将prometheus的metrics数据格式转换成K8S。

## 部署

在开始此步骤之前，请确认
- 在uk8s控制台-详情-监控中心 已开启prometheus监控
- 本地helm3.x 已安装 
- uk8s集群上metrics-server服务已经部署

#### 安装prometheus-adapter

 [Prometheus Adapter](https://github.com/kubernetes-sigs/prometheus-adapter)该组件负责将 `Prometheus` 指标转换为 Kubernetes 自定义指标 API 格式，你可以在已安装 Helm 3.x 且能够通过 kubectl 连接到集群的主机上，使用以下命令进行部署：
```shell
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  -n uk8s-monitor \
  --set prometheus.url=http://uk8s-prometheus.uk8s-monitor.svc \
  --set image.repository=uhub.service.ucloud.cn/uk8s/prometheus-adapter \
  --set image.tag=v0.12.0
```
#### 启用custom.metrics.k8s.io服务


部署`Prometheus Adapter`后还需要将自定义指标 API 注册到 API 聚合器（Kubernetes 主 API 服务器的一部分）。为此，我们需要创建一个 APIService 自定义资源，它的作用是让 Kubernetes 的控制器（比如 HPA 自动扩缩容）可以通过标准的 API 地址访问 `prometheus-adapter` 提供的自定义指标。

我们申明一个custom.metrics.k8s.io的APIService，并执行命令部署到集群：

```yaml
apiVersion: apiregistration.k8s.io/v1
kind: APIService
metadata:
  name: v1beta2.custom.metrics.k8s.io
spec:
  group: custom.metrics.k8s.io
  groupPriorityMinimum: 100
  insecureSkipTLSVerify: true
  service:
    name: prometheus-adapter
    namespace: uk8s-monitor	
  version: v1beta2
  versionPriority: 100
```


## 测试
本演练将介绍在集群上设置 Prometheus 适配器的基础知识，以及如何配置自动缩放器以使用来自适配器的应用程序指标。更多详细信息，请参考 [Prometheus Adapter Walkthrough](https://github.com/kubernetes-sigs/prometheus-adapter/blob/master/docs/walkthrough.md)。
#### 部署测试服务
将您的应用程序部署到集群中，并通过服务公开，以便您可以向其发送流量并从中获取指标：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-app
  labels:
    app: sample-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sample-app
  template:
    metadata:
      labels:
        app: sample-app
    spec:
      containers:
      - image: uhub.service.ucloud.cn/uk8s/autoscale-demo:v0.1.2
        name: metrics-provider
        ports:
        - name: http
          containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: sample-app
  name: sample-app
spec:
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 8080
  selector:
    app: sample-app
  type: ClusterIP
```
现在，检查您的应用程序，确保它公开了指标，并通过 http_requests_total 指标计算访问指标页面的次数。您可以在能够访问 Pod 的主机（如 master 节点）上使用以下命令进行测试：
```shell
curl http://$(kubectl get pod -l app=sample-app -o jsonpath='{.items[0].status.podIP}'):8080
```
请注意，每次访问该页面时，计数器都会增加。

#### 配置HPA
现在，您需要确保能够根据该指标自动扩缩应用程序，以便为发布做好准备。您可以使用如下所示的 Horizo​​ntalPodAutoscaler 来实现自动扩缩：
```yaml
kind: HorizontalPodAutoscaler
apiVersion: autoscaling/v2
metadata:
  name: sample-app
spec:
  scaleTargetRef:
    # 指定要进行自动扩缩容的目标资源，这里是名为 sample-app 的 Deployment
    apiVersion: apps/v1
    kind: Deployment
    name: sample-app
  # 设置副本数的范围：最少1个，最多10个
  minReplicas: 1
  maxReplicas: 10
  metrics:
  # 使用类型为 Pods 的自定义指标，对每个 Pod 的该指标进行平均计算
  - type: Pods
    pods:
      # 指定使用的指标名称为 http_requests，这是一个自定义指标（custom metrics）
      # 当前尚未生效，需要 Prometheus Adapter 配置支持该指标
      metric:
        name: http_requests
      # 指定扩缩容的触发阈值为每个 Pod 平均 500m（500 毫次请求/秒）
      # 即每个 Pod 每2秒处理1次请求时，HPA 会维持当前副本数
      # 如果超出此速率，HPA 会自动扩容；反之则缩容
      target:
        type: Value
        averageValue: 500m

```
#### 监控配置
为了监控你的应用程序，你需要设置一个指向该应用程序的 ServiceMonitor。假设你已经设置了 Prometheus 实例，以便在以下 app: sample-app 标签，创建一个 ServiceMonitor 来通过 服务：

前提条件：你的应用服务需要满足以下要求，才能被 Prometheus 成功采集指标：

- 服务具有标签 app: sample-app（或与 ServiceMonitor 中 selector 匹配的标签）；

- 服务已通过命名端口（如 http）暴露了指标接口；

- 应用在该端口上暴露了标准的 Prometheus 指标，默认抓取路径为 /metrics，也可以通过 endpoints.path 字段自定义指标路径。

```shell
kind: ServiceMonitor
apiVersion: monitoring.coreos.com/v1
metadata:
  name: sample-app
  labels:
    app: sample-app
  namespace: default
spec:
  selector:
    matchLabels:
      app: sample-app
  endpoints:
  - port: http
```

现在，你应该可以看到你的指标（ http_requests_total ）出现在你的 Prometheus 实例中。通过仪表盘查找它们，并确保它们具有 namespace 和 pod 标签。如果不匹配，请检查服务监视器上的标签是否与 Prometheus CRD 上的标签匹配。


#### 配置适配器Prometheus Adapter
现在您已经拥有一个正在运行的 Prometheus 副本来监控您的应用程序，您需要部署适配器，它知道如何与 Kubernetes 和 Prometheus 进行通信，充当两者之间的翻译器。

不过，为了使自定义指标能够在 Kubernetes 中展示，还需要配置适配器的规则，告诉它如何从 Prometheus 中提取指标并转换为 Kubernetes 支持的格式：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: adapter-config
  namespace: uk8s-monitor
data:
  config.yaml: |-
    # Prometheus Adapter 自定义指标规则配置
    "rules":
    - "seriesQuery": |
         {namespace!="",__name__!~"^container_.*"}  # 查询所有不以 container_ 开头、带有 namespace 标签的指标
      "resources":
        "template": "<<.Resource>>"  # 映射到 K8s 中的资源，如 Pod、Deployment 等
      "name":
        "matches": "^(.*)_total"     # 匹配所有以 _total 结尾的指标（如 http_requests_total）
        "as": ""                     # 保持原指标名称
      "metricsQuery": |
        sum by (<<.GroupBy>>) (      # 按指定标签聚合
          irate (
            <<.Series>>{<<.LabelMatchers>>}[1m]  # 使用 irate 函数计算每秒速率，时间窗口为 1 分钟
          )
        )

```
> 📘 参考文档：官方 Prometheus Adapter 配置说明请见 [Metrics Discovery and Presentation Configuration](https://github.com/kubernetes-sigs/prometheus-adapter/blob/master/docs/config.md)

重启prometheus-adapter以生效配置

```shell
kubectl rollout restart deployment prometheus-adapter -n uk8s-monitor
```


您可以使用 kubectl get --raw 检查指标的值，它会向 Kubernetes API 服务器发送原始 GET 请求，自动注入身份验证信息：

```shell
# 该命令用于查询命名空间 default 下标签为 app=sample-app 的所有 Pod 的自定义指标 http_requests 的当前值。
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta2/namespaces/default/pods/*/http_requests?selector=app%3Dsample-app" | jq .
```
由于适配器的配置，累积指标 http_requests_total 已转换为速率指标， pods/http_requests ，用于测量 1 分钟间隔内的每秒请求数。该值目前应该接近于零，因为除了 Prometheus 的常规指标收集外，您的应用没有任何流量。

如果一切正常，执行上述命令将返回类似以下内容的输出:

```json
{
  "kind": "MetricValueList",
  "apiVersion": "custom.metrics.k8s.io/v1beta2",
  "metadata": {},
  "items": [
    {
      "describedObject": {
        "kind": "Pod",
        "namespace": "default",
        "name": "sample-app-85d5996dc6-q4s74",
        "apiVersion": "/v1"
      },
      "metric": {
        "name": "http_requests",
        "selector": null
      },
      "timestamp": "2025-04-29T09:59:22Z",
      "value": "52m"
    }
  ]
}
```

#### 测试
尝试使用 curl 生成一定流量：
```shell
timeout 1m bash -c '
  while sleep 0.1; do
    curl http://$(kubectl get pod -l app=sample-app -o jsonpath="{.items[0].status.podIP}"):8080
  done
'
```
如果您再次查看 HPA，您应该看到最后观察到的指标值大致对应于您的请求率，并且 HPA 最近扩展了您的应用程序。

现在，您的应用已根据 HTTP 请求自动扩展，一切准备就绪，可以正式发布了！如果您暂时搁置该应用一段时间，HPA 应该会缩减其规模，这样您就可以为正式发布节省宝贵的预算。
