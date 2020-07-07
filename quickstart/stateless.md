
## 在UK8S中部署无状态服务

### 前言
在K8S中部署一个无状态服务是一件很简单的事，但要在K8S中部署一个健壮的无状态服务，则需要对K8S的各个概念有一个基础的了解。本文以Nginx为例来说明如何部署一个无状态应用，通过本文档，你将：

1. 了解Deployment的基础知识；

2. 如何ConfigMap保存配置文件，并实现热更新；

3. 如何将服务暴露到K8S集群外部；

### 1、部署一个高可用的Nginx服务

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: uhub.service.ucloud.cn/ucloud/nginx:latest
        ports:
        - containerPort: 80

```

在上面的示例中：

1. 我们声明要创建一个名为"nginx-deployment"的Deployment，名字通过.metadata.name参数指定。

2. 该Deployment将创建2个一样的Pods，你也可以通过.spec.replicas参数来修改其数量。

3. selector 字段定义 Deployment 如何查找要管理的 Pods。 一般情况下，只需要与 Pod 模板（app: nginx）中定义的标签一致即可。更复杂的匹配规则不在我们的讨论范围内。

4. template 字段包含以下子字段：
    
   * Pod 标记为app: nginx，使用labels字段;

   * Pod 模板规范或 .template.spec 字段指示 Pods 运行一个容器nginx;

   * 创建一个容器并使用name字段将其命名为 nginx;


将上述内容保存为nginx-deployment.yaml，我们可以在kubectl中执行以下命令来运行容器：

```shell

kubectl apply -f nginx-deployment.yaml 

```   


### 2、通过Configmap实现nginx配置文件的热更新

上面的例子我们只是运行起了一个nginx服务，但对于在线业务，我们还需要考虑如何运维问题，比如如何实现nginx配置文件的热更新。这里我们需要用到Kubernetes的ConfigMap功能。

1. 首先我们创建一个nginx配置文件。

```shell

cat  >www.conf <<EOF
server {
	server_name www.test.com;
	listen 80;
	root /app/webroot/;
}
EOF

```

2. 创建一个ConfigMap保存配置文件信息, 文件内容作为value, 可以自定义key, 也可以使用文件名作为key。

```shell

kubectl create configmap nginx-file --from-file=./www.conf  # 文件名作为key

kubectl create configmap nginx-file --from-file=www.conf=./www.conf # 自定义key（www.conf）


```

3. 创建一个Deployment，并将ConfigMap作为Volume挂载到Pod。


```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 2
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: uhub.service.ucloud.cn/ucloud/nginx:latest
        ports:
        - containerPort: 80
        volumeMounts:                        #挂载
        - name: nginxcon                    #调用下面定义的存储卷, 名字要一致
          mountPath: /etc/nginx/conf.d/    #pod容器目录
          readOnly: true                  #只读
      volumes:                           #创建一个存储卷
      - name: nginxcon                  #定义存储卷名字
        configMap:                     #定义存储卷类型为configMap
          name: nginx-file            #引用名字叫nginx-file的configmap, 

```

将配置信息从容器镜像中独立出来的好处是：1、不用为不同环境制作不同的镜像；2、实现配置文件的热更新。 在这个例子中，我们可以尝试去修改ConfigMap中的配置信息，然后在登录到容器中，我们会发现nginx的配置文件会也会被修改，已容器并不需要重启。


### 3、将应用暴露到集群外部

上面我们已经部署好nginx应用，那如何从集群内、集群外、互联网访问这个应用呢？ 这里就涉及到Service这个K8S对象了，Service定义了一组Pod及访问它的方式。一个简单的类比，Service可以认为是负载均衡，而Pod则是云主机。


#### 1. 创建一个只能在集群内访问的Service

```yaml

apiVersion: v1
kind: Service
metadata:
  name: nginx-svc-clusterip
spec:
  type: ClusterIP
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  selector:
    app: nginx

```
在上面的示例中，

1. 我们创建了一个名为nignx-svc-clusterip的service；

2. 该service的类型为ClusterIP，通过spec.type字段指定；

3. 该service对外暴露的端口为80，TCP协议，后端节点（可认为是负载均衡的RealServer）的端口也是80，这些信息都通过spec.ports参数来指定。

4. 和Deployment类似，这里selector 字段定义 Service 如何查找 Pods并将流量转发给它。 一般情况下，只需要与 Pod 模板（app: nginx）中定义的标签一致即可。

#### 2. 创建一个可在VPC内其他服务访问的Service

ClusterIP类型的Service在创建成功后，K8S将为其分配一个IP，但该IP只在集群内可达。 如果我们的服务要被云账户下的其他服务（比如云主机）访问，应该怎么办? UK8S集成了内网ULB，我们只需要创建一个LoadBalancer类型的Service接口。

```yaml

apiVersion: v1
kind: Service
metadata:
  name: nginx-deployment-vpc
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "inner"  
     # ULB类型，这里表示为内网ULB
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "tcp"       
     # 用于声明ULB协议类型，并非应用协议，tcp和udp均代表ULB4，https和http均代表ULB7；
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type": "port"
     # 对于ULB4而言，不论容器端口类型是tcp还是udp，均建议显式声明为port。
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  selector:
    app: nginx

```

在上面的例子中,

1. 我们创建了一个LoadBalancer类型的Service，K8S姜维该Service分配一个ExternalIP，IP类型为内网IP。在UK8S中，意味着这将在你的云账户下创建一个ULB（云负载均衡）。

2. 通过metadata.annotations，我们声明该ULB的类型为inner，这意味着该ULB只能在VPC内可达。

3. 我们还通过annontaions来声明ULB的协议类型，以及Vserver的健康检查方式。

#### 3、创建一个可被互联网访问的Service

下面我们将介绍如何将部署在UK8S中的服务暴露到公网。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-deployment-internet
  annotations:
    "service.beta.kubernetes.io/ucloud-load-balancer-type": "outer"
    # 代表ULB网络类型，outer为外网，inner为内网；outer为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol": "tcp"
    # 表示ULB协议类型，tcp与udp等价，表示ULB4；http与httpS等价，表示ULB7；tcp为默认值，此处可省略。
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-bandwidth": "2" 
    # bandwidth下默认为2Mpbs,建议显式声明带宽大小，避免费用超标。
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-chargetype": "month" 
    # 付费模式，支持month，year，dynamic，默认为month
    "service.beta.kubernetes.io/ucloud-load-balancer-eip-quantity": "1" 
    # 付费时长，默认为1，chargetype为dynimic时无效    
spec:
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  selector:
    app: nginx

```
在上面的实例中：

1. 我们创建一个LoadBalancer类型的Service，K8S将为该Service分配一个ExternalIP，IP类型为外网弹性IP，在UK8S中，这意味着将在你的云账户下创建一个外网ULB，**并产生费用**。

2. ULB的相关参数都是通过meta.annotations来指定的。

在测试完毕后，我们可以删除该Service，避免持续产生费用。

```shell

kubectl delete service nginx-deployment-internet

```


