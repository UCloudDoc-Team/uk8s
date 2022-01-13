# 入门必读

Kubernetes 提供了一系列的命令行工具来辅助我们调试和定位问题，本指南列举一些常见的命令来帮助应用管理者快速定位和解决问题。

## 1. 定位问题

在开始处理问题之前，我们需要确认问题的类型，是 Pod ，Service ，或者 Controller（Deployment、StatefulSet） 的问题，然后分别使用不同的命令来查看故障原因。

## 2. Pod 常见命令

当我们发现 Pod 处于 Pending 状态，或者反复 crash，无法接受流量，可以使用以下命令来快速定位问题：

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

## 3. Controller 常见命令

控制器负责 Pod 的生命周期管理，一般 Pod 无法被注册时，可以通过 Controller 来查看原因。这里以 Deployment 为例，介绍 Kubernetes Controller
的常用命令,其他 Controller 的命令类型与其一致。

1. 查看 Deployment 状态

```bash
kubectl -n ${NAMESPACE} get deploy -o wide
```

2. 查看 Deployment yaml 配置

```bash
kubectl -n ${NAMESPACE} get deploy ${DEPLOYMENT_NAME} -o yaml
```

3. 查看 Deployment 事件

```bash
kubectl -n ${NAMESPACE} describe deployment ${DEPLOYMENT_NAME}
```

## 4. Service 常见命令

Service 描述了一组 Pod 的访问方式，当我们发现应用无法访问时，则需要使用 Service 命令来查看故障原因。

1. 查看 Service 状态

```bash
kubectl  -n ${NAMESPACE} get svc -o wide
```

我们可以通过上述命令查看到 Service 的类型、集群内部和外部IP、暴露的端口，以及 Selector 信息。

2. 查看 Service 事件及负载均衡信息

```bash
kubectl  -n ${NAMESPACE} describe svc ${SERVICE_NAME} 

Name:              example-app
Namespace:         default
Labels:            app=example-app
Annotations:       <none>
Selector:          app=example-app
Type:              ClusterIP
IP:                10.2.192.27
Port:              web  8080/TCP
TargetPort:        8080/TCP
Endpoints:         192.168.59.207:8080,192.168.75.87:8080,192.168.84.90:8080
Session Affinity:  None
Events:            <none>
```

如上所示，我们可以通过这个命令查看到 Service 的 Endpoints 信息，Endpoints信息如果为空，则说明 Service 的配置信息有误，Service 无法将流量转发到相应的
Pod. 另外还有 Port 及 TargetPort 信息，确保与业务实际暴露的端口一致。
