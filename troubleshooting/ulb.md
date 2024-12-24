# ULB 相关常见问题处理

## 1. 如何区别使用ULB4还是ULB7？

通过service.metadata.annotations中的service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol值来声明使用ULB4还是ULB7。

如果值为tcp或者udp则使用ULB4。

如果是http或者https，则使用ULB7。

## 2. 如何区别ULB7是不是ALB

通过查看service.metadata.annotations中service.beta.kubernetes.io/ucloud-load-balancer-listentype是否为application来确定是alb，或者在service上找到对应LB对应的ID，查看是否在控制台上LB产品页面的应用型负载均衡页面内。

## 3. 使用 ULB4 时 Vserver 为什么会有健康检查失效

1. 如果 svc 的 externalTrafficPolicy 为 Local 时，这种情况是正常的，失败的节点表示没有运行对应的 pod
2. 需要在节点上抓包 `tcpdump -i eth0 host <ulb-ip>` 查看是否正常, ulb-ip 替换为 svc 对应的实际 ip
3. 查看节点上 kube-proxy 服务是否正常 `systemctl status kube-proxy`
4. 执行`iptables -L -n -t nat |grep KUBE-SVC` 及 `ipvsadm -L -n`查看转发规则是否下发正常

## 4. ULB4 对应的端口为什么不是 NodePort 的端口

1. K8S 节点上对 ulb_ip+serviceport 的端口组合进行了 iptables 转发，所以不走 nodeport
2. 如果有兴趣，可以通过在节点上执行`iptables -L -n -t nat` 或者`ipvsadm -L -n` 查看对应规则 

## 5. 我想在删除LoadBalancer类型的Service并保留EIP该怎么操作？

修改 Service 类型，原 `type: LoadBalancer` 修改为 NodePort 或者 ClusterIP，再进行删除 Service 操作，EIP 和 ULB 会保留。

因该操作 EIP 和 ULB 资源将不再受 UK8S 管理，所以需要手动至 ULB 和 EIP 页面进行资源解绑和绑定。

## 6. 更改报文转发ULB的EIP之后在uk8s不生效

如果uk8s中某个Service绑定了报文转发类型的ULB，而用户手动更改了ULB的EIP，会发现无法通过新的EIP来访问Service。

这是因为cloudprovider组件无法监听到ULB的变动，没有触发对账流程将新的EIP写入iptables以实现转发。

如果您遇到该问题，可以在修改EIP之后使用下面的命令重启cloudprovider以强制触发对账流程：

```bash
kubectl -n kube-system rollout restart deploy cloudprovider-ucloud
```

注意，在重启之后，可能需要2分钟左右的时间生效。

## 7. Service换绑后原ULB无法重新绑定

当Service换绑ULB之后，原来的ULB会有vserver残留，这时候别的Service绑定原来ULB会报类似如下的错误：

```
Error syncing load balancer: failed to ensure load balancer: vserver(s) have already been created for one or more ports
```

如果遇到，需要手动将原来ULB中的vserver清理掉。

## 8. 如何手动更改Service绑定ULB的EIP

1. 在控制台的ULB管理页面，手动变更对应ULB的EIP。
2. 在Service中，增加`service.beta.kubernetes.io/ucloud-load-balancer-id`字段，设置为对应的ULB ID。
3. 等待一段时间，观察Serivce中的EIP相关Annotation是否更新。


## 9. 一个LoadBalancer的Service是否支持多端口？

支持，UK8S会为service.spec.ports下每个ServicePort分别创建一个VServer，VServer端口为Service端口。

## 10. 是否支持多协议？

目前UK8S CloudProvider 插件版本 >= 19.05.3 同时支持HTTP和HTTPS协议，cloudprovider 插件版本 >= 24.03.5 也支持UDP和TCP协议混用。

## 11. 如果Loadbalancer创建外网ULB后，用户在ULB控制台页面绑定了新的EIP，会被删除吗？

只有访问SVC的ExternalIP才能把流量导入后端Pod，访问其他EIP无效。删除SVC时，所有EIP都会被删除。

## 12. ULB配置迁移怎么操作？

因配置迁移实际为监听器迁移，故针对所有用到该ULB监听器的Service资源，需新建一个[使用已有ALB](https://docs.ucloud.cn/uk8s/service/ulb_designation?id=%e4%bd%bf%e7%94%a8%e5%b7%b2%e6%9c%89alb)的Service

将`service.beta.kubernetes.io/ucloud-load-balancer-id-provision`改为`service.beta.kubernetes.io/ucloud-load-balancer-id`值为迁移后的albid，新增`service.beta.kubernetes.io/ucloud-load-balancer-listentype`值为`application`

* 如果监听器为https协议则需额外配置ssl参数`service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol`、`service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert`与`service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port`

以下样例展示了ulb配置迁移了一个带有80，443，8443端口监听器的ulb，其中80为http，443以及8443为https，原有Service如下：

```yaml
# 迁移前的Service
apiVersion: v1
kind: Service
metadata:
  annotations:
    # 迁移前的ulbid
    service.beta.kubernetes.io/ucloud-load-balancer-id-provision: ulb-xxx 
    service.beta.kubernetes.io/ucloud-load-balancer-paymode: month
    service.beta.kubernetes.io/ucloud-load-balancer-type: inner
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol: https
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert: ssl-xxx
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port: 443,8443
  name: service1
  namespace: default
spec:
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: 80
  - name: ssl
    port: 8443
    protocol: TCP
    targetPort: 80
  - name: http
    port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: service1
  type: LoadBalancer
```

对80以及443端口进行ulb配置迁移后新建的Service如下：

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    # 迁移后的albid
    service.beta.kubernetes.io/ucloud-load-balancer-id: alb-xxx
    # “application”表示使用应用型负载均衡ALB
    service.beta.kubernetes.io/ucloud-load-balancer-listentype: "application"
    service.beta.kubernetes.io/ucloud-load-balancer-paymode: month
    service.beta.kubernetes.io/ucloud-load-balancer-type: inner
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-protocol: https
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-cert: ssl-xxx
    service.beta.kubernetes.io/ucloud-load-balancer-vserver-ssl-port: 443
  name: service2
  namespace: default
spec:
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 80
  - name: https
    port: 443
    protocol: TCP
    targetPort: 80
  selector:
    app: service2
  type: LoadBalancer
```

创建Service资源后同时建议业务侧将原先Servive的服务流量进行切换到该新建Service上。