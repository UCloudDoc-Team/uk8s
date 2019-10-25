
## HPA

### 前言

HPA(Horizontal Pod Autoscaling)指Kubernetes Pod的横向自动伸缩，其本身也是Kubernetes中的一个API对象。通过此伸缩组件，Kubernetes集群便可以利用监控指标（CPU使用率等）自动扩容或者缩容服务中的Pod数量，当业务需求增加时，HPA将自动增加服务的Pod数量 ，提高系统稳定性，而当业务需求下降时，HPA将自动减少服务的Pod数量，减少对集群资源的请求量(Request)，配合Cluster Autoscaler，还可实现集群规模的自动伸缩，节省IT成本。

需要注意的是，目前默认HPA只能支持根据CPU和内存的阀值检测扩缩容，但也可以通过custom metric api 调用prometheus实现自定义metric，根据更加灵活的监控指标实现弹性伸缩。但HPA不能用于伸缩一些无法进行缩放的控制器如DaemonSet。

### 工作原理
![](/images/bestpractice/autoscaling/hpa.png)

HPA在K8S中被设计为一个Controller，可以简单的使用kubectl autoscale命令来创建。HPA Controller默认30秒轮询一次，查询指定的Resource中（Deployment,RC）的资源使用率，并且将其与创建HPA时设定的指标做对比，从而实现自动伸缩的功能。

创建了HPA后，HPA会从Metric Server（UK8S中不使用Heapster）获取如某个Deployment中每一个Pod利用率的平均值，然后和HPA中定义的指标进行对比，同时计算出需要伸缩的具体值并进行操作。其算法模型大致如下：

```
desiredReplicas = ceil[currentReplicas * ( currentMetricValue / desiredMetricValue )]

```

例如，如果当前所有Pod的平均CPU使用量是200m，而期望值为100m，那副本数(replicas)将会翻倍。而如果当前的值为50m，那就需要减去一半的副本数(replicas)。

需要注意的是，HPA Controller中有一个tolerance（容忍力）的概念，当currentMetricValue / desiredMetricValue的比率接近1.0时，并不会触发伸缩。默认的方差为0.1，这主要是出于系统稳定性的考虑，避免集群震荡。例如，HPA的策略为cpu使用率高于50%触发扩容，那么只有当使用率大于55%时才会触发扩容动作，HPA通过扩缩Pod，尽力把Pod的使用率控制在这个45%~55%范围之间。你可以通过--horizontal-pod-autoscaler-tolerance这个参数来调整方差值。

在每次扩容和缩容后都有一个窗口时间，在执行伸缩操作后，在这个窗口时间内，不会在进行伸缩操作，可以理解为类似技能的冷却时间。默认扩容为3分钟(–-horizontal-pod-autoscaler-upscale-delay)，缩容为5分钟(–-horizontal-pod-autoscaler-downscale-delay)。

最后值得注意的是，**Pod没有设置request时，HPA不会工作。**

### HPA API对象详解

```

apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: nginxtest
  namespace: default
spec:
  maxReplicas: 5 #最大副本数
  minReplicas: 1 #最小副本数
  scaleTargetRef:
    apiVersion: extensions/v1beta1
    kind: Deployment #需要伸缩的资源类型
    name: nginxtest  #需要伸缩的资源名称
  targetCPUUtilizationPercentage: 50 #触发伸缩的cpu使用率
status:
  currentCPUUtilizationPercentage: 48 #当前资源下pod的cpu使用率
  currentReplicas: 1 #当前的副本数
  desiredReplicas: 1 #期望的副本数
```

### 案例实践

下面我们用一个简单的例子来看下HPA如何工作。

#### 1、部署测试应用

```
kubectl apply -f  http://uk8s.cn-bj.ufileos.com/autoscailing/hpa/hpa-example.yaml
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

#### 2、为测试应用开启HPA

```
kubectl apply -f  http://uk8s.cn-bj.ufileos.com/autoscailing/hpa/hpa.yaml
```

#### 3、部署压测工具

```
kubectl apply -f http://uk8s.cn-bj.ufileos.com/autoscailing/hpa/load.yaml
```

压测工具是一个busybox容器，容器启动后循环访问测试应用。

```
while true; do wget -q -O- http://hap-example.default.svc.cluster.local; done
```

#### 4、查看测试应用负载情况

```
kubectl top pods | grep hpa-example
```

#### 5、当测试应用的CPU平均负载超过55%后，我们发现HPA将开始扩容Pod

```
kubectl get deploy | grep hpa-example
```

### 总结

本文主要介绍了HPA的相关原理和使用方法，HPA这个组件可以对应用的容器数量做自动伸缩，可以有效提升服务的稳定性。
