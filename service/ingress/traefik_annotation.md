## traefik 高级用法

### 通过路径的路由

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: cheeses
  annotations:
    kubernetes.io/ingress.class: traefik
    traefik.frontend.rule.type: PathPrefixStrip
spec:
  rules:
  - host: cheeses.minikube
    http:
      paths:
      - path: /stilton
        backend:
          serviceName: stilton
          servicePort: http
      - path: /cheddar
        backend:
          serviceName: cheddar
          servicePort: http
      - path: /wensleydale
        backend:
          serviceName: wensleydale
          servicePort: http
```

以这个Ingress为例，我们分别定义了3个路径对应3个服务( /stilton对应stilton，/cheddar对应cheddar，/wensleydale对应wensleydale)
，但值得注意的一点，cheses.minikube/stilton会将/stilton传到容器中，也就是说必须增加转发的回写，否则容器中的程序必须存放在/stilton路径下才能得以访问，这里使用traefik.frontend.rule.type的注释从url路径中去掉转发的路径到容器中。

---

### 指定路由优先级

有时您需要为入口路由指定优先级，尤其是在处理通配符路由时。这可以通过添加 traefik.frontend.priority 注释来完成，即：

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: wildcard-cheeses
  annotations:
    kubernetes.io/ingress.class: traefik
    traefik.frontend.priority: "1"
spec:
  rules:
  - host: *.minikube
    http:
      paths:
      - path: /
        backend:
          serviceName: stilton
          servicePort: http

kind: Ingress
metadata:
  name: specific-cheeses
  annotations:
    kubernetes.io/ingress.class: traefik
    traefik.frontend.priority: "2"
spec:
  rules:
  - host: specific.minikube
    http:
      paths:
      - path: /
        backend:
          serviceName: stilton
          servicePort: http
```

---

### 禁止Ingress 传递主机头

要禁用每个入口资源传递主机标头traefik.frontend.passHostHeader，请将入口上的注释设置为"false"。

这是一个示例定义：

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: example
  annotations:
    kubernetes.io/ingress.class: traefik
    traefik.frontend.passHostHeader: "false"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /static
        backend:
          serviceName: static
          servicePort: https
```

以及一个示例服务定义：

```
apiVersion: v1
kind: Service
metadata:
  name: static
spec:
  ports:
  - name: https
    port: 443
  type: ExternalName
  externalName: static.otherdomain.com
```

如果您要访问example.com/static该请求，那么将传递给static.otherdomain.com/static，static.otherdomain.com并将收到带有Host头的请求static.otherdomain.com。

---

### 流量分流

可以使用服务权重在多个部署之间以细粒度方式拆分Ingress流量。

一个规范用例是canary版本，其中代表较新版本的部署将随着时间的推移接收最初较小但不断增加的请求部分。在Traefik中可以这样做的方法是指定应该进入每个部署的请求的百分比。

例如，假设一个应用程序my-app在版本1中运行。较新的版本2即将发布，但对生产中运行的新版本的稳健性和可靠性的信心只能逐渐获得。因此，my-app-canary创建新部署并将其缩放到足以获得1％流量份额的副本计数。与此同时，像往常一样创建一个Service对象。

Ingress规范看起来像这样：

apiVersion: extensions/v1beta1 kind: Ingress metadata: annotations:
traefik.ingress.kubernetes.io/service-weights: | my-app: 99% my-app-canary: 1% name: my-app spec:
rules:

- http: paths:
  - backend: serviceName: my-app servicePort: 80 path: /
  - backend: serviceName: my-app-canary servicePort: 80 path: /
    记下traefik.ingress.kubernetes.io/service-weights注释：它指定引用的后端服务之间的请求分配，my-app以及my-app-canary。根据这一定义，Traefik将99％的请求路由到my-app部署支持的pod
    ，并将1％的请求路由到支持的pod my-app-canary。随着时间的推移，该比例可能会慢慢转向金丝雀部署，直到它被认为取代之前的主要应用程序，步骤如5％/ 95％，10％/
    90％，50％/ 50％，最后100％/ 0％。

必须满足一些条件才能正确应用服务权重：

关联的服务后端必须共享相同的路径和主机。 所有服务后端共享的总百分比必须达到100％（但请参阅省略最终服务的部分）。 百分比值被解释为浮点数到支持的精度，如注释文档中所定义。
