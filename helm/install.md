{{indexmenu_n>30}}
## 安装应用

### 安装商店应用

按照前文helm工具已经安装完成，接下来通过helm客户端在kubernetes集群中创建一个应用，执行安装前最好先进行应用商店的同步，以获得最新的应用信息。

```
#更新商店信息
helm repo update
#查询tomcat应用
helm search tomcat
#安装商店应用
helm install stable/tomcat
```

执行了安装商店应用的命令后，我们看到了系统返回给我们了安装的详细信息，由于没有在安装命令中定义 --name 所以Helm随机生成了一个名字 giggly-leopard (此处每次创建都会随机生成)，其中Pod正在启动，LoadBalancer类型的Service正在获取EIP。
```
NAME:   giggly-leopard
……
RESOURCES:
==> v1/Pod(related)
NAME                                    READY  STATUS   RESTARTS  AGE
giggly-leopard-tomcat-6f46df7f86-59zhl  0/1    Pending  0         0s

==> v1/Service
NAME                   TYPE          CLUSTER-IP     EXTERNAL-IP  PORT(S)       AGE
giggly-leopard-tomcat  LoadBalancer  172.17.199.50  <pending>    80:31968/TCP  0s

==> v1beta2/Deployment
NAME                   READY  UP-TO-DATE  AVAILABLE  AGE
giggly-leopard-tomcat  0/1    0           0          0s
……
```
我们可以在稍后通过查看详情命令查看到Pod运行和EIP地址。
```
helm status giggly-leopard
```
```
LAST DEPLOYED: Wed Jun 26 21:09:53 2019
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Pod(related)
NAME                                    READY  STATUS   RESTARTS  AGE
giggly-leopard-tomcat-6f46df7f86-59zhl  1/1    Running  0         14h

==> v1/Service
NAME                   TYPE          CLUSTER-IP     EXTERNAL-IP      PORT(S)       AGE
giggly-leopard-tomcat  LoadBalancer  172.17.199.50  xxx.xxx.xxx.xxx  80:31968/TCP  14h

==> v1beta2/Deployment
NAME                   READY  UP-TO-DATE  AVAILABLE  AGE
giggly-leopard-tomcat  1/1    1           1          14h


NOTES:
1. Get the application URL by running these commands:
     NOTE: It may take a few minutes for the LoadBalancer IP to be available.
           You can watch the status of by running 'kubectl get svc -w giggly-leopard-tomcat'
  export SERVICE_IP=$(kubectl get svc --namespace default giggly-leopard-tomcat -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
  echo http://$SERVICE_IP:

```

可以在浏览器访问http://EIP/sample 查看到tomcat欢迎页面。
![](/images/helm/tomcat.png)