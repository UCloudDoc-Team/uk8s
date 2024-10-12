## Nginx Ingress

**本文适用于的 K8S 版本为 1.26+，对于不同版本，请参考：[Ingress 支持](/uk8s/service/ingress/README)**

### 什么是 Ingress

Ingress 是从 Kubernetes 集群外部访问集群内部服务的入口，同时为集群内的 Service 提供七层负载均衡能力。

一般情况下，Service 和 Pod 仅可在集群内部通过 IP 地址访问，所有到达集群边界的流量或被丢弃或被转发到其他地方，前面的 service 章节我们提供了创建 LoadBalancer
类型的 Service 方法，借助于 Kubernetes 提供的扩展接口，UK8S 会创建一个与该 Service 对应的负载均衡服务即 ULB
来承接外部流量，并路由到集群内部。但在诸如微服务等场景下，一个 Service 对应一个负载均衡器，管理成本明显过高，Ingress 因此应运而生。

我们可以把 Ingress 理解为 Service 提供能力的 “Service”，为后端不同 Service 提供代理的负载均衡服务，我们可以在 Ingress 配置可供外部访问
URL、负载均衡、SSL、基于名称的虚拟主机等。

下面我们通过在 UK8S 中部署 Nginx Ingress Controller，来了解一下 Ingress 的使用过程。

### 一、部署 Ingress Controller

为了使 Ingress 正常工作，集群内必须部署 Ingress Controller。与其他类型的控制器不同，其他类型的控制器如 Deployment 通常作为
kube-controller-manager 二进制文件的一部分，在集群启动时自动运行。而 Ingress Controller 则需要自行部署，Kubernetes 社区提供了以下 Ingress
Controller 供选择，分别如下：

1. Nginx
2. HAProxy
3. Envoy
4. Traefik

这里我们选择 Nginx 作为 Ingress Controller，部署 Nginx Ingress Controller 非常简单，执行以下指定即可。

```bash
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/ingress_nginx/mandatory_1.26.yaml
```

在 `mandatory_1.26.yaml` 这个文件里，是 Ingress Controller 的定义，我们可以把 yaml
文件下载到本地仔细研读下。这里简要简述下部分 yaml 字段的意义。

这个 yaml 定义了一个使用 ingress-nginx-controller 作为镜像的 pod 副本集，这个 Pod 主要功能就是监听 Ingress 对象以及它所代理的后端 Service
变化的控制器。当一个新的 Ingress 对象由用户创建后，控制器会根据 Ingress 对象所定义的内容，生成一份对应的 Nginx 配置文件（也就是我们熟知的
`/etc/nginx/nginx.conf`），并使用这个配置文件启动一个 Nginx 服务。而一旦 Ingress 对象被更新，控制器会更新这个配置文件。需要注意的是，如果只是被代理的
Service 对象被更新，控制器所管理的 nginx 服务不需要重新加载，这是因为 ingress-nginx-controller 通过 nginx lua 实现了 upstream 的动态配置。

另外，在这个 yaml 文件中，我们还看到定义了 ConfigMap，ingress-nginx-controller 可以通过 ConfigMap 对象来对 Nginx 配置文件进行定制，示例如下：

```yaml
apiVersion: v1
data:
  allow-snippet-annotations: "false"
kind: ConfigMap
metadata:
  labels:
    app.kubernetes.io/component: controller
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/version: 1.10.5
  name: ingress-nginx-controller
  namespace: ingress-nginx
```

需要注意的是，ConfigMap 中的 key 和 value 只支持字符串，因此对于整数等类型，需要使用双引号，例如"100"，详细资料见
[Nginx-Ingress-ConfigMap](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/)。

本质上，这个 ingress-nginx-controller 是一个可以根据 Ingress 对象和被代理后端 Service 的变化，自动进行更新的 Nginx 负载均衡器。

容器默认使用 UTC
时间，如果要使用宿主机时区，参见 [Pod 时区问题](https://docs.ucloud.cn/uk8s/troubleshooting/pod_debug_summary?id=_10-pod%e7%9a%84%e6%97%b6%e5%8c%ba%e9%97%ae%e9%a2%98)

### 二、集群外部访问 nginx ingress

上面我们已经在 UK8S 中部署了一个 nginx ingress controller，并且为了在集群外部可达，我们还创建了一个外部可达的 LoadBalancer 类型的
Service，如下所示。

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"
  labels:
    app.kubernetes.io/component: controller
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/version: 1.10.5
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  externalTrafficPolicy: Local
  ports:
  - appProtocol: http
    name: http
    port: 80
    protocol: TCP
    targetPort: http
  - appProtocol: https
    name: https
    port: 443
    protocol: TCP
    targetPort: https
  selector:
    app.kubernetes.io/component: controller
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/name: ingress-nginx
  type: LoadBalancer
```

这个 Service 的唯一工作，就是将所有携带 ingress-nginx 标签的 Pod 的 80 和 433 端口暴露出去，我们可以通过以下方式获取到这个 Service 的外部访问入口。

需要注意的是样例中的 LoadBalancer 创建的 ULB 为内网模式， 如果创建外网 ULB，需要将这个 Service 的
`metadata.annotations."service.beta.kubernetes.io/ucloud-load-balancer-type"` 改为 "outer"，更多参数请官方文档
[ULB 参数说明](https://docs.ucloud.cn/uk8s/service/annotations)。

```bash
$ kubectl get svc -n ingress-nginx
NAME                       TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)                      AGE
ingress-nginx-controller   LoadBalancer   172.30.48.77   xxx.yy.xxx.yy   80:30052/TCP,443:31285/TCP   14m
......
```

部署完 Ingress Controller 和它所需要的 Service 后，我们就可以使用通过它来将集群内部的其他 Service 代理出去了。

### 三、创建两个应用

在下面的 yaml 中，我们定义了 2 个镜像名为 echo-nginx 的应用，主要是输出 nginx 应用自身的一些全局变量。

```yaml
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
  labels:
spec:
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
  selector:
    app: demo-app-2
```

我们将上述 yaml 保存为 `demo-app.yaml`，并执行如下命令创建应用。

```bash
kubectl apply -f demo-app.yaml
```

### 四、定义 Ingress 对象

我们已经部署了 nginx ingress controller 并将其暴露到外网，并且创建好了两个应用，接下来我们就可以定义一个 ingress 对象，来把两个应用代理出集群。

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-app-ingress
spec:
  ingressClassName: nginx
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
```

上述 yaml 文件定义了一个 Ingress 对象，其中 `ingress.spec.rules` 便是 ingress 的代理规则集合。

我们先看 host 字段，他的值必须是一个标准的域名格式字符串，而不能是 IP 地址。而 host 字段定义的值，就是这个 Ingress
的入口。这样就意味着，当用户访问`demo-app.example.com`的时候，实际访问到的就是这个 Ingress 对象。这样，Kubernetes 就能使用 IngressRule
来对你的请求进行下一步转发。

接下来是 path 字段。你可以简单理解为，这里的每个 path 都对应一个后端 Service。所以，我们例子里，定义了两个 path，他们分别对应 demo-app-1 和 demo-app-2
这两个 Deployment 的 Service（即：demo-app-1-svc 和 demo-app-2-svc）。

每条 http 规则包含以下信息：一个 host 配置项（比如`demo-app.example.com`），path 列表（比如：`/demo-app-1`和`/demo-app-2`），每个
path 都关联一个 backend（比如：`demo-app-1-svc`的 80 端口）。在 LoadBalancer 将流量转发到 backend 之前，所有的入站请求都要先匹配 host 和
path。

当没有匹配到规则中的任意一组 host 和 path 时，`ingress.spec.defaultBackend` 中定义的默认 backend 将会生效，将不匹配 host 和 path
的流量转发至 defaultBackend 处理。

我们将上述 yaml 保存为 ingress.yaml，并通过以下命令直接创建 ingress 对象：

```bash
kubectl apply -f ingress.yaml
```

接下来，我们可以查看这个 ingress 对象

```bash
$ kubectl get ingresses.networking.k8s.io
NAME               CLASS    HOSTS                  ADDRESS   PORTS   AGE
demo-app-ingress   <none>   demo-app.example.com             80      5m39s

$ kubectl describe ingresses.networking.k8s.io demo-app-ingress
Name:             demo-app-ingress
Labels:           <none>
Namespace:        ingress-nginx
Address:
Default backend: demo-app-1-svc:80 (172.20.145.127:80,172.20.187.251:80)
Rules:
  Host                  Path  Backends
  ----                  ----  --------
  demo-app.example.com
                        /demo-app-1   demo-app-1-svc:80 (172.20.145.127:80,172.20.187.251:80)
                        /demo-app-2   demo-app-2-svc:80 (172.20.40.180:80,172.20.43.118:80,172.20.62.63:80)
Annotations:            <none>
Events:                 <none>
```

从 rule 规则可以看到， 我们的定义的 Host 是 `demo-app.example.com`，他有两条转发规则（Path），分别转发给 demo-app-1-svc 和
demo-app-2-svc。

当然，在 Ingress 的 yaml 文件里，你还可以定义多个 Host，来为更多的域名提供负载均衡服务。

接下来，我们就可以通过访问这个 Ingress 的地址和端口，访问到我们前面部署的应用了，比如，当我们访问 `http://demo-app.example.com/demo-app-2` 时，应该是
demo-app-2 这个 Deployment 负责响应我的请求，当创建 LoadBalance 时选择外网模式并绑定了 EIP，那么可以直接通过外网访问，我们在本地 `/etc/hosts` 中添加 Service 外网 ip 以及域名后即可直接从外网通过域名访问。如果是在内网模式下，仅 VPC 内的资源可以通过 Ingress 访问。

```bash
$ cat /etc/hosts
......

xxx.yy.xxx.yy demo-app.example.com
```

```bash
$ curl http://demo-app.example.com/demo-app-2
Scheme: http
Server address: 172.20.43.118:80
Server name: demo-app-2-5f6c5df698-rvsmc
Date: 12/Jan/2022:02:56:38 +0000
URI: /demo-app-2
Request ID: ba34c07f5cc78e74629041df5568977a
```

### 五、TLS 支持

在上述的 ingress 对象中，我们没有给 Host 指定 TLS 证书，ingress controller 支持通过指定一个包含 TLS 私钥以及证书的 secret 来加密站点。

我们先创建一个包含 tls.crt 以及 tls.key 的 secret，在生成证书的时候，需要确保证书的 CN 包含`demo-app.example.com`，并将证书内容使用 base64
编码。

```bash
$ HOST=demo-app.example.com

$ openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=${HOST}/O=${HOST}"
Generating a RSA private key
................................+++++
................................+++++
writing new private key to 'tls.key'
```

```bash
$ kubectl create secret tls demo-app-tls --key tls.key --cert tls.crt
secret/demo-app-tls created

$ kubectl describe secret demo-app-tls
Name:         demo-app-tls
Namespace:    ingress-nginx
Labels:       <none>
Annotations:  <none>

Type:  kubernetes.io/tls

Data
====
tls.crt:  1229 bytes
tls.key:  1708 bytes
```

然后在 ingress 对象中，通过 ingress.spec.tls 字段引用 secret，ingress controller 即会加密来保护客户端到 ingress 之间的通信管道。

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-app-ingress
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - demo-app.example.com
      secretName: demo-app-tls
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
```

此时可通过 https 协议访问 ingress，但需要注意的是由于 ingress 的证书是我们自签生成的，所以在使用 curl 等工具访问时，需要略过证书校验，**生产环境中建议您使用经过 CA
机构签名的 TLS 证书**。

```bash
$ curl --insecure https://demo-app.example.com/demo-app-2
Scheme: http
Server address: 172.20.40.180:80
Server name: demo-app-2-5f6c5df698-pvr45
Date: 12/Jan/2022:03:19:58 +0000
URI: /demo-app-2
Request ID: 4cc35ddb1a301977f0477ded4c09d5df
```

### 六、设置访问白名单

部分场景下，我们的业务只允许指定的 IP 地址访问，这可以通过添加 annotations 来实现，即
`nginx.ingress.kubernetes.io/whitelist-source-range`，值则是 CIDR 列表，多个 CIDR 间用 ","分开。示例如下：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/whitelist-source-range: 172.16.0.0/16,172.18.0.0/16
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - demo-app.example.com
      secretName: demo-app-tls
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
```
