
## 网络隔离(NetworkPolicy)

### 概述

在UK8S中，默认情况下，所有的Pod都是互通的，即：Pod可以接收来自任何发送方的请求，也可以向任何接收方发送请求。

但在实际业务场景中，为了保障业务安全，网络隔离是非常必要的。下面介绍下如何在UK8S中实现网络隔离。

>> NetworkPolicy支持仅限于2019年12月3日之后创建的UK8S集群，或cni版本大于等于19.12.1(在Node节点执行/opt/cni/bin/cnivpc version)。之前创建的集群如想使用NetworkPolicy，请联系UK8S团队协助处理。

### 安装插件

为了在 UK8S 中实现网络隔离，需要部署 calico 的 Felix 和 Typha 组件，组件模块已容器化，直接在UK8S通过kubectl命令安装即可.

```bash

kubectl apply -f http://uk8s.cn-bj.ufileos.com/policy_calico-policy-only.yaml

```

>> Warning: 在安装calico网络隔离插件之间，请务必确认cni版本大于等于19.12.1，否则会删除Node上原有的网络配置，导致pod网络不通。



### NetworkPolicy规则解析

安装完calico的网络隔离策略组件后，我们就可以在UK8S中创建NetworkPolicy对象，用于实现Pod的访问控制，如下所示。

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 172.17.0.0/16
        except:
        - 172.17.1.0/24
    - namespaceSelector:
        matchLabels:
          project: myproject
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 6379
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 5978

```

下面简要描述下各个参数的作用：

+ **spec.podSelector**: 这个参数的意义用于决定该NetworkPolicy的作用域，即对那些Pod有效。上面的示例表示对所有携带了role=db 标签(label)的pod生效。

+ **spec.ingress.from**: 入向请求访问控制，即接受哪些源的请求。支持IP、namespace、pod三种控制模式，上面的示例表示放行源地址为172.17/16中除172.17.1/24 之外的请求、或任何携带了标签projcet=myproject的namespace下的所有pod、或Default namespace里携带了role=frontend标签的pod。from中的多组规则是或逻辑，满足上述三个条件中的一个即放行。

+ **spec.ingress.ports**: 声明开放访问的端口，如果不填写则默认开放所有。上面的示例表示只允许访问6379端口。from和ports是与逻辑，即指允许上述from规则下放行的源访问6379端口。

+ **spec.egress**: 声明允许访问的目的地址，与from类似。上面的示例表示只允许请求IP为10.0.0.0/24网段的地址，并且只允许访问该网段地址的5978端口。

通过上面的描述，我们应该清楚，NetworkPolicy是一个白名单机制，即一旦开启NetworkPolicy，除非显式指定，否则一概拒绝。

### 示例

#### 1、限制一组Pod只允许访问VPC内部的资源(不能访问外网)

```yaml

kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: pod-egress-policy
spec:
  podSelector:
    matchLabels:
      pod: internal-only
  egress:
  - to:
    - ipBlock:
        cidr: 10.9.0.0/16
```

### 2、限制暴露了公网服务的Service的来源IP

首先创建一个通过外网ULB4对公网暴露服务的应用

```yaml
apiVersion: v1
kind: Service
metadata: 
  name: ucloud-nginx
  labels:
    app: ucloud-nginx
spec: 
  type: LoadBalancer
  externalTrafficPolicy: local
  ports: 
    - protocol: TCP
      port: 80
  selector:
    app: ucloud-nginx
---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx
  labels:
    app: ucloud-nginx
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
    ports:
    - containerPort: 80
```

上述应用创建完毕后，我们可以通过外网ULB IP直接访问应用，现在我们设置只允许从办公室环境访问该应用，假设办公室出口IP为106.10.10.10。

```yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: access-nginx
spec:
  podSelector:
    matchLabels:
      app: ucloud-nginx
  ingress:
  - from:
    - ipBlock:
        cidr: 106.10.10.10/24  #验证时请改为你客户端的出口IP。
```
