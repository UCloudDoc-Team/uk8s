# ULB 相关常见问题处理

## 1. 使用 ULB4 时 Vserver 为什么会有健康检查失效

1. 如果 svc 的 externalTrafficPolicy 为 Local 时，这种情况是正常的，失败的节点表示没有运行对应的 pod
2. 需要在节点上抓包 `tcpdump -i eth0 host <ulb-ip>` 查看是否正常, ulb-ip 替换为 svc 对应的实际 ip
3. 查看节点上 kube-proxy 服务是否正常 `systemctl status kube-proxy`
4. 执行`iptables -L -n -t nat |grep KUBE-SVC` 及 `ipvsadm -L -n`查看转发规则是否下发正常

## 2. ULB4 对应的端口为什么不是 NodePort 的端口

1. K8S 节点上对 ulb_ip+serviceport 的端口组合进行了 iptables 转发，所以不走 nodeport
2. 如果有兴趣，可以通过在节点上执行`iptables -L -n -t nat` 或者`ipvsadm -L -n` 查看对应规则 

## 3. 我想在删除LoadBalancer类型的Service并保留EIP该怎么操作？

修改 Service 类型，原 `type: LoadBalancer` 修改为 NodePort 或者 ClusterIP，再进行删除 Service 操作，EIP 和 ULB 会保留。

因该操作 EIP 和 ULB 资源将不再受 UK8S 管理，所以需要手动至 ULB 和 EIP 页面进行资源解绑和绑定。

## 4. 更改报文转发ULB的EIP之后在uk8s不生效

如果uk8s中某个Service绑定了报文转发类型的ULB，而用户手动更改了ULB的EIP，会发现无法通过新的EIP来访问Service。

这是因为cloudprovider组件无法监听到ULB的变动，没有触发对账流程将新的EIP写入iptables以实现转发。

如果您遇到该问题，可以在修改EIP之后使用下面的命令重启cloudprovider以强制触发对账流程：

```bash
kubectl -n kube-system rollout restart deploy cloudprovider-ucloud
```

注意，在重启之后，可能需要2分钟左右的时间生效。

## 5. Service换绑后原ULB无法重新绑定

当Service换绑ULB之后，原来的ULB会有vserver残留，这时候别的Service绑定原来ULB会报类似如下的错误：

```
Error syncing load balancer: failed to ensure load balancer: vserver(s) have already been created for one or more ports
```

如果遇到，需要手动将原来ULB中的vserver清理掉。