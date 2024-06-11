# 部署Kubernetes Dashboard

Dashboard是Kubernetes社区的一个Web开源项目，你可以通过Dashboard来部署更新应用、排查应用故障以及管理Kubernetes集群资源。另外，Dashboard还提供了集群的状态，以及错误日志等信息。下面我们介绍下如何在UK8S上部署、访问DashBoard。

## 部署Dashboard

UK8S集群没有默认安装Dashboard，如果你希望体验社区原生Dashboard，需要自行安装，[官方文档](https://github.com/kubernetes/dashboard/releases)。执行以下命令安装Dashboard，使用的镜像已经去掉了Https的证书限制。

### Dashboard v1.10.0

推荐kubernetes1.12及以下版本使用

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/service/dashboard.v1.10.0.yaml
```

官方兼容性提示

| kubernetes版本 | 1.8 | 1.9 | 1.10 | 1.11 | 1.12 | 1.13 |
| :----------: | :-: | :-: | :--: | :--: | :--: | :--: |
|     兼容性      |  ✓  |  ✓  |  ✓   |  ?   |  ?   |  ×   |

- ✓ 完全支持的版本范围。
- ? 由于Kubernetes API版本之间的存在变化，某些功能可能无法正常使用（测试未覆盖完整）。
- × 不支持的版本范围。

### Dashboard v2.0.0-rc1

推荐kubernetes1.13及以上版本使用

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/service/dashboard.v2.0.0-rc1.yaml
```

官方兼容性提示

| kubernetes版本 | 1.12 | 1.13 | 1.14 | 1.15 | 1.16 |
| :----------: | :--: | :--: | :--: | :--: | :--: |
|     兼容性      |  ?   |  ?   |  ?   |  ?   |  ✓   |

- ✓ 完全支持的版本范围。
- ? 由于Kubernetes API版本之间的存在变化，某些功能可能无法正常使用（测试未覆盖完整）。
- × 不支持的版本范围。

您可以通过访问或下载这个yaml文件，这个yaml中使用外网ULB暴露服务，产生额外的EIP费用。

Service的访问类型为HTTP，如果您希望使用HTTPS，请先购买SSL证书。

### Dashboard v3.0.0

- http

```shell
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/service/dashboard-http.v3.0.0.yaml
```

- https

```shell
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/service/dashboard-https.v3.0.0.yaml
```

| kubernetes版本 | 1.22 | 1.23 | 1.24 | 1.25 | 1.26 |
| :----------: | :--: | :--: | :--: | :--: | :--: |
|     兼容性      |  ?   |  ?   |  ?   |  ✓   |  ?   |

- ✓ 完全支持的版本范围。
- ? 由于Kubernetes API版本之间的存在变化，某些功能可能无法正常使用（测试未覆盖完整）。
- × 不支持的版本范围。

## 访问Dashboard

在上面的实例中，我们创建了一个类型为LoadBalancer的service，可直接通过Service 的外网IP（实际为ULB的外网IP）访问Dashboard。

获取到外网IP后，我们直接在浏览器中输入IP，到达登录页面，Dashboard支持kubeconfig和token两种身份验证方式，此处我们选择Token验证方式。将获取的token复制到输入框，点击登录，即可开始使用Dashboard。

> 注意： 使用chrome登录，会报证书错误，点高级之后进入即可（mac电脑需要直接在键盘上盲输thisisunsafe）

### Dashboard v1.10.0

查看EIP

```
kubectl get svc -n kube-system | grep kubernetes-dashboard-http
```

查看TOKEN

```
kubectl describe secret dashboard-ui -n kube-system
```

### Dashboard v2.0.0-rc1

查看EIP

```
kubectl get svc -n kubernetes-dashboard | grep kubernetes-dashboard
```

查看TOKEN

```
kubectl describe secret -n kubernetes-dashboard kubernetes-dashboard-token
```

### Dashboard v3.0.0

#### http

- http方式只支持本地地址访问

```shell
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard 8080:80
```

查看TOKEN

```shell
kubectl describe secret -n kubernetes-dashboard kubernetes-dashboard-token
```

##### 1.24及以上查看token

- 获取访问token，这里使用了kubernetes-dashboard下的sa kubernetes-dashboard创建了token，--duration表示token有效期

```shell
kubectl -n kubernetes-dashboard create token kubernetes-dashboard --duration=1h
```

#### https

- 获取外网ulb地址

```shell
kubectl -n kubernetes-dashboard get svc kubernetes-dashboard --output jsonpath="{.status.loadBalancer.ingress[*]['ip']}"
```
