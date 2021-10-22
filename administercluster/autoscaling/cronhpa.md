# 定时伸缩

HPA(Horizontal Pod Autoscaling) 指 Kubernetes Pod 的横向自动伸缩，是 Kubernetes 集群利用监控指标自动扩容或者缩容服务中的 Pod 数量，其中监控指标利用 CPU 内存等。定时伸缩不同的是通过定时器进行 Pod 的数量的伸缩，用于已知的高并发，在高并发来临前提前扩容业务进行应对。

## 1. 在UK8S使用定时伸缩

### 1.1 开启定时伸缩

在 UK8S 集群管理页面中点击**集群伸缩**标签页，选择**定时伸缩(CronHPA)**，点击立即开启安装 CronHPA 控制插件，开启定时伸缩功能。

![](/images/administercluster/autoscaling/opencronhpa.png)

### 1.2 添加定时伸缩条件

用户点击添加进入新增定时任务页面，在页面中需要输入定时器的名字、选择需要伸缩的对象、执行计划的时间和目标 Pod 数量。如勾选「单次执行」选项，则表明该定时伸缩任务仅需执行一次，非周期性执行。

### 1.2 针对计划表语法说明

针对计划表语法使用和 CronTab 一致的语法，下面列举几种常用语法，详细语法请参考[链接](https://wiki.archlinux.org/index.php/Cron_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)#Crontab_%E6%A0%BC%E5%BC%8F)

Crontab格式（前5位为时间选项，这里我们只用到了前5位）

```
<分钟> <小时> <日> <月份> <星期> <命令>
```

每天一次，0点0分执行

```
0 0 * * *
```

每周一次，0点0分执行

```
0 0 * * 0
```

每月一次，0点0分执行

```
0 0 1 * *
```

> ⚠️ CronTab 的命令时间为 UTC 时间，任务真实执行时间用户可以进行 +8 小时计算。

### 1.3 示例 yaml

我们针对 nginx-deployment 这个应用设置了 up5 和 down2 两个执行计划，分别设置的是 `40 8 * * *` 和 `50 8 * * *`，即应用将在北京时间 16 点 40 分扩容到 5 个，在 16 点 50 分缩容到 2 个，并每天执行。

```yaml
apiVersion: autoscaling.ucloud.cn/v1
kind: CronHorizontalPodAutoscaler
metadata:
  labels:
  controller-tools.k8s.io: "1.0"
  name: "nginx-cronhpa"
  namespace: default
spec:
  jobs: # 执行计划，支持最多在同一 CronHPA 中添加 10 个执行计划
  - name: "up5"
    schedule: "40 8 * * * "
    targetSize: 5
    runOnce: false
  - name: "down2"
    schedule: "50 8 * * * "
    targetSize: 2
    runOnce: false 
  scaleTargetRef: # 目标执行对象，支持 Deployment、StatefulSet 及 HPA 资源对象
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
```

## 2. CronHPA 定时伸缩支持 HPA 对象

CronHPA 插件支持在创建时，选择原有的 HPA 对象，兼容规则如下：

| HPA 配置<br>min/max| CronHPA<br>目标Pod数 | Deployment<br>当前 Pod 数 | 扩缩结果 | 说明 |
|:-----:|:-----:|:-----:|-----|-----|
|<div style="width:55pt">1/10</div>|<div style="width:60pt">5</div>|5|<div style="width:90pt">HPA：5/10<br>Deployment：5</div>|CronHPA 目标副本数 > HPA 副本数下限，修改 HPA 中的副本数下限|
|5/10|4|5|HPA：4/10<br>Deployment：5|CronHPA 目标副本数 < HPA 副本数下限，修改 HPA 中的副本数下限<br>当业务下降低于 HPA 设定阈值范围时，HPA 将调整 Deployment 中副本数为 4|
|1/10|11|5|HPA：11/11<br>Deployment：11|CronHPA 目标副本数 > HPA 副本数上限，同时修改 HPA 中的副本数上限与下限|
