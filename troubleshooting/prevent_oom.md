# 预防节点OOM

该文档为预防节点OOM的开源方案，不提供SLA，仅做参考，请**谨慎使用**。


## 原理

在用户态实时获取available内存，当小于阈值时开始依据策略发送sigterm与kill信号杀死进程

## 使用方法

1. -M 参数实现oom-protector内存杀进程阈值, 第一个参数为sigterm信号阈值，第二个参数为kill信号阈值，以','分割，单位只支持KB；

2. --avoid参数可以避免杀死符合条件的进程；

3. --prefer参数可以优先杀死符合条件的进程；

##  进程删除主要依据

根据oom_score 分值来杀进程，如系统上有自行启动的进程且oom_score_adj未设置为-1000，就有被杀死的可能。

**备注：** 该程序无法阻止瞬时内存暴增引发的内存宕机，依旧需要设置pod合理的资源requests与limits。


## 部署示例

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  labels:
    app: oom-protector
  name: oom-protector
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: oom-protector
  template:
    metadata:
      labels:
        app: oom-protector
    spec:
      hostPID: true
      containers:
      - image: uhub.service.ucloud.cn/uk8s/earlyoom:alpine
        name: earlyoom
        args:
        - -p
        - -M  
        - "307200,204800"
        - --avoid  
        - "docker|kubelet|containerd|sshd"
        securityContext:
          capabilities:
            add:
            - KILL
        resources:
          requests:
            memory: "32Mi"
            cpu: "50m"
          limits:
            memory: "64Mi"
            cpu: "100m"
```






