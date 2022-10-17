# 在节点宕机时恢复挂载了云盘的Pod

> 警告：节点宕机后，在卸载云盘时无法到节点上面进行unmount操作，因此无法安全地卸载云盘。下面的文档涉及对云盘的强制解绑，这种操作可能会造成数据丢失。如果无法接受这种风险，切勿进行本文档的操作（此时应该尝试恢复节点）。
>
> 如果磁盘数据容忍丢失（例如储存日志数据），并且希望Pod尽快恢复，可以参考本文档的操作。

节点宕机之后，如果Pod挂载了云盘，是无法被自动恢复的。因为Kubernetes无法确定节点是真正宕机了还是因为网络问题暂时失联，所以云盘此时还有可能存在数据写入。如果此时贸然进行Pod迁移可能会破坏云盘。

如果是正常的Pod，在经过容忍时间之后，会自动进行驱逐，详见我们的另外一篇文档：[Pod 容忍节点异常时间调整](/uk8s/bestpractice/taint_base_eviction)。

如果您确定节点宕机了，并且想要恢复宕机节点上面挂载了云盘的Pod，请参考本文档进行操作。

## 场景复现

下面我们创建一个3节点的集群：

```shell
$ kubectl get node
NAME           STATUS                     ROLES    AGE     VERSION
10.9.133.163   Ready,SchedulingDisabled   master   4m26s   v1.22.5
10.9.138.243   Ready                      <none>   4m16s   v1.22.5
10.9.187.33    Ready,SchedulingDisabled   master   4m41s   v1.22.5
10.9.188.56    Ready                      <none>   3m58s   v1.22.5
10.9.32.154    Ready,SchedulingDisabled   master   4m43s   v1.22.5
10.9.61.217    Ready                      <none>   3m49s   v1.22.5
```

在里面创建一个`StatefulSet`，启动6个pod，它们都挂载了`ssd`云盘：

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: test-web-ssd
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 6
  serviceName: "test-nginx-ssd"
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: uhub.service.ucloud.cn/ucloud/nginx:latest
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: test-nginx-ssd
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: test-nginx-ssd
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "ssd-csi-udisk"
      resources:
        requests:
          storage: 1Gi
```

在控制台界面，手动将一个云主机进行断电操作，以模拟宕机的场景：

![](/uk8s/images/troubleshooting/power_off_uhost.png)

过了一会，会发现该节点处于`NotReady`状态，Pod卡在了`Terminating`，而`StatefulSet`控制器不会为它们启动新的副本或进行云盘卸载等操作：

```shell
$ kubectl get node 10.9.188.56
NAME          STATUS     ROLES    AGE   VERSION
10.9.188.56   NotReady   <none>   12m   v1.22.5
```

```shell
$ kubectl get po -o wide | grep '10.9.188.56'
test-web-ssd-3   1/1     Terminating   0          9m52s   10.9.48.46     10.9.188.56    <none>           <none>
```

## 修复Pod

如果该节点短时间内无法恢复，我们应该考虑恢复中断的Pod以确保业务的正常运行。

首先，在确认节点宕机后，到控制台界面对异常节点上面的云盘进行手动卸载的操作：

> 警告：这一步可能造成云盘部分数据的丢失，请确认可以接受风险再进行操作，如果无法容忍数据的丢失，切勿进行操作。

![](/uk8s/images/troubleshooting/unmount_udisk.png)

随后，在Kubernetes中，将异常的node资源删除掉，这样才能释放异常的Pod并进行重建：

```shell
$ kubectl delete node 10.9.188.56
node "10.9.188.56" deleted
```

而此时调度器并不知道云盘已经卸载，，我们还需要手动删除对应的`volumeattachment`资源：

```shell
$ kubectl get volumeattachment | grep '10.9.188.56'
csi-53bbdc72c17cc6ecc7c87b2b9b6526679175e53f0b88b52384f9773c0abbcded   udisk.csi.ucloud.cn   pvc-f6aa7b36-6d44-4521-ba8a-0086fd979e70   10.9.188.56    true       13m
```

```shell
$ kubectl delete volumeattachment csi-53bbdc72c17cc6ecc7c87b2b9b6526679175e53f0b88b52384f9773c0abbcded
volumeattachment.storage.k8s.io "csi-53bbdc72c17cc6ecc7c87b2b9b6526679175e53f0b88b52384f9773c0abbcded" deleted
```

等待Pod重建，重建后会复用原来的云盘：

```shell
$ kubectl get po test-web-ssd-3
NAME             READY   STATUS    RESTARTS   AGE
test-web-ssd-3   1/1     Running   0          103s
```



