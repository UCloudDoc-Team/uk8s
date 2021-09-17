# 亲和性实践

Kubernetes 提供了多种节点分配使用的方法，常用的有以下4种：

* 节点筛选器(nodeSelector)
* 节点亲和与反亲和性(nodeAffinity)
* Pod亲和与反亲和性(podAffinity)
* 节点隔离/限制

## 1. 标签

在做节点选择的时候很多时候用到了 Kubernetes 的 Label 功能，这里我们分别展示给节点及 Pod Label 的方法。

1. 给 10.10.10.10 节点增加 `disktype=ssd` 标签

```bash
# kubectl label nodes 10.10.10.10 disktype=ssd
```

2. 给 Pod 增加 `disktype=ssd` 标签，同理可以针对 Deployment、Service 等对象进行增加标签操作

```bash
# kubectl label po unginx-7db67b8c69-zcxmm disktype=ssd
```

## 2. 节点筛选器（nodeSelector）

节点筛选器，用于创建 Pod（及 Deployment、StatefulSet 等控制器时），将 Pod 分配给相应的节点。

实例 yaml 创建了一个 Pod 对象，在 `spec.nodeSelector` 下以 Map 形式增加改容器部署的节点的限制条件，nodeSelector 会筛选拥有 `disktype: ssd` 的 Node 节点进行 Pod 部署。

```yaml
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

## 3. 节点亲和与反亲和性（nodeAffinity）

使用节点亲和性与反亲和性，需要在 Deployment `spec.template.spec` 下增加 `affinity` 字段，节点亲和分为**硬匹配**和**软匹配** 两种。

### 3.1 硬匹配

在以下 yaml 示例中，`requiredDuringSchedulingIgnoredDuringExecution` 可以理解为**排除不具备指定 Label 的节点**，如果节点不含有 `ucloud=yes` 则 Pod 不会被分配到该节点。

`nodeSelectorTerms` 下提供了 `matchExpressions`（匹配表达式）和 `matchFields`（匹配字段），选择使用其一，我们这里使用了 `matchExpressions`，下面的表达式中 Key 和 Values对应，`operator` 的可选参数有In、NotIn、Exists、DoesNotExist、Gt、Lt，这里可以设置 NotIn、DoesNotExist 进行反亲和的设置，也就是如果这里写入了 `operator: NotIn` 的时候，Pod 将分配在没有 `ucloud=yes` Label 的节点上。

```yaml
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

### 3.2 软匹配

和 `requiredDuringSchedulingIgnoredDuringExecution` 对应还有 `preferredDuringSchedulingIgnoredDuringExecution`，这里称为软匹配，这个参数为对应节点进行打分，降低不具备 Label 的节点的选中几率。

这里的 `weight` 字段在1-100范围内。对于满足所有调度要求的每个节点，调度程序将通过迭代此字段的元素计算总和，并在节点与对应的节点匹配时将「权重」添加到总和 `MatchExpressions`，然后将该分数与节点的其他优先级函数的分数组合。总得分最高的节点是最优选的。

```yaml
preferredDuringSchedulingIgnoredDuringExecution:
- weight: 1
  preference:
    matchExpressions:
    - key: another-node-label-key
      operator: In
      values:
      - another-node-label-value
```

### 3.3 说明

1. 如果同时指定 nodeSelector 和 nodeAffinity，节点必须满足全部条件，Pod 才会被调度到该节点。

2. 如果指定了多个 nodeSelectorTerms 关联 nodeAffinity 类型，如果能满足其中一个 nodeSelectorTerms，则 Pod 就可以调度到这个节点。

3. 如果指定了多个 matchExpressions 关联的 nodeSelectorTerms，则只有在节点满足所有 matchExpressions 要求情况下才能将该容器调度到节点上。

4. 如果删除或更改已有容器节点的 Label，Kubernetes 不会主动删除该容器，亲和的调度选择仅在调度 Pod 时起作用。

