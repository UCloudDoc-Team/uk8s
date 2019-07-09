# Nginx Ingress

{{indexmenu_n>0}}

\#\#\#什么是Ingress

Ingress 是从Kubernetes集群外部访问集群内部服务的入口，同时为集群内的Service提供七层负载均衡能力。

一般情况下，Service和Pod仅可在集群内部通过IP地址访问，所有到达集群边界的流量或被丢弃或被转发到其他地方，前面的service章节我们提供了创建LoadBalancer类型的Service方法，借助于Kubernetes提供的扩展接口，UK8S会创建一个与该Service对应的负载均衡服务即ULB来承接外部流量，并路由到集群内部。但在诸如微服务等场景下，一个Service对应一个负载均衡器，管理成本明显过高，Ingress因此应运而生。

我们可以把Ingress理解为Service的”Service”，为后端不同Service提供代理的负载均衡服务，我们可以在Ingress配置可供外部访问URL、负载均衡、SSL、基于名称的虚拟主机等。

下面我们通过在UK8S中部署Nginx Ingress Controller，来了解一下Ingress的使用过程。

\#\#\# 一、部署Ingress Controller

为了使Ingress正常工作，集群内必须部署Ingress
Controller。与其他类型的控制器不同，其他类型的控制器如Deployment通常作为kube-controller-manager二进制文件的一部分，在集群启动时自动运行。而Ingress
Controller则需要自行部署，Kubernetes社区提供了以下Ingress Controller供选择，分别如下： 1、Nginx
2、HAProxy 3、Envoy 4、Traefik

这里我们选择Nginx作为Ingress Controller，部署Nginx Ingress Controller非常简单，执行以下指定即可。

\`\`\` kubectl apply -f
<http://uk8s.cn-bj.ufileos.com/yaml/ingress/nginx/mandatory.yaml> \`\`\`

在mandatory.yaml这个文件里，正是Nginx官方为你维护的Ingress
Controller的定义，我们可以把yaml文件下载到本地仔细研读下。这里简要简述下部分yaml字段的意义。

这个yaml定义了一个使用nginx-ingress-controller作为镜像的pod副本集，这个Pod主要功能就是一个监听Ingress对象以及它所代理的后端Service变化的控制器。当一个新的Ingress对象由用户创建后，控制器会根据Ingress对象所定义的内容，生成一份对应的Nginx配置文件（也就是我们熟知的/etc/nginx/nginx.conf），并使用这个配置文件启动一个Nginx服务。而一旦Ingress对象被更新，控制器会更新这个配置文件。需要注意的是，如果只是被代理的Service对象被更新，控制器所管理的nginx服务不需要重新加载，这是因为nginx-ingress-controller通过nginx
lua实现了upstream的动态配置。

另外，在这个yaml文件中，我们还看到定义了ConfigMap，nginx-ingress-controller可以通过ConfigMap对象来对Nginx配置文件进行定制，示例如下：

``` yaml

 kind: ConfigMap
 apiVersion: v1
 metadata:
     name: nginx-configuration
     namespace: ingress-nginx
     labels:
         app.kubernetes.io/name: ingress-nginx
         app.kubernetes.io/part-of: ingress-nginx
data:
  map-hash-bucket-size: "128"
  ssl-protocols: SSLv2
```

需要注意的是，ConfigMap中的key和value只支持字符串，因此对于整数等类型，需要使用双引号，例如"100"，详细资料见\[Nginx-Ingress-ConfigMap\](<https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/>)。

本质上，这个Nginx-ingress-controller，其实是一个可以根据Ingress对象和被代理后端Service的变化，自动进行更新的Nginx负载均衡器。

容器默认使用UTC时间，如果要使用宿主机时区，参见\[Pod时区问题\](../../q/container)

\#\#\# 二、将nginx ingress controller暴露出集群

上面我们已经在UK8S中部署了一个nginx ingress
controller，但这个Nginx服务只能在集群内部可达，为了在集群外部可达，我们还需要为此创建一个外部可达的Service，这里我们选择创建一个LoadBalancer类型的Service，并将其暴露到外网。

\`\`\` apiVersion: v1 kind: Service metadata:

    name: ingress-nginx
    namespace: ingress-nginx
    labels:
      app.kubernetes.io/name: ingress-nginx
      app.kubernetes.io/part-of: ingress-nginx

spec:

    type: LoadBalancer
    ports:
      - name: http
        port: 80
        targetPort: 80
        protocol: TCP
      - name: https
        port: 443
        targetPort: 443
        protocol: TCP
    selector:
      app.kubernetes.io/name: ingress-nginx
      app.kubernetes.io/part-of: ingress-nginx

\`\`\`

这个 Service 的唯一工作，就是将所有携带 ingress-nginx 标签的 Pod 的 80 和 433
端口暴露出去，我们可以通过以下方式获取到这个Service的外网访问入口。

\`\`\` bash-4.4\# kubectl get svc -n ingress-nginx NAME TYPE CLUSTER-IP
EXTERNAL-IP PORT(S) AGE ingress-nginx LoadBalancer 172.17.118.146
117.50.x.x 80:34947/TCP,443:48761/TCP 2d23h

\`\`\` 部署完Ingress Controller 和它所需要的 Service后
，我们就可以使用通过他来将集群内部的其他Service代理出去了。

\#\#\# 三、创建两个应用

在下面的yaml中，我们定义了2个镜像名为echo-nginx的应用，主要是输出nginx应用自身的一些全局变量。

\`\`\` apiVersion: extensions/v1beta1 kind: Deployment metadata:

    name: uhost

spec:

    replicas: 2
    selector:
      matchLabels:
        app: uhost
    template:
      metadata:
        labels:
          app: uhost
      spec:
        containers:
        - name: uhost
          image: uhub.service.ucloud.cn/jenkins_k8s_cicd/echo_nginx:v11
          ports:
          - containerPort: 80

\--- apiVersion: v1 kind: Service metadata:

    name: uhost-svc

spec:

    ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
    selector:
      app: uhost

\--- apiVersion: extensions/v1beta1 kind: Deployment metadata:

    name: uk8s

spec:

    replicas: 3
    selector:
      matchLabels:
        app:  uk8s
    template:
      metadata:
        labels:
          app: uk8s
      spec:
        containers:
        - name: uk8s
          image: uhub.service.ucloud.cn/jenkins_k8s_cicd/echo_nginx:v11
          ports:
          - containerPort: 80

\--- apiVersion: v1 kind: Service metadata:

    name: uk8s-svc
    labels:

spec:

    ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
    selector:
      app: uk8s

\`\`\`

我们将上述yaml保存为uk8s-ingrss-test-nginx.yaml，并执行如下命令创建应用。

\`\`\` kubectl apply -f uk8s-ingrss-test-nginx.yaml \`\`\`

\#\#\# 四、定义Ingress对象

我们已经部署了nginx ingress
controller并将其暴露到外网，并且创建好了两个应用，接下来，我们就可以定义一个ingress对象，来把两个应用代理出集群。

\`\`\` apiVersion: extensions/v1beta1 kind: Ingress metadata:

    name: uk8s-ingress

spec:

    rules:
    - host: uk8s.example.com
      http:
        paths:
        - path: /uhost
          backend:
            serviceName: uhost-svc
            servicePort: 80
        - path: /uk8s
          backend:
            serviceName: uk8s-svc
            servicePort: 80

\`\`\`

上述yaml文件定义了一个Ingress对象，其中ingress.spec.rules便是ingress的代理规则集合。

我们先看host字段，他的值必须是一个标准的域名格式字符串，而不能是IP地址。而host字段定义的值，就是这个Ingress的入口。这样就意味着，当用户访问uk8s.example.com的时候，实际访问到的就是这个Ingress对象。这样，Kubernetes就能使用IngressRule来对你的请求进行下一步转发。

接下来是path字段。你可以简单理解为，这里的每个path都对应一个后端Service。所以，我们例子里，定义了两个path，他们分别对应uhost和uk8s这两个Deployment的Service(即：uhost-svc和uk8s-svc)。

每条http规则包含以下信息：一个host配置项（比如uk8s.example.com），path列表（比如：/uhost），每个path都关联一个backend(比如uhost:80)。在loadbalancer将流量转发到backend之前，所有的入站请求都要先匹配host和path。

我们将上述yaml保存为ingress.yaml，并通过以下命名直接创建ingress对象：

\`\`\` kubectl apply -f ingress.yaml \`\`\`

接下来，我们可以查看这个ingress对象

\`\`\` bash-4.4\# kubectl get ingress NAME HOSTS ADDRESS PORTS AGE
uk8s-ingress uk8s.example.com 117.50.x.x 80, 443 4h56m bash-4.4\#
kubectl describe ingress uk8s-ingress Name: uk8s-ingress Namespace:
default Address: 117.50.x.x Default backend: default-http-backend:80
(\<none\>) TLS:

    uk8s-secret terminates uk8s.example.com

Rules:

    Host              Path  Backends
    ----              ----  --------
    uk8s.example.com
                      /uhost   uhost-svc:80 (<none>)
                      /uk8s    uk8s-svc:80 (<none>)

Annotations:

    kubectl.kubernetes.io/last-applied-configuration:  {"apiVersion":"extensions/v1beta1","kind":"Ingress","metadata":{"annotations":{},"name":"uk8s-ingress","namespace":"default"},"spec":{"rules":[{"host":"uk8s.example.com","http":{"paths":[{"backend":{"serviceName":"uhost-svc","servicePort":80},"path":"/uhost"},{"backend":{"serviceName":"uk8s-svc","servicePort":80},"path":"/uk8s"}]}}],"tls":[{"hosts":["uk8s.example.com"],"secretName":"uk8s-secret"}]}}

\`\`\`

从rule规则可以看到，
我们的定义的Host是uk8s.example.com，他有两条转发规则（Path）,分别转发给uhost-svc和uk8s-svc。

当然，在 Ingress 的 YAML 文件里，你还可以定义多个 Host，来为更多的域名提供负载均衡服务。

接下来，我们就可以通过访问这个 Ingress
的地址和端口，访问到我们前面部署的应用了，比如，当我们访问http://uk8s.example.com/uk8s
时，应该是uk8s这个Deployment负责响应我的请求，由于我们LoadBalance绑定了EIP，所以外网是可以访问的，我们在本地添加hosts即可直接从外网通过域名访问。

\#\#\# 五、TLS支持

在上述的ingress对象中，我们没有给Host指定TLS证书，ingress
controller支持通过指定一个包含TLS私钥以及证书的secret来加密站点。

我们先创建一个包含tls.crt以及tls.key的secret，在生成证书的时候，需要确保证书的CN包含"uk8s.example.com"，并将证书内容使用base64编码。

\`\`\` apiVersion: v1 data:

    tls.crt: base64 encoded cert
    tls.key: base64 encoded key

kind: Secret metadata:

    name: uk8s-tls
    namespace: default

type: kubernetes.io/tls

\`\`\`

我们也可以通过以下命令来快速创建secret：

\`\`\` kubectl create secret tls uk8s-tls --key /tmp/tls.key --cert
/tmp/tls.crt \`\`\`

然后在ingress对象中，通过ingress.spec.tls字段引用secret，ingress
controller即会加密来保护客户端到ingress之间的通信管道。

\`\`\` apiVersion: extensions/v1beta1 kind: Ingress metadata:

    name: uk8s-ingress

spec:

    tls:
    - hosts:
      - uk8s.example.com
      secretName: uk8s-tls
    rules:
    - host: uk8s.example.com
      http:
        paths:
        - path: /uhost
          backend:
            serviceName: uhost-svc
            servicePort: 80
        - path: /uk8s
          backend:
            serviceName: uk8s-svc
            servicePort: 80

\`\`\`

\#\#\# 六、设置访问白名单

部分场景下，我们的业务只允许制定的IP地址访问，这可以通过添加annotations来实现，即nginx.ingress.kubernetes.io/whitelist-source-range，值则是一段CIDR，多个网段用","分开。示例如下：

\`\`\` apiVersion: extensions/v1beta1 kind: Ingress metadata:

    name: uk8s-ingress
    annotations:
      nginx.ingress.kubernetes.io/whitelist-source-range: 172.16.0.0/16,172.18.0.0/16

spec:

    rules:
    - host: uk8s.example.com
      http:
        paths:
        - path: /uhost
          backend:
            serviceName: uhost-svc
            servicePort: 80
        - path: /uk8s
          backend:
            serviceName: uk8s-svc
            servicePort: 80

\`\`\`
