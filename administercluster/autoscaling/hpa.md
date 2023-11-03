# HPA

## 前言

HPA(Horizontal Pod Autoscaling)指Kubernetes
Pod的横向自动伸缩，其本身也是Kubernetes中的一个API对象。通过此伸缩组件，Kubernetes集群便可以利用监控指标（CPU使用率等）自动扩容或者缩容服务中的Pod数量，当业务需求增加时，HPA将自动增加服务的Pod数量
，提高系统稳定性，而当业务需求下降时，HPA将自动减少服务的Pod数量，减少对集群资源的请求量(Request)，配合Cluster Autoscaler，还可实现集群规模的自动伸缩，节省IT成本。

需要注意的是，目前默认HPA只能支持根据CPU和内存的阈值检测扩缩容，但也可以通过custom metric api
调用prometheus实现自定义metric，根据更加灵活的监控指标实现弹性伸缩。但HPA不能用于伸缩一些无法进行缩放的控制器如DaemonSet。

## 工作原理

![](/images/administercluster/autoscaling/hpa.png)

HPA在K8S中被设计为一个Controller，可以简单的使用kubectl autoscale命令来创建。HPA
Controller默认30秒轮询一次，查询指定的Resource中（Deployment,RC）的资源使用率，并且将其与创建HPA时设定的指标做对比，从而实现自动伸缩的功能。

创建了HPA后，HPA会从Metric
Server（UK8S中不使用Heapster）获取如某个Deployment中每一个Pod利用率的平均值，然后和HPA中定义的指标进行对比，同时计算出需要伸缩的具体值并进行操作。其算法模型大致如下：

```
desiredReplicas = ceil[currentReplicas * ( currentMetricValue / desiredMetricValue )]
```

例如，如果当前所有Pod的平均CPU使用量是200m，而期望值为100m，那副本数(replicas)将会翻倍。而如果当前的值为50m，那就需要减去一半的副本数(replicas)。

需要注意的是，HPA Controller中有一个tolerance（容忍力）的概念，当currentMetricValue /
desiredMetricValue的比率接近1.0时，并不会触发伸缩。默认的方差为0.1，这主要是出于系统稳定性的考虑，避免集群震荡。例如，HPA的策略为cpu使用率高于50%触发扩容，那么只有当使用率大于55%时才会触发扩容动作，HPA通过扩缩Pod，尽力把Pod的使用率控制在这个45%~55%范围之间。你可以通过--horizontal-pod-autoscaler-tolerance这个参数来调整方差值。

在每次扩容和缩容后都有一个窗口时间，在执行伸缩操作后，在这个窗口时间内，不会在进行伸缩操作，可以理解为类似技能的冷却时间。默认扩容为3分钟(–-horizontal-pod-autoscaler-upscale-delay)，缩容为5分钟(–-horizontal-pod-autoscaler-downscale-delay)。

最后值得注意的是，**Pod没有设置 Request 时，HPA 不会工作。**

## HPA 对象控制台管理

HPA 对象的添加、查看和删除，可在 UK8S 集群管理控制台**集群伸缩**页面**弹性伸缩(HPA)** 子页进行。

点击**表单添加**可通过控制台页面添加 HPA 对象，您也可以通过 yaml 进行添加。

| 配置项      | 描述                                      |
| -------- | --------------------------------------- |
| 命名空间     | HPA 对象所属 Namespace 命名空间                 |
| HPA 对象名称 | 名称必须以小写字母开头，只能包含小写字母、数字、小数点(.)和中划线(-)   |
| 应用类型     | 支持 Deployment 及 StatefulSet 控制器         |
| 应用名称     | 选择需要进行弹性伸缩的 Deployment 及 StatefulSet 对象 |
| 扩容阈值     | 扩缩容阈值，支持设置 CPU 及内存利用率                   |
| 伸缩区间     | Pod 副本数量范围                              |

**HPA API对象详解**

UK8S 控制台通过 **autoscaling/v2beta2** 版本 Kubernetes API 进行 HPA 对象的创建。
> 注意：集群版本1.26之前请使用`autoscaling/v2beta2`，集群版本1.26开始请使用`autoscaling/v2`

```yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: nginxtest
  namespace: default
spec:
  maxReplicas: 5 #最大副本数
  minReplicas: 1 #最小副本数
  metrics:
    # 设置触发伸缩的 CPU 利用率
    - type: Resource
      resource:
        name: cpu
        target:
          averageUtilization: 50
          type: Utilization
    # 设置触发伸缩的 MEM 利用率
    - type: Resource
      resource:
        name: memory
        target:
          averageUtilization: 50
          type: Utilization     
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment #需要伸缩的资源类型
    name: nginxtest  #需要伸缩的资源名称
```

## 案例实践

下面我们用一个简单的例子来看下HPA如何工作。

### 1. 部署测试应用

```
kubectl apply -f  https://docs.ucloud.cn/uk8s/yaml/hpa/hpa-example.yaml
```

这是一个计算密集型的PHP应用，代码示例如下：

```
<?php
  $x = 0.0001;
  for ($i = 0; $i <= 1000000; $i++) {
    $x += sqrt($x);
  }
  echo "OK!";
?>
```

### 2. 为测试应用开启HPA

```
kubectl apply -f  https://docs.ucloud.cn/uk8s/yaml/hpa/hpa.yaml
```

### 3. 部署压测工具

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/hpa/load.yaml
```

压测工具是一个busybox容器，容器启动后循环访问测试应用。

```
while true; do wget -q -O- http://hap-example.default.svc.cluster.local; done
```

### 4. 查看测试应用负载情况

```
kubectl top pods | grep hpa-example
```

### 5. 当测试应用的CPU平均负载超过55%后，我们发现HPA将开始扩容Pod

```
kubectl get deploy | grep hpa-example
```
