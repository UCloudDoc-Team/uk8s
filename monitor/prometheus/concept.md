# 核心概念

{{indexmenu_n>2}}

为了在 Prometheus 的配置和使用中可以更加顺畅，我们对 Prometheus 中的数据模型、metric 类型以及 instance
和 job 等概念做个简要介绍。

\#\#\# 数据模型

Prometheus 中存储的数据为时间序列，是由 metric 的名字和一系列的标签（键值对）唯一标识的，不同的标签则代表不同的时间序列。

\+ **metric 名字：**该名字应该具有语义，一般用于表示 metric 的功能，例如：http\_requests\_total,
表示 http 请求的总数。其中，metric 名字由 ASCII 字符，数字，下划线，以及冒号组成，且必须满足正则表达式
\[a-zA-Z\_:\]\[a-zA-Z0-9\_:\]\*。

\+ **标签：**使同一个时间序列有了不同维度的识别。例如 http\_requests\_total{method="Get"} 表示所有
http 请求中的 Get 请求。当 method="post" 时，则为新的一个 metric。标签中的键由 ASCII
字符，数字，以及下划线组成，且必须满足正则表达式
\[a-zA-Z\_:\]\[a-zA-Z0-9\_:\]\*。

\+ **样本：**实际的时间序列，每个序列包括一个 float64 的值和一个毫秒级的时间戳。

\+ **格式：** 如http\_requests\_total{method="POST",endpoint="/api/tracks"}。

\#\#\# metric 类型

Prometheus 客户端库主要提供四种主要的 metric 类型，分别如下：

**1、Counter**

一种累加的 metric，典型的应用如：请求的个数，结束的任务数， 出现的错误数等等。 例如，查询
http\_requests\_total{method="get", job="kubernetes-nodes",
handler="prometheus"} 返回 8，10 秒后，再次查询，则返回 14。

![](/images/compute/uk8s/monitor/prometheus/counter.png)

\*\* 2、Gauge\*\*

一种常规的 metric，典型的应用如：温度，运行的 goroutines
的个数。例如：go\_goroutines{instance="10.9.81.55",
job="kubernetes-nodes"} 返回值 147，10 秒后返回 124。

![](/images/compute/uk8s/monitor/prometheus/guage.png)

**3、Histogram**

可以理解为柱状图，典型的应用如：请求持续时间，响应大小。可以对观察结果采样，分组及统计。 例如，查询
http\_request\_duration\_microseconds\_sum{job="kubernetes-nodes",
handler="prometheus"} 时，返回结果如下：

![](/images/compute/uk8s/monitor/prometheus/histogram.png)

**4、Summary**

类似于 Histogram, 典型的应用如：请求持续时间，响应大小。提供观测值的 count 和 sum
功能。提供百分位的功能，即可以按百分比划分跟踪结果。

\#\#\# instance\&job

**instance:** 一个单独 scrape 的目标， 一般对应于一个进程。

**jobs:** 一组同类型的 instances

例如，一个 api-server 的 job 可以包含4个 instances：

\+ job: api-server

1.  instance 1: 1.2.3.4:5670
2.  instance 2: 1.2.3.4:5671
3.  instance 3: 1.2.3.4:5672
4.  instance 4: 1.2.3.4:5673

当 scrape 目标时，Prometheus 会自动给这个 scrape
的时间序列附加一些标签以便更好的分别，例如：instance，job。
