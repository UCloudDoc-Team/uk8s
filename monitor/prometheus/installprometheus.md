{{indexmenu_n>0}}
## 部署Prometheus

### 前言

对于一套Kubernetes集群而言，需要监控的对象大致可以分为以下几类：

* **Kubernetes系统组件：**Kubernetes内置的系统组件一般有apiserver、controller-manager、etcd、kubelet等，为了保证集群正常运行，我们需要实时知晓其当前的运行状态。

* **底层基础设施：** Node节点(虚拟机或物理机)的资源状态、内核事件等。

* **Kubernetes对象：** 主要是Kubernetes中的工作负载对象，如Deployment、DaemonSet、Pod等。

* **应用指标：** 应用内部需要关心的数据指标，如httpRequest。

### 部署Prometheus

在Kubernetes中部署Prometheus，除了手工方式外，CoreOS开源了Prometheus-Operator以及kube-Prometheus项目，使得在K8S中安装部署Prometheus变得异常简单。下面我们介绍下如何在UK8S中部署Kube-Prometheus。

#### 1、关于Prometheus-Operator
Prometheus-operator的本职就是一组用户自定义的CRD资源以及Controller的实现，Prometheus Operator这个controller有BRAC权限下去负责监听这些自定义资源的变化，并且根据这些资源的定义自动化的完成如Prometheus Server自身以及配置的自动化管理工作。

在K8S中，监控metrics基本最小单位都是一个Service背后的一组pod，对应Prometheus中的target，所以prometheus-operator抽象了对应的CRD类型" ServiceMonitor "，这个ServiceMonitor通过 sepc.selector.labes来查找对应的Service及其背后的Pod或endpoints，通过sepc.endpoint来指明Metrics的url路径。
以下面的CoreDNS举例，需要pull的Target对象Namespace为kube-system，kube-app是他们的labels，port为metrics。
```
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    k8s-app: coredns
  name: coredns
  namespace: monitoring
spec:
  endpoints:
  - bearerTokenFile: /var/run/secrets/kubernetes.io/serviceaccount/token
    interval: 15s
    port: metrics
  jobLabel: k8s-app
  namespaceSelector:
    matchNames:
    - kube-system
  selector:
    matchLabels:
      k8s-app: kube-dns
```

#### 2、准备工作

ssh到任意一台Master节点，克隆kube-prometheus项目。该项目源自CoreOS开源的[kube-prometheus](https://github.com/coreos/kube-prometheus)，与原始项目相比，主要作为以下优化：

+ 将Prometheus和AlbertManager的数据存储介质由emptyDir改为UDisk，提升稳定性，避免数据丢失；

+ 将镜像源统一修改为UHub，避免镜像拉取失败的情况出现；

+ 新增UK8S专属文件目录，用于配置监控controller-manager、schduler、etcd；

+ 将执行文件按目录划分，便于修改及阅读。

```
yum install git -y
git clone https://github.com/zhangpengboshanghai/kube-prometheus.git
```

####  3、修改UK8S专属文件配置参数
在manifests目录下有UK8S目录，这批配置文件主要用于为UK8S中的controller-manager、schduler、etcd手动创建endpoints和svc，便于Prometheus Server通过ServiceMonitor来采集这三个组件的监控数据。
```
cd /kube-prometheus/manifests/uk8s
# 修改以下两个文件，将其中的IP替换为你自己UK8S Master节点的内网IP
vi controllerManagerAndScheduler_ep.yaml
vi etcd_ep.yaml
```
#### 4、 备注
上面提到要修改controllerManagerAndScheduler_ep.yaml和etcd_ep.yaml这两个文件，这里解释下原因。
由于UK8S的ETCD、Scheduler、Controller-Manager都是通过二进制部署的，为了能通过配置"ServiceMonitor"实现Metrics的抓取，我们必须要为其在K8S中创建一个SVC对象，但由于这三个组件都不是Pod，因此我们需要手动为其创建Endpoints。
```
apiVersion: v1
kind: Endpoints
metadata:
  labels:
    k8s-app: etcd
  name: etcd
  namespace: kube-system
subsets:
- addresses:
  - ip: 10.7.35.44 # 替换成master节点的内网IP
    nodeName: etc-master2
  ports:
  - name: port
    port: 2379
    protocol: TCP
- addresses:
  - ip: 10.7.163.60 # 同上
    nodeName: etc-master1
  ports:
  - name: port
    port: 2379
    protocol: TCP
- addresses:
  - ip: 10.7.142.140 #同上
    nodeName: etc-master3
  ports:
  - name: port
    port: 2379
    protocol: TCP
```

#### 5、部署Prometheus Operator

先创建一个名为monitor的NameSpace，Monitor创建成功后，直接部署Operator，Prometheus Operateor以Deployment的方式启动，并会创建前面提到的几个CRD对象。
```
# 创建Namespace
kubectl apply -f  00namespace-namespace.yaml
# 创建Secret，给到Prometheus Server抓取ETCD数据时使用
kubectl -n monitoring create secret generic etcd-certs --from-file=/etc/kubernetes/ssl/ca.pem --from-file=/etc/kubernetes/ssl/etcd.pem --from-file=/etc/kubernetes/ssl/etcd-key.pem
# 创建Operator
kubectl apply -f operator/
# 查看operator启动状态
kubectl get po -n monitoring
# 查看CRD
kubectl get crd -n monitoring
```

#### 6、部署整套CRD

比较关键的有Prometheus Server、Grafana、 AlertManager、ServiceMonitor、Node-Exporter等，这些镜像已全部修改为UHub官方镜像，因此拉取速度相对比较快。
```
kubectl apply -f adapter/ 
kubectl apply -f alertmanager/ 
kubectl apply -f node-exporter/ 
kubectl apply -f kube-state-metrics/ 
kubectl apply -f grafana/ 
kubectl apply -f prometheus/ 
kubectl apply -f serviceMonitor/
kubectl apply -f uk8s/
```
我们可以通过以下命令来查看应用拉取状态。
```
kubectl -n monitoring get po
```
由于默认所有的SVC 类型均为ClusterIP，我们将其改为LoadBalancer，方便演示。
```
 kubectl edit svc/prometheus-k8s -n monitoring
# 修改为type: LoadBalancer
[root@10-9-52-233 manifests]# kubectl get svc -n monitoring
# 获取到Prometheus Server的EXTERNAL-IP及端口
```
可以看到，所有K8S组件的监控指标均已获取到。

#### 7、监控应用指标
我们先来部署一组Pod及SVC，该镜像里的主进程会在8080端口上输出metrics信息。
```
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: example-app
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: example-app
    spec:
      containers:
      - name: example-app
        image: uhub.service.ucloud.cn/uk8s_public/instrumented_app:latest
        ports:
        - name: web
          containerPort: 8080
---
kind: Service
apiVersion: v1
metadata:
  name: example-app
  labels:
    app: example-app
spec:
  selector:
    app: example-app
  ports:
  - name: web
    port: 8080
```
再创建一个ServiceMonitor来告诉prometheus server需要监控带有label为app: example-app的svc背后的一组pod的metrics。
```
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: example-app
  labels:
    team: frontend
spec:
  selector:
    matchLabels:
      app: example-app
  endpoints:
  - port: web

```
打开浏览器访问Prometheus Server，进入target发现已经监听起来了，对应的config里也有配置生成和导入。

#### 8、说明

该文档只适用于kubernetes 1.14以上的版本，如果你的kubernetes版本为1.14以下，可以使用[release-0.1](https://github.com/coreos/kube-prometheus/tree/release-0.1).


