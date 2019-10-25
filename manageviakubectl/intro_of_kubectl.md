
## kubectl命令行简介


kubectl是一个用于操作kubernetes集群的命令行工具，本文将简要介绍下kubectl的语法，并提供一些常见命令示例，如果你想了解深入了解kubectl的用法，请查阅官方文档[kubectl overview](https://kubernetes.io/docs/reference/kubectl/overview/)，或使用kubectl help命令查看详细帮助。 安装kubectl请查看[安装及配置kubectl](connectviakubectl)。


### kubectl 语法

kubectl的语法示例如下：
```
kubectl [command] [TYPE] [NAME] [flags]
```
**command:** command意指你想对某些资源所进行的操作，常用的有create、get、describe、delete等。

**TYPE:** 声明command需要操作的资源类型，TYPE对大小写、单数、复数不敏感，支持缩写。比如，以下命令都是合法且等价的：
```
kubectl get pod 
kubectl get pods
kubectl get po
kubectl get POD
```
**NAME:** 即资源的名称，NAME是大小写敏感的。如果不指定某个资源的名称，则显示所有资源，如kubectl get pods 会显示Default命名空间下所有的pod。

你还可以同时获取多个资源的详细情况，如获取同一类型的资源详情，不同类型的资源详情：
```
kubectl get pods pod1 pod2
```

```
kubectl get pod/example-pod1 replicationcontroller/example-rc1
```

**flags：** 可选参数，例如，你可以使用all-namespaces来获取所有namespace下的资源对象。关于各命令的flag用法请参见[kubectl command](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands)

重要：命令行指定的flags将覆盖默认值和任何相应的环境变量。

更多关于kubectl命令的介绍，请使用kubectl help。


### 常见命令

**kubectl create** - 使用一个文件或者标准输入创建资源。

```
// 使用exampe-service.yaml文件创建一个“service”对象
$ kubectl create -f example-service.yaml

// 使用example-controller.yaml文件创建一个"replication"对象
$ kubectl create -f example-controller.yaml

```

**kubectl describe** - 获取资源的详细状态，包括初始化中的资源。

```
// 查看名为<node-name>的node节点详情
$ kubectl describe nodes <node-name>

// 查看名为<pod-name>的pod详情，包含pod的创建日志
$ kubectl describe pods/<pod-name>

// 查看所有由名为<rc-name>的replication管理的pod。
// 注意: 任何由replication controller创建的pod，其名称前缀为replication名称。
$ kubectl describe pods <rc-name>

// 查看所有pods，但不包含未初始化的pods
$ kubectl describe pods --include-uninitialized=false

```

**kubectl logs** - 获取某个pod的日志

```
// 获取一个pod的日志快照
$ kubectl logs <pod-name>

// 获取一个pod的实时日志流，类似于linux的'tail -f'
$ kubectl logs -f <pod-name>
```

**kubectl exec** - 对pod中的容器执行命令

```
// 从pod中获取运行"date"命令的输出，默认情况下，来自于pod中的第一个容器。
$ kubectl exec <pod-name> date

// 从pod中指定的容器中获取运行"date"命令的输出
$ kubectl exec <pod-name> -c <container-name> date

// 从pod中得到一个交互式tty(控制终端),并执行/bin/bash
$ kubectl exec -ti <pod-name> /bin/bash
```
