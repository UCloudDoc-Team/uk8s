# 添加告警规则

监控中心会自带一些默认规则，譬如master组件etcd、kube-apiserver相关规则，prometheus、kubelet等组件相关规则。用户也可以自己新增自定义告警规则，格式基于PromQL表达式定义；

## 添加规则

![](/images/prometheus/addrule.png)


页面中需要填写的内容对应PromQL表达式：

```
groups:
- name: example
  rules:
  - alert: HighErrorRate
    expr: job:request_latency_seconds:mean5m{job="myjob"} > 0.5
    for: 10m
    labels:
      severity: page
    annotations:
      summary: High request latency
      description: description info
```

- 告警组: 对应表达是中name；告警规则分类名称，譬如etcd组件，设置告警组etcd，方便用户查看
- 告警规则：对应表达式中alert；告警规则名称
- 触发条件：对应表达式中expr；基于 PromQL 的表达式告警触发条件，用于计算是否有时间序列满足该条件
- 持续时间：对应表达式中for；触发条件评估等待时间
- 标签：对应表达式中labels；自定义标签，允许用户指定要附加到告警上的一组附加标签。
- 注释：对应表达式中annotations；用于指定一组附加信息，比如用于描述告警详细信息的文字等，annotations的内容在告警产生时会一同作为参数发送到Alertmanager。