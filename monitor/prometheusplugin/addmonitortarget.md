# 添加监控目标

一个监控目标可理解为Prometheus中的一个Target或Job. 原生Prometheus既支持静态配置监控目标，也支持动态服务发现。

由于K8S的Pod被设置非永久性的资源，为了正确地抓取到每个应用对应的Pod监控数据，Prometheus Operator引入了Service
Monitor机制，通过监听Service后面的Endpoint（可认为是健康的Pod）来实现监控数据的采集。

因此，为了抓取一组Pod的监控数据，我们必须为这组Pod创建一个对应的Service，并暴露对应的Metrics端口。

> !
> 这里需要强调的是，Service必须暴露Metrics端口，而非业务端口。如我们有一个应用，其应用端口为80，Metrics端口为9200，则供Prometheus抓取数据的Service端口必须是9200，如果设置为80，则不能抓取到任何监控数据。

### 操作说明

#### 1. 部署应用

在下面这个例子中，我们部署了一个示例应用，该应用为一个web应用程序，其容器对外暴露了两个端口，一个是业务端口80，另一个是Metrics端口8080.
并且创建了一个Service，暴露的端口与容器端口一致。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: example-app
  template:
    metadata:
      labels:
        app: example-app
    spec:
      containers:
      - name: example-app
        image: uhub.service.ucloud.cn/uk8s_public/instrumented_app:latest
        ports:
        - name: metrics
          containerPort: 8080
        - name: web
          containerPort: 80
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
  - name: metrics
    port: 8080
  - name: web
    port: 80
```

#### 2、添加监控目标

我们在UK8S的监控中心-->监控目标页面，直接选中该Service，端口名称选择“metrics”，抓取路径一般默认填写“/metrics”，如果监控指标的路径是自定义请咨询业务方。

![](images/prometheus/addtarget.jpg)

- 命名空间：kubernetes集群上部署server的namespace名称
- 服务名称：kubenetes集群上要获取metric的service的名称
- 端口名称：获取metric的service上的端口名称
- 路径：获取metric的service访问路径

#### 3、查看监控目标

添加完毕后，我们可以打开Prometheus 控制台，查看该监控目标是否已添加成功。
