## 定时伸缩

### 前言

HPA(Horizontal Pod Autoscaling)指Kubernetes Pod的横向自动伸缩，是kubernetes集群利用监控指标自动扩容或者缩容服务中的Pod数量，其中监控指标利用CPU内存等。定时伸缩不同的是通过定时器进行Pod的数量的伸缩，用于已知的高并发，在高并发来临前提前扩容业务进行应对。

### 在UK8S使用定时伸缩

#### 1.开启定时伸缩

用户在UK8S集群中点击插件tab页，选择定时伸缩，点击立即开启

![](/images/administercluster/autoscaling/opencronhpa.png)

#### 2.添加定时伸缩条件

用户点击添加进入新增定时任务页面，在页面中需要输入定时器的名字、选择需要伸缩的对象、执行计划的时间和目标Pod数量。如勾选「单次执行」选项，则表明该定时伸缩任务仅需执行一次，非周期性执行。

![](/images/administercluster/autoscaling/createcronhpa.png)

#### 针对计划表语法说明

针对计划表语法使用和CronTab一致的语法，下面列举几种常用语法，详细语法请参考[链接](https://wiki.archlinux.org/index.php/Cron_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)#Crontab_%E6%A0%BC%E5%BC%8F)

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

#### 针对UTC时间说明

如图，执行时间为 UTC 时间是因为 CronTab 的命令时间为UTC时间，方便于用户填写时间命令，实际真实执行时间用户可以进行+8小时计算。


![](/images/administercluster/autoscaling/createcronhpa.png)


### 验证操作


我们针对nginx-deployment这个应用设置了up5和down2两个执行计划，分别设置的是`40 8 * * *`和`50 8 * * *`，我们+8小时计算，应用将在16点40分扩容到5个，在16点50分缩容到2个，并每天执行。

![](/images/administercluster/autoscaling/testcronhpa.png)

16点40分，扩容到5个执行成功

![](/images/administercluster/autoscaling/1cronhpa.png)

我们查看nginx-deployment已经扩容到了5个。

![](/images/administercluster/autoscaling/2cronhpa.png)

16点50分，缩容到2个执行成功

![](/images/administercluster/autoscaling/3cronhpa.png)

我们查看nginx-deployment已经缩容到了2个。

![](/images/administercluster/autoscaling/4cronhpa.png)

### CronHPA 定时伸缩支持 HPA 对象

CronHPA 插件支持在创建时，选择原有的 HPA 对象，兼容规则如下：

| HPA 配置<br>min/max| CronHPA<br>目标 Pod 数 | Deployment<br>当前 Pod 数 | 扩缩结果 | 说明 |
|-----|-----|-----|-----|-----|
|1/10|5|5|HPA（min/max）：5/10<br>Deployment：5|当CronHPA中的目标副本数大于HPA中的副本数下限，修改HPA中的副本数下限|
|5/10|4|5|HPA（min/max）：4/10<br>Deployment：5|当CronHPA中的目标副本数小于HPA中的副本数下限，修改HPA中的副本数下限<br>当业务下降低于设定阈值范围时，HPA 将将 Deployment 中副本数调整为 4|
|1/10|11|5|HPA（min/max）：11/11<br>Deployment：11|当CronHPA中的目标副本数大于HPA中的副本数上限，同时修改HPA中的副本数上限与下限|