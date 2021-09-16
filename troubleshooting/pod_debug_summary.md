# Pod 常见故障处理

在Kubernetes中发布应用时，我们经常会遇到Pod出现异常的情况，如Pod长时间处于Pending状态，或者反复重启，下面介绍下Pod 的各种异常状态及处理思路。

## 1. 常见错误

|状态|	状态说明|处理办法|
|----|----------|--------|
|Error|	Pod 启动过程中发生错误。|一般是由于容器启动命令、参数配置错误所致，请联系镜像制作者|
|NodeLost|Pod 所在节点失联。|检查 Pod 所在节点的状态|
|Unkown|Pod 所在节点失联或其他未知异常。|检查 Pod 所在节点的状态|
|Pending|Pod 等待被调度。|资源不足等原因导致，通过 kubectl describe 命令查看 Pod 事件|
|Terminating|Pod 正在被销毁。|可增加 --fore参数强制删除|
|CrashLoopBackOff|容器退出，Kubelet 正在将它重启。|一般是由于容器启动命令、参数配置错误所致|
|ErrImageNeverPull|	策略禁止拉取镜像。|拉取镜像失败，确认imagePullSecret是否正确|
|ImagePullBackOff|正在重试拉取。| 镜像仓库与集群的网络连通性问题|
|RegistryUnavailable|连接不到镜像仓库。|联系仓库管理员|
|ErrImagePull|	拉取镜像出错。|联系仓库管理员，或确认镜像名是否正确|
|RunContainerError|	启动容器失败。| 容器参数配置异常|
|PostStartHookError|	执行 postStart hook 报错。|postStart 命令有误|
|NetworkPluginNotReady|	网络插件还没有完全启动。| cni 插件异常，可检查cni状态|



## 2. 常见命令

当我们发现 Pod 处于 上述状态时，可以使用以下命令来快速定位问题：

1. 获取 Pod 状态

```bash
kubectl -n ${NAMESPACE} get pod  -o wide 
```

2. 查看 Pod 的 yaml 配置

```bash
kubectl -n ${NAMESPACE} get pod ${POD_NAME}  -o yaml
```

3. 查看 Pod 事件

```bash
kubectl  -n ${NAMESPACE} describe pod ${POD_NAME}
```

4. 查看 Pod 日志

```bash
kubectl  -n ${NAMESPACE} logs ${POD_NAME} ${CONTAINER_NAME}
```

5. 登录 Pod 

```bash
kubectl -n ${NAMESPACE} exec -it  ${POD_NAME} /bin/bash
```

