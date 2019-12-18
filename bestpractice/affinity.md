

## 亲和性实践

### 节点和pod分配使用方法

kubernetes提供了多种节点分配使用的方法，常用的有以下4种：

* 节点筛选器(nodeSelector)
* 节点亲和与反亲和性(nodeAffinity)
* pod亲和与反亲和性(podAffinity)
* 节点隔离/限制

### 增加标签

在做节点选择的时候很多时候用到了kubernetes的label功能，这里我们提供两个增加label的方法。

1. 给10.10.10.10节点增加**disktype=ssd**标签

```
kubectl label nodes 10.10.10.10 disktype=ssd
```

2. 给pod增加**disktype=ssd**标签，同理可以针对deploy、svc等对象进行增加标签操作

```
kubectl label po unginx-7db67b8c69-zcxmm disktype=ssd
```

### 节点筛选器

参考这个yaml文件，这是一个pod对象的yaml，在**spec.nodeSelector**下以map形式增加改容器部署的节点的限制条件，nodeSelector会筛选拥有**disktype: ssd**的node节点进行pod部署。

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    env: test
spec:
  containers:
  - name: nginx
    image: nginx
    imagePullPolicy: IfNotPresent
  nodeSelector:
    disktype: ssd
```


### 节点亲和与反亲和性(nodeAffinity)

参考这个yaml文件，这是一个deploy对象的yaml，在**spec.template.spec**下增加**affinity**字段,节点亲和分为两种：

* 硬匹配
* 软匹配

#### 硬匹配

如下的yaml示例，**requiredDuringSchedulingIgnoredDuringExecution**可以理解为**排除不具备指定label的节点**，这个例子讲的是如果节点不含有**ucloud=yes**则不会被分配，**nodeSelectorTerms**下提供了**matchExpressions**(匹配表达式)和**matchFields**(匹配字段)，选择使用其一，我们这里使用了**matchExpressions**，下面的表达式种key和values对应，**operator**的可选参数有In, NotIn、Exists、DoesNotExist、Gt、Lt，这里可以设置NotIn、DoesNotExist进行反亲和的设置，也就是如果这里写入了**operator: NotIn**的时候，这个安装将安装在没有**ucloud=yes**的节点上。

```
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    run: ucloud
  name: ucloud
spec:
  replicas: 3
  selector:
    matchLabels:
      run: ucloud
  template:
    metadata:
      creationTimestamp: null
      labels:
        run: ucloud
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution: 
            nodeSelectorTerms: 
            - matchExpressions:
              - key: ucloud
                operator: In
                values:
                - "yes"
      containers:
      - image: nginx
        name: ucloud
        ports:
        - containerPort: 80
        resources: {}
```

#### 软匹配

和**requiredDuringSchedulingIgnoredDuringExecution**对应的还有一个 **preferredDuringSchedulingIgnoredDuringExecution**，这里称为软匹配，这个参数是为对应的节点进行打分，降低不具备label的节点的选中几率。

这里的**weight**字段在1-100范围内。对于满足所有调度要求的每个节点，调度程序将通过迭代此字段的元素计算总和，并在节点与对应的节点匹配时将“权重”添加到总和MatchExpressions，然后将该分数与节点的其他优先级函数的分数组合。总得分最高的节点是最优选的。

```
preferredDuringSchedulingIgnoredDuringExecution:
- weight: 1
  preference:
    matchExpressions:
    - key: another-node-label-key
      operator: In
      values:
      - another-node-label-value
```

#### 值得注意的

如果同时指定nodeSelector和nodeAffinity，都必须全部满足条件，Pod才会被调度到的候选节点。

如果指定了多个nodeSelectorTerms关联nodeAffinity类型，如果能满足其中一个nodeSelectorTerms，则pod就可以调度到这个节点。

如果指定了多个matchExpressions关联的nodeSelectorTerms，则只有 matchExpressions在可以满足所有要求的情况下才能将该容器调度到节点上。

如果删除或更改计划容器的节点的label，k8s不会主动删除该容器，亲和的调度选择仅在调度pod时起作用。

### 参考yaml文件

* [nodeAffinity.yaml](https://github.com/UCloudDocs/uk8s/blob/master/yaml/nodeAffinity.yaml)
* [nodeName.yaml](https://github.com/UCloudDocs/uk8s/blob/master/yaml/nodeName.yaml)


