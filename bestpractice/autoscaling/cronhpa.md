## 定时伸缩

### 前言

HPA(Horizontal Pod Autoscaling)指Kubernetes Pod的横向自动伸缩，是kubernetes集群利用监控指标自动扩容或者缩容服务中的Pod数量，其中监控指标利用CPU内存等。定时伸缩不同的是通过定时器进行Pod的数量的伸缩，用于已知的高并发，在高并发来临前提前扩容业务进行应对。

### 在UK8S使用定时伸缩

#### 1.开启定时伸缩

用户在UK8S集群中点击插件tab页，选择定时伸缩，点击立即开启

![](/images/bestpractice/autoscaling/opencronhpa.png)

#### 2.添加定时伸缩条件

用户点击添加进入新增定时任务页面，在页面中需要输入定时器的名字、选择需要伸缩的对象、执行计划的时间和目标Pod数量。

![](/images/bestpractice/autoscaling/createcronhpa.png)

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

如图，执行时间为UTC时间是因为CronTab的命令时间为UTC时间，方便于用户填写时间命令，实际真实执行时间用户可以进行+8小时计算。


![](/images/bestpractice/autoscaling/createcronhpa.png)


### 验证操作


我们针对nginx-deployment这个应用设置了up5和down2两个执行计划，分别设置的是`40 8 * * *`和`50 8 * * *`，我们+8小时计算，应用将在16点40分扩容到5个，在16点50分缩容到2个，并每天执行。

![](/images/bestpractice/autoscaling/testcronhpa.png)

16点40分，扩容到5个执行成功

![](/images/bestpractice/autoscaling/1cronhpa.png)

我们查看nginx-deployment已经扩容到了5个。

![](/images/bestpractice/autoscaling/2cronhpa.png)

16点50分，缩容到2个执行成功

![](/images/bestpractice/autoscaling/3cronhpa.png)

我们查看nginx-deployment已经缩容到了2个。

![](/images/bestpractice/autoscaling/4cronhpa.png)