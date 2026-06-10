## Traefik Ingress

### 什么是Ingress

Ingress 是从Kubernetes集群外部访问集群内部服务的入口，同时为集群内的Service提供七层负载均衡能力。

一般情况下，Service和Pod仅可在集群内部通过IP地址访问，所有到达集群边界的流量或被丢弃或被转发到其他地方，前面的service章节我们提供了创建LoadBalancer类型的Service方法，借助于Kubernetes提供的扩展接口，UK8S会创建一个与该Service对应的负载均衡服务即ULB来承接外部流量，并路由到集群内部。但在诸如微服务等场景下，一个Service对应一个负载均衡器，管理成本明显过高，Ingress因此应运而生。

我们可以把Ingress理解为Service的”Service”，为后端不同Service提供代理的负载均衡服务，我们可以在Ingress配置可供外部访问URL、负载均衡、SSL、基于名称的虚拟主机等。

### 什么是Traefik

Traefik是一个为了让部署微服务更加便捷而诞生的现代HTTP反向代理、负载均衡工具。 它支持多种后台 (Docker, Swarm, Kubernetes, Marathon, Mesos,
Consul, Etcd, …) 来自动化、动态的应用它的配置文件设置。

下面我们通过在UK8S中部署Traefik Ingress Controller，来了解一下Ingress的使用过程。

使用版本：Traefik 3.7.4

### 部署Ingress Controller

这里我们选择Traefik作为Ingress Controller，部署Traefik Ingress Controller非常简单，执行一下指令即可。

```shell
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/ingress_traefik/traefik_3.7.4.yaml
```

### 访问dashboard

- 使用端口转发到本地的8080端口

```shell
kubectl -n traefik port-forward svc/traefik 8080:80
```

- 浏览器访问 <http://dashboard.localhost:8080/dashboard/#/> 即可
