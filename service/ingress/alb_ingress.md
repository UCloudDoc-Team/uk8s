# ALB Ingress

> alb ingress 是使用 ucloud alb 实现 [k8s ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)，得益于 ucloud alb 超高的性能，让你的服务具备大规模应用层流量处理能力

## 部署

### 先决条件

* cni必须为vpc cni
* 该地域支持alb（可以在控制台查看是否支持alb）

### 安装cert-manager

> alb ingress 需要使用cert-manager来签署webhook证书
> 下面是使用helm安装，关于其他安装方式参考<https://cert-manager.io/docs/installation/>

* 如果helm中没有repo需要先添加helm repo

```shell
helm repo add jetstack https://charts.jetstack.io --force-update
```

* 安装helm

```shell
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.19.1 \
  --set crds.enabled=true
```

### 安装ucloud alb ingress

```shell
kubctl apply -f https://docs.ucloud.cn/uk8s/yaml/ingress_alb/20251124.yaml
```

## 使用

### 基本使用

* 下面的例子是一个使用ucloud ssl证书部署2个服务，端口为http 80和 https 443
* alb ingrss 大部分配置是通过注解完成的，详情可以查看[注解参数说明](#注解参数说明)和[所有功能完整的例子](#所有功能完整的例子)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-app-ingress
  labels:
    uk8s: ingress-test
  annotations:
    # lb类型，outer公网，inner内网，默认公网,如果只使用内网lb请解除下面的注释
    alb.ingress.kubernetes.io/load-balancer-type: 'outer'
    #  监听端口
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    # 第一个为默认证书，多个使用逗号隔开，且默认证书不可从其他证书中切换
    alb.ingress.kubernetes.io/certificates: 'ssl-xxx'
    # 使用多个证书时解除下面的注释
    # alb.ingress.kubernetes.io/certificates: 'ssl-xxx,ssl-yyy'
spec:
  ingressClassName: alb
  defaultBackend:
    service:
      name: demo-app-1-svc
      port:
        number: 80
  rules:
    - host: demo-app.example.com
      http:
        paths:
          - path: /demo-app-1
            pathType: Prefix
            backend:
              service:
                name: demo-app-1-svc
                port:
                  number: 80
          - path: /demo-app-2
            pathType: Prefix
            backend:
              service:
                name: demo-app-2-svc
                port:
                  number: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app-1
  labels:
    app:  demo-app-1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo-app-1
  template:
    metadata:
      labels:
        app: demo-app-1
    spec:
      containers:
        - name: demo-app-1
          image: uhub.service.ucloud.cn/jenkins_k8s_cicd/echo_nginx:v11
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: demo-app-1-svc
spec:
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
  selector:
    app: demo-app-1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app-2
  labels:
    app:  demo-app-2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo-app-2
  template:
    metadata:
      labels:
        app: demo-app-2
    spec:
      containers:
        - name: demo-app-2
          image: uhub.service.ucloud.cn/jenkins_k8s_cicd/echo_nginx:v11
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: demo-app-2-svc
spec:
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
  selector:
    app: demo-app-2
```

### 使用configmap配置tls证书

1. 首先需要创建一个`kubernetes.io/tls`类型的configmap,如下

   ```shell
   apiVersion: v1
   kind: Secret
   metadata:
     name: demo-app-ingress
   data:
     tls.crt: "<base64处理过后的证书>"
     tls.key: "<base64处理过后的私钥>"
   type: kubernetes.io/tls
   ```

2. ingress中引入configmap,控制器会自动在alb的证书管理中创建对应的证书并绑定到alb中

```yaml
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-app-ingress
  labels:
    uk8s: ingress-test
  annotations:
    # lb类型，outer公网，inner内网，默认公网,如果只使用内网lb请解除下面的注释
    alb.ingress.kubernetes.io/load-balancer-type: 'outer'
    #  监听端口
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    # 第一个为默认证书，多个使用逗号隔开，且默认证书不可从其他证书中切换
  ingressClassName: alb
  defaultBackend:
    service:
      name: demo-app-1-svc
      port:
        number: 80
  rules:
    - host: demo-app.example.com
      http:
        paths:
          - path: /demo-app-1
            pathType: Prefix
            backend:
              service:
                name: demo-app-1-svc
                port:
                  number: 80
          - path: /demo-app-2
            pathType: Prefix
            backend:
              service:
                name: demo-app-2-svc
                port:
                  number: 80
  tls:
    - hosts: 
      - test.com
      secretName: demo-app-ingress
    - hosts: 
      - example.com
      secretName: demo-app-ingress2
```

### Pod Readines Gate

ucloud Load Balancer controller 支持[pod-readiness-gate](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-readiness-gate)，用于告诉pod已经注册到alb中并可以正常接受流量

> 每个listener一个readiness gate

* 在需要开启的ns上加上下面的标签

```shell
kubectl label ns <ns> alb.k8s.ucloud/pod-readiness-gate-inject=enabled
```

* 开启后可以看到READINESS GATES有标签

```shell
kubectl get po -o wide
NAME                          READY   STATUS    RESTARTS   AGE     IP              NODE            NOMINATED NODE   READINESS GATES
demo-app-1-7d8dc8f966-7bgmh   1/1     Running   0          5s      10.60.103.142   10.60.247.141   <none>           0/2
demo-app-1-7d8dc8f966-t2ggq   1/1     Running   0          5s      10.60.201.32    10.60.57.16     <none>           0/2
demo-app-2-d98469768-gvl5b    1/1     Running   0          5s      10.60.114.222   10.60.247.141   <none>           0/2
demo-app-2-d98469768-mpln4    1/1     Running   0          5s      10.60.41.90     10.60.96.249    <none>           0/2
demo-app-2-d98469768-t2tpp    1/1     Running   0          5s      10.60.64.103    10.60.57.16     <none>           0/2
```

* 稍等片刻 alb 监控检测都通过之后则全部满足

```shell
❯ kubectl get po -o wide
NAME                          READY   STATUS    RESTARTS   AGE     IP              NODE            NOMINATED NODE   READINESS GATES
demo-app-1-7d8dc8f966-7bgmh   1/1     Running   0          51s     10.60.103.142   10.60.247.141   <none>           2/2
demo-app-1-7d8dc8f966-t2ggq   1/1     Running   0          51s     10.60.201.32    10.60.57.16     <none>           2/2
demo-app-2-d98469768-gvl5b    1/1     Running   0          51s     10.60.114.222   10.60.247.141   <none>           2/2
demo-app-2-d98469768-mpln4    1/1     Running   0          51s     10.60.41.90     10.60.96.249    <none>           2/2
demo-app-2-d98469768-t2tpp    1/1     Running   0          51s     10.60.64.103    10.60.57.16     <none>           2/2
```

* 如果ns开启了readiness gate 但是某个工作负载不想开启则使用下面的标签

```shell
kubectl label deployment alb.k8s.ucloud/pod-readiness-gate-inject=disabled
```

### 所有功能完整的例子

```yaml
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-app-ingress
  labels:
    uk8s: ingress-test
  annotations:
    # lb类型，outer公网，inner内网，默认公网,如果只使用内网lb请解除下面的注释
    alb.ingress.kubernetes.io/load-balancer-type: 'outer'
    #  监听端口
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    # 第一个为默认证书，多个使用逗号隔开，且默认证书不可从其他证书中切换
    alb.ingress.kubernetes.io/certificates: 'ssl-xxx'
    # 使用多个证书时解除下面的注释
    # alb.ingress.kubernetes.io/certificates: 'ssl-xxx,ssl-yyy'

    # 子网id 默认: 集群所在的子网
    # alb.ingress.kubernetes.io/subnet-id: 'subnet-xxx'

    # lb付费模式 默认:month
    # month（按月付费）;year（按年付费）;dynamic（按时付费）
    # alb.ingress.kubernetes.io/load-balancer-chargetype 'month'
    # lb付费时长 默认:1 chargetype 为 dynamic 时无需填写
    # alb.ingress.kubernetes.io/load-balancer-quantity: '1'

    # lb使用按时付费模式示例
    # alb.ingress.kubernetes.io/load-balancer-chargetype: 'dynamic'

    # eip计费模式 默认：bandwidth 支持 traffic（流量计费）、bandwidth（带宽计费）、sharebandwidth（共享带宽）
    # alb.ingress.kubernetes.io/eip-paymode: 'bandwidth'
    # eip共享带宽 ID 仅在 eip-paymode 为 sharebandwidth 时生效
    # alb.ingress.kubernetes.io/eip-sharebandwidthid: '<共享带宽id>'
    # eip外网带宽 默认:2 单位为 Mbps。共享带宽模式下无需指定，或者配置为 0；流量计费模式下，该参数为流量计费 EIP 带宽上限
    # alb.ingress.kubernetes.io/eip-bandwidth: '2'
    # 付费模式 默认:month  支持 month（按月付费）、year（按年付费）、dynamic（按时付费）
    # alb.ingress.kubernetes.io/eip-chargetype: 'month'
    # eip付费时长 默认:1 chargetype 为 dynamic 时无需填写
    # alb.ingress.kubernetes.io/eip-quantity: '1'
    # eip弹性IP线路 默认:BGP/International
    # 国际线路:International;BGP线路:Bgp;精品BGP:BGPPro;电信:Telecom
    # 默认值根据所处地域决定（华北（北京2）、上海、华南（广州）、华北（乌兰察布）为BGP，其他地域为International）
    # alb.ingress.kubernetes.io/eip-operator-name: 'BGP'

    # 外网带宽计费，以下是10Mbps包月的配置示例
    # alb.ingress.kubernetes.io/eip-paymode: 'bandwidth'
    # alb.ingress.kubernetes.io/eip-bandwidth: '10'
    # alb.ingress.kubernetes.io/eip-chargetype: 'month'
    # alb.ingress.kubernetes.io/eip-quantity: '1'

    # 外网流量计费，以下是300Mbps带宽上线，按时付费
    # alb.ingress.kubernetes.io/eip-paymode: 'traffic'
    # alb.ingress.kubernetes.io/eip-bandwidth: '300'
    # alb.ingress.kubernetes.io/eip-chargetype: 'dynamic'
    # alb.ingress.kubernetes.io/eip-quantity: '1'

    # 外网共享带宽，以下是使用共享带宽计费的配置示例
    # alb.ingress.kubernetes.io/eip-paymode: 'sharebandwidth'
    # alb.ingress.kubernetes.io/eip-sharebandwidthid: 'bwshare-xxx'
    
    # 以下参数设置任何一个则使用http方式的健康检查,另一个则是默认，默认为Port
    # http的方式做健康检查的域名 默认: ""
    # alb.ingress.kubernetes.io/monitor-domain: "example.com"
    # http的方式做健康检查的的路径 默认: ""
    # alb.ingress.kubernetes.io/monitor-path: "/healthz"

    # 安全组配置,多个使用逗号隔开
    # 优先级为顺序
    # alb.ingress.kubernetes.io/security-groups: 'secgroup-xxx,secgroup-yyy'
spec:
  ingressClassName: alb
  defaultBackend:
    service:
      name: demo-app-1-svc
      port:
        number: 80
  rules:
    - host: demo-app.example.com
      http:
        paths:
          - path: /demo-app-1
            pathType: Prefix
            backend:
              service:
                name: demo-app-1-svc
                port:
                  number: 80
          - path: /demo-app-2
            pathType: Prefix
            backend:
              service:
                name: demo-app-2-svc
                port:
                  number: 80
  #tls:
  #  - hosts: 
  #    - test.com
  #    secretName: demo-app-ingress
  #  - hosts: 
  #    - example.com
  #    secretName: demo-app-ingress2
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app-1
  labels:
    app:  demo-app-1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo-app-1
  template:
    metadata:
      labels:
        app: demo-app-1
    spec:
      containers:
        - name: demo-app-1
          image: uhub.service.ucloud.cn/jenkins_k8s_cicd/echo_nginx:v11
          ports:
            - containerPort: 80
      # readinessGates:
      #   - conditionType: "80.target-health.alb.k8s.ucloud/demo-app-ingress"
      #   - conditionType: "443.target-health.alb.k8s.ucloud/demo-app-ingress"
---
apiVersion: v1
kind: Service
metadata:
  name: demo-app-1-svc
spec:
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
  selector:
    app: demo-app-1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app-2
  labels:
    app:  demo-app-2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo-app-2
  template:
    metadata:
      labels:
        app: demo-app-2
    spec:
      containers:
        - name: demo-app-2
          image: uhub.service.ucloud.cn/jenkins_k8s_cicd/echo_nginx:v11
          ports:
            - containerPort: 80
      # readinessGates:
      #   - conditionType: "80.target-health.alb.k8s.ucloud/demo-app-ingress"
      #   - conditionType: "443.target-health.alb.k8s.ucloud/demo-app-ingress"
---
apiVersion: v1
kind: Service
metadata:
  name: demo-app-2-svc
spec:
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
  selector:
    app: demo-app-2
---
apiVersion: v1
kind: Secret
metadata:
  name: demo-app-ingress
data:
  tls.crt: "<base64处理过后的证书>"
  tls.key: "<base64处理过后的私钥>"
type: kubernetes.io/tls
---
apiVersion: v1
kind: Secret
metadata:
  name: demo-app-ingress2
data:
  tls.crt: "<base64处理过后的证书>"
  tls.key: "<base64处理过后的私钥>"
type: kubernetes.io/tls
```

## 注解参数说明

> 动态配置是指创建完成之后仍然可以修改的配置

| 注解名称                                           | 说明                                                    | 默认值                      | 是否支持动态配置 |
|----------------------------------------------------|---------------------------------------------------------|-----------------------------|------------------|
| alb.ingress.kubernetes.io/load-balancer-id         | 绑定的LB的ID                                            | ""                          | 否               |
| alb.ingress.kubernetes.io/load-balancer-type       | LB 的类型 (outer/inner)                                 | outer                       | 是               |
| alb.ingress.kubernetes.io/http-listen-ports        | LB 监听端口，默认 HTTP 80 和 HTTPS 443 json数组格式     | [{"HTTP":80},{"HTTPS":443}] | 否               |
| alb.ingress.kubernetes.io/certificates             | 指定 ucloud ssl 证书 id，数组逗号隔开，第一个为默认证书 | ""                          | 是               |
| alb.ingress.kubernetes.io/subnet-id                | 子网 ID                                                 | 集群的子网                  | 否               |
| alb.ingress.kubernetes.io/load-balancer-chargetype | LB 付费模式 (month/year/dynamic)                        | "month"                     | 否               |
| alb.ingress.kubernetes.io/load-balancer-quantity   | LB 付费时长                                             | 1                           | 否               |
| alb.ingress.kubernetes.io/monitor-domain           | http 的方式做健康检查的域名                             | ""                          | 是               |
| alb.ingress.kubernetes.io/monitor-path             | http 的方式做健康检查的路径                             | ""                          | 是               |
| alb.ingress.kubernetes.io/security-groups          | 安全组配置，多个使用逗号隔开，优先级为顺序              | ""                          | 是               |
| alb.ingress.kubernetes.io/eip-paymode              | EIP 计费模式 (traffic/bandwidth/sharebandwidth)         | "bandwidth"                 | 否               |
| alb.ingress.kubernetes.io/eip-sharebandwidthid     | EIP 共享带宽 ID                                         | ""                          | 否               |
| alb.ingress.kubernetes.io/eip-bandwidth            | EIP 带宽，单位为 Mbps                                   | 2                           | 是               |
| alb.ingress.kubernetes.io/eip-chargetype           | EIP 付费模式 (month/year/dynamic)                       | "month"                     | 否               |
| alb.ingress.kubernetes.io/eip-quantity             | EIP 付费时长，chargetype 为 dynamic 时无需填写          | 1                           | 否               |
| alb.ingress.kubernetes.io/eip-operator-name        | EIP 弹性IP线路 (International/Bgp/BGPPro/Telecom)       | 根据地域                    | 否               |

* lb类型:
  * outer：外网
  * innger： 内网

* 付费模式:
  * month: 按月
  * year： 按年
  * dynamic: 按时

* EIP 计费模式：
  * traffic: 按流量
  * bandwidth: 按带宽
  * sharebandwidth: 共享带宽

* EIP 默认线路:
  * BGP: 华北（北京2）、上海、华南（广州）、华北（乌兰察布）
  * International: 其他地域
