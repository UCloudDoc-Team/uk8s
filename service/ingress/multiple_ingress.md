
## ingress 高级用法

### 多个Ingress Controller SVC
如果您只运行了一个ingress controller，想通过多个ULB对外提供服务（例如需要在ULB中绑定SSL证书），可以参考这个yaml文件。
```
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx2
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
```
这里我新建了一个把ingress controller暴露出集群的svc，名为ingress-nginx2，这时针对这个nginx ingress controller就拥有了2个svc,对应了2个ULB。
```
[root@10-10-10-194 ~]# kubectl get svc -n ingress-nginx
NAME             TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)                      AGE
ingress-nginx    LoadBalancer   172.17.23.246   xx.xx.xx.xx     80:32677/TCP,443:39787/TCP   10d
ingress-nginx2   LoadBalancer   172.17.7.114    yy.yy.yy.yy     80:47962/TCP,443:45958/TCP   29m
```
 用户可以解析增加n1 xx.xx.xx.xx和n2 yy.yy.yy.yy进行区分流量入口，这个操作流程将使用同一套ingress controller，多个SVC的使用场景，逻辑如下图。
 ```
 ULB1            ULB2
  |               |
ing_svc1       ing_svc2
  |               |
  -----------------
          |
  ingress controller
          |
  -----------------      
  |               |
app_svc1       app_svc2
  |               |
app_pod1       app_pod2   
```

### 多个 Ingress Controller

如果您运行了多个ingress controller在您的kubernetes集群中（例如同时运行了nginx和traefik），则需要在使用ingress资源对象时进行声明操作，例如：

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: traefik-web-ui
  namespace: kube-system
  annotations:
    kubernetes.io/ingress.class: traefik
    # 声明使用 traefik 作为指定的ingress controller
    # 也可以替换成 nginx 等已安装的ingress controller
spec:
  rules:
  - host: traefik-ui.minikube
    http:
      paths:
      - path: /
        backend:
          serviceName: traefik-web-ui
          servicePort: web
```

> 如果您部署了不同类型的ingress controller（例如nginx和traefik），而不指定注释类型，将导致这两个或者所有的ingress controller都在努力满足ingress的需求，并且所有的ingress controller都在争抢更新ingress的状态。

---

### 使用 DaemonSet 部署

可以将Traefik与Deployment或DaemonSet对象一起使用，而这两个选项各有利弊：

* 使用Deployment时，可伸缩性可以更好，因为在使用DaemonSet时您将拥有每个节点的单一Pod模型，而在使用Deployment时，基于环境您可能需要更少的Pod。
* 当节点加入群集时，DaemonSet会自动扩展到新节点，而Deployment仅在需要时在新节点上进行调度。
* DaemonSet 确保只有一个pod副本在任何单个节点上运行。如果要确保两个pod不在同一节点上，则需要 Deployment 进行设置。

这是一个DaemonSet的部署示例。这里还可以使用spec.template.spec.nodeSelector，则DaemonSet控制器将在与该节点选择器匹配的Node，同样，还可以使用spec.template.spec.affinity，控制部署的亲和性。

```
kind: DaemonSet
apiVersion: extensions/v1beta1
metadata:
  name: traefik-ingress-controller
  namespace: kube-system
  labels:
    k8s-app: traefik-ingress-lb
spec:
  template:
    metadata:
      labels:
        k8s-app: traefik-ingress-lb
        name: traefik-ingress-lb
    spec:
      serviceAccountName: traefik-ingress-controller
      terminationGracePeriodSeconds: 60
      containers:
      - image: traefik
        name: traefik-ingress-lb
        ports:
        - name: http
          containerPort: 80
          hostPort: 80
        - name: admin
          containerPort: 8080
        args:
        - --api
        - --kubernetes
        - --logLevel=INFO
      nodeSelector: 
        node: ingress-traefik
```

----

### 多个 Ingress-traefik Controller

有时，多个Traefik Deployments应该同时运行。例如，可以设想一个部署对内部提供服务，另一个对外部提供服务。

对于这种情况，建议通过标签对Ingress对象进行分类，并相应地labelSelector为每个Traefik部署配置选项。为了坚持上面的内部/外部示例，所有用于内部流量的Ingress对象都可以接收traffic-type: internal标签，而为外部流量指定的对象会收到traffic-type: external标签。然后，Traefik Deployments上的标签选择器将分别为traffic-type=internal和traffic-type=external。

