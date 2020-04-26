
## Traefik Ingress

### 什么是Ingress

Ingress 是从Kubernetes集群外部访问集群内部服务的入口，同时为集群内的Service提供七层负载均衡能力。

一般情况下，Service和Pod仅可在集群内部通过IP地址访问，所有到达集群边界的流量或被丢弃或被转发到其他地方，前面的service章节我们提供了创建LoadBalancer类型的Service方法，借助于Kubernetes提供的扩展接口，UK8S会创建一个与该Service对应的负载均衡服务即ULB来承接外部流量，并路由到集群内部。但在诸如微服务等场景下，一个Service对应一个负载均衡器，管理成本明显过高，Ingress因此应运而生。

我们可以把Ingress理解为Service的”Service”，为后端不同Service提供代理的负载均衡服务，我们可以在Ingress配置可供外部访问URL、负载均衡、SSL、基于名称的虚拟主机等。

### 什么是Traefik
Traefik是一个为了让部署微服务更加便捷而诞生的现代HTTP反向代理、负载均衡工具。 它支持多种后台 (Docker, Swarm, Kubernetes, Marathon, Mesos, Consul, Etcd, …) 来自动化、动态的应用它的配置文件设置。

下面我们通过在UK8S中部署Traefik Ingress Controller，来了解一下Ingress的使用过程。

使用版本：Traefik 1.7

### 一、部署Ingress Controller
这里我们选择Traefik作为Ingress Controller，部署Traefik Ingress Controller非常简单，执行一下指令即可。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/ingress_traefik/mandatory.yaml
```

在mandatory.yaml这个文件里，正是Traefik官方提供的安装文件[traefik-rbac.yaml](https://github.com/containous/traefik/blob/v1.7/examples/k8s/traefik-rbac.yaml)和[traefik-deployment.yaml](https://github.com/containous/traefik/blob/v1.7/examples/k8s/traefik-deployment.yaml)，我们可以把yaml文件下载到本地仔细研读下，从执行结果来看大家可以看出，我们在这里创建了ClusterRole、ClusterRoleBinding、pod、serviceaccount。
```
clusterrole.rbac.authorization.k8s.io/traefik-ingress-controller created
clusterrolebinding.rbac.authorization.k8s.io/traefik-ingress-controller created
serviceaccount/traefik-ingress-controller created
deployment.extensions/traefik-ingress-controller created
```

### 二、将Traefik ingress controller暴露出集群
上面我们已经在UK8S中部署了一个traefik ingress controller，但这个ingress服务只能在集群内部可达，为了在集群外部可达，我们还需要为此创建一个外部可达的Service，这里我们选择创建一个LoadBalancer类型的Service，并将其暴露到外网。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/ingress_traefik/Service.yaml
```

```
kind: Service
apiVersion: v1
metadata:
  name: traefik-ingress-service
  namespace: kube-system
spec:
  selector:
    k8s-app: traefik-ingress-lb
  ports:
    - protocol: TCP
      port: 80
      name: web
    - protocol: TCP
      port: 8080
      name: admin
  type: LoadBalancer
```
这个Service可以在官方yaml[traefik-deployment.yaml](https://github.com/containous/traefik/blob/v1.7/examples/k8s/traefik-deployment.yaml)中找到，根据UK8S使用对其进行了修改，spec.type由官方提供的 **NodePort** 改为了 **LoadBalancer** ，会自动生成一个EIP提供外部服务。

这个service的工作就是将traefik-ingress-service服务的80和8080端口暴露出去，其中，80端口为web服务端口，8080为管理端口。
部署完成我们可以直接通过 **<EIP>:8080** 访问管理页面。

### 三、通过traefik ingress暴露traefik dashboard
traefik dashboard是官方提供的一个管理界面，也是traefik ingress暴露的第一个服务。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/ingress_traefik/ui.yaml
```

可以研读一下这个yaml文件，这个yaml中包含两段，第一段是将traefik的dashboard创建一个service提供服务，暴露的服务同<EIP>:8080；然后第二段定义了一个ingress对象，这里的spec.rules.host=traefik-ui.minikube是我们的URL地址，spec.rules.http.paths.backend下定义了绑定的服务。

可以通过写入本机host文件， **<EIP> traefik-ui.minikube** ，然后浏览器查看 **traefik-ui.minikube** 是否成功，直接访问<EIP>无法查看dashboard，访问域名可以正常访问则设置成功。

