# Pod故障排查

在Kubernetes中发布应用时，我们经常会遇到Pod出现异常的情况，如Pod长时间处于Pending状态，或者反复重启，下面介绍下如何各种Pod异常的情况。


## 常用命令

在Pod故障排查的过程中，我们基本上通过以下命令来获取有效信息，确认故障原因。

1. 查看Pod 状态

```bash
 kubectl get po <pod-name> -o wide 


```



