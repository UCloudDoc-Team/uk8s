# node-problem-detector 资源修改

由于 node-problem-detector 默认给的配置资源太低，可能会导致以下问题

* 系统出现僵尸进程
* node 节点读 IO 变高
* npd 进程会出现报错： `Timeout when running plugin "./config/plugin/network_problem.sh": state -signal`

需要调整 node-problem-detector 的资源配置，操作步骤如下

### 1. 获取 DaemonSet 的名称

```yaml
kubectl get ds -n kube-system |grep node-problem-detector
node-problem-detector            1         1         1       1            1           <none>          236d
```

找到 `DaemonSet` 的名称，一般叫做 node-problem-detector，或者叫做 ack-node-problem-detector-daemonset

### 2. 编辑 DaemonSet 资源，修改 resources 配置

通过 edit 命令修改资源的配置，执行下面命令之后，会进入 vim 模式

```yaml
kubectl edit ds node-problem-detector -n kube-system
```

修改 resource 对应的内容为 100m 和 100Mi ，保存退出即可，node-problem-detector 对应的 pod 会自动重启

```yaml
        resources:
          limits:
            cpu: 100m
            memory: 100Mi
          requests:
            cpu: 100m
            memory: 100Mi
```

### 3. 验证 pod 正常运行

```
kubectl get pod -n kube-system |grep node-problem-detector
```

确认 pod 正常运行 



## 常见问题：

#### 1. 修改会影响我们的应用服务吗？

不会， node-problem-detector 的作用是检查 node 节点是否存在异常，修改 node-problem-detector 不会影响应用服务


### 2. 那些集群需要修改？

我们已经在近期的发布中修改了该问题，如果集群是在 2022 年 3月 12 日之前创建的集群，都有可能出现这个问题。

新后面新创建的集群不会出现。
