# 集群常见问题


## 1. 集群详情页提示ApiServer自签https证书过期
![](/images/troubleshooting/apiserver证书过期提示.png)

### 过期的是什么证书
`apiserver-loopback-client` 证书, 用于 `kube-scheduler`、`kube-controller-manager` 等管理组件和 `kube-apiserver` 之间的同节点通信。

### 证书过期有什么影响
影响管理组件之间的通信，可能会无法正常创建Pod。

### 如何查看证书
`apiserver-loopback-client` 存放于 `kube-apiserver` 的内存中，在服务启动时自动生成，没有写入到文件中。查看证书的方法如下:

登录**master节点**执行

```
curl --resolve apiserver-loopback-client:6443:127.0.0.1 -k -v https://apiserver-loopback-client:6443 2>&1| grep -i  'server certificate' -A5
```

### 如何解决

逐一登录master节点，重启`kube-apiserver`服务(`systemctl restart kube-apiserver`)，重启不会影响线上业务，需注意点：
1. 重启期间不能有业务发布变更等操作
2. 逐一执行重启，不可两台及以上master同时重启。

> 托管版UK8S用户无法自行重启apiserver, 请联系UK8S团队
