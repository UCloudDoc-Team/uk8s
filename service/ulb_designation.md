# 使用已有的ULB

UK8S支持在创建 LoadBalancer 类型的 Service 时，指定使用已有的 ULB 实例，而不是创建一个新的ULB实例。

也支持多个Service复用一个ULB实例，但存在以下规则限制：

1. 已有的 ULB 实例，必须是你自行创建的 ULB 实例，不能是 UK8S 插件创建出来的，否则会导致 ULB 被意外删除（在UK8S内删除Service，ULB也会被同步删除）。

2. 多个Service复用一个ULB实例时，Service端口不能冲突，否则新Service无法创建成功。

3. 指定已有的ULB实例创建LoadBalancer Service，Service被删除后，ULB实例不会被删除，仅删除对应的Vserver。

4. 通过UK8S创建的Vserver命名规范为`Protocol-ServicePort-ServiceUUID`，请勿随意修改，否则可能导致脏数据。

下面我们来看下如何使用已有的ULB实例。

## 使用已有ALB

```yaml
apiVersion: v1
kind: Service
metadata:
  name: https
  labels:
    app: https
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-id": "alb-rpfirtgx4l4" # 替换为自己的alb id
    # 申明使用alb
    "service.beta.kubernetes.io/ucloud-load-balancer-listentype": "application"
    # 申明使用http协议
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "http"
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 443
      targetPort: 8080
      name: https
    - protocol: TCP
      name: http
      port: 80
      targetPort: 8080
  selector:
    app: https
```

## 使用已有的内网ULB

声明使用已有的内网ULB，需要声明至少两个annotations。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: https
  labels:
    app: https
  annotations:
    service.beta.kubernetes.io/ucloud-load-balancer-id: "ulb-ofvmd1o4" #替换成自己的ULB Id
    service.beta.kubernetes.io/ucloud-load-balancer-type: "inner"
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 443
      targetPort: 8080
  selector:
    app: https
```

## 使用已有的外网ULB（7层）

```yaml
apiVersion: v1
kind: Service
metadata:
  name: https
  labels:
    app: https
  annotations:
    service.beta.kubernetes.io/ucloud-load-balancer-id: "ulb-ofvmd1o4"
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol: "https"
    # http与https等价，均表示使用7层负载均衡
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert: "ssl-b103etqy"
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port: "443"
    # 443端口启用SSL，80端口依然为HTTP
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 443
      targetPort: 8080
    - protocol: TCP
      port: 80
      targetPort: 8080
  selector:
    app: https
```

## 使用已有的外网ULB（4层）

```yaml
apiVersion: v1
kind: Service
metadata:
  name: https
  labels:
    app: https
  annotations:
    service.beta.kubernetes.io/ucloud-load-balancer-id: "ulb-ofvmd1o4"
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol: "tcp"
    # 表示使用4层负载均衡
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 443
      targetPort: 8080
    - protocol: TCP
      port: 80
      targetPort: 8080
  selector:
    app: tcp
```
