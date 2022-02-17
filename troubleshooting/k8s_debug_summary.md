# UK8S 集群常见问题

<!--* [UK8S 人工支持](#uk8s-人工支持)
* [为什么我的容器一起来就退出了？](#为什么我的容器一起来就退出了)
* [Docker 如何调整日志等级](#docker-如何调整日志等级)
* [为什么节点已经异常了，但是 Pod 还处在 Running 状态](#为什么节点已经异常了但是-pod-还处在-running-状态)
* [节点宕机了 Pod 一直卡在 Terminating 怎么办](#节点宕机了-pod-一直卡在-Terminating-怎么办)
* [Pod 异常退出了怎么办？](#pod-异常退出了怎么办)
* [CNI 插件升级为什么失败了？](#cni-插件升级为什么失败了)
* [UK8S 页面概览页一直刷新不出来？](#uk8s-页面概览页一直刷新不出来)
* [UK8S 节点 NotReady 了怎么办](#uk8s-节点-notready-了怎么办)
* [为什么我的集群连不上外网?](#为什么我的集群连不上外网)
* [为什么我的 UHub 登陆失败了?](#为什么我的-uhub-登陆失败了)
* [UHub 下载失败（慢）](#uhub-下载失败慢)
* [PV PVC StorageClass 以及 UDisk 的各种关系？](#pv-pvc-storageclass-以及-udisk-的各种关系)
  - [Statefulset 中使用 pvc](#statefulset-中使用-pvc)
* [VolumeAttachment 的作用](#volumeattachment-的作用)
* [如何查看 PVC 对应的 UDisk 实际挂载情况](#如何查看-pvc-对应的-udisk-实际挂载情况)
* [磁盘挂载的错误处理](#磁盘挂载的错误处理)
  - [PV 和 PVC 一直卡在 terminating/磁盘卸载失败怎么办](#pv-和-pvc-一直卡在-terminating磁盘卸载失败怎么办)
  - [Pod 的 PVC 一直挂载不上怎么办？](#pod-的-pvc-一直挂载不上怎么办)
* [UDisk-PVC 使用注意事项](#udisk-pvc-使用注意事项)
* [为什么在 K8S 节点 Docker 直接起容器网络不通](#为什么在-k8s-节点-docker-直接起容器网络不通)
* [使用 ULB4 时 Vserver 为什么会有健康检查失效](#使用-ulb4-时-vserver-为什么会有健康检查失效)
* [ULB4 对应的端口为什么不是 NodePort 的端口](#ulb4-对应的端口为什么不是-nodeport-的端口)-->

## 1. UK8S 完全兼容原生 Kubernetes API吗？

完全兼容。

## 2. UK8S 人工支持

对于使用 UK8S 遇到的本文档未涉及的问题，如果需要人工支持，请提供主机的 uhost-id，并添加公钥信任，将下面内容添加到ssh配置文件authorized_keys中。


```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDGIFVUtrp+jAnIu1fBvyLx/4L4GNsX+6v8RodxM+t3G7gCgaG+kHqs1xkLBWQNNMVQz2c/vA1gMNYASnvK/aQJmI9NxuOoaoqbL/yrZ58caJG82TrDKGgByvAYcT5yJkJqGRuLlF3XL1p2C0P8nxf2dzfjQgy5LGvZ1awEsIeoSdEuicaxFoxkxzTH/OM2WSLuJ+VbFg8Xl0j3F5kP9sT/no1Gau15zSHxQmjmpGJSjiTpjSBCm4sMaJQ0upruK8RuuLAzGwNw8qRXJ4qY7Tvg36lu39KHwZ22w/VZT1cNZq1mQXvsR54Piaix163YoXfS7jke6j8L6Nm2xtY4inqd uk8s-tech-support
```

## 3. UK8S对Node上发布的容器有限制吗？如何修改？

UK8S 为保障生产环境 Pod 的运行稳定，每个 Node 限制了 Pod 数量为 110 个，用户可以通过登陆 Node 节点"vim /etc/kubernetes/kubelet.conf"
修改 `maxpods:110`，然后执行 `systemctl restart kubelet` 重启 kubelet 即可。

## 4. 为什么我的容器一起来就退出了？

1. 查看容器log，排查异常重启的原因
2. pod是否正确设置了启动命令，启动命令可以在制作镜像时指定，也可以在pod配置中指定
3. 启动命令必须保持在前台运行，否则k8s会认为pod已经结束，并重启pod。

## 5. Docker 如何调整日志等级

1. 修改/etc/docker/daemon.json 文件，增加一行配置"debug": true
2. systemctl reload docker 加载配置，查看日志
3. 如果不再需要查看详细日志，删除debug配置，重新reload docker即可

## 6. 为什么节点已经异常了，但是 Pod 还处在 Running 状态

1. 这是由于k8s的状态保护造成的，在节点较少或异常节点很多的情况下很容易出现
2. 具体可以查看文档 https://kubernetes.io/zh/docs/concepts/architecture/nodes/#reliability

## 7. 节点宕机了 Pod 一直卡在 Terminating 怎么办

1. 节点宕机超过一定时间后（一般为 5 分钟），k8s 会尝试驱逐 pod，导致 pod 变为 Terminating 状态
2. 由于此时 kubelet 无法执行删除pod的一系列操作，pod 会一直卡在 Terminating
3. 类型为 daemonset 的 pod，默认在每个节点都有调度，因此 pod 宕机不需要考虑此种类型 pod，k8s 也默认不会驱逐该类型的 pod
4. 类型为 depolyment 和 replicaset 的 pod，当 pod 卡在 termanting 时，控制器会自动拉起对等数量的 pod
5. 类型为 statefulset 的 pod，当 pod 卡在 termanting 时，由于 statefulset 下属的 pod 名称固定，必须等上一个 pod 彻底删除，对应的新 pod
   才会被拉起，在节点宕机情况下无法自动拉起恢复
6. 对于使用 udisk-pvc 的 pod，由于 pvc 无法卸载，会导致新起的 pod 无法运行，请按照本文 pvc 相关内容(#如何查看pvc对应的udisk实际挂载情况)，确认相关关系

## 8. Pod 异常退出了怎么办？

1. `kubectl describe pods pod-name -n ns` 查看 pod 的相关 event 及每个 container 的 status，是 pod 自己退出，还是由于
   oom 被杀，或者是被驱逐
2. 如果是 pod 自己退出，`kubectl logs pod-name -p -n ns` 查看容器退出的日志，排查原因
3. 如果是由于 oom 被杀，建议根据业务重新调整 pod 的 request 和 limit 设置（两者不宜相差过大），或检查是否有内存泄漏
4. 如果 pod 被驱逐，说明节点压力过大，需要检查时哪个 pod 占用资源过多，并调整 request 和 limit 设置
5. 非 pod 自身原因导致的退出，需要执行`dmesg`查看系统日志以及`journalctl -u kubelet`查看 kubelet 相关日志。

## 9. CNI 插件升级为什么失败了？

1. 检查节点是否设置了污点及禁止调度（master 节点的默认污点不计算在内），带有污点的节点需要选择强制升级（不会对节点有特殊影响）。
2. 如果强制升级失败的，请重新点击 cni 强制升级。
3. 执行`kubectl get pods -n kube-system |grep plugin-operation`找到对应插件升级的 pod，并 describe pod 查看 pod
   失败原因。

## 10. UK8S 页面概览页一直刷新不出来？

1. api-server 对应的 ulb4 是否被删除（`uk8s-xxxxxx-master-ulb4`）
2. UK8S 集群的三台 master 主机是否被删了或者关机等
3. 登陆到 UK8S 三台 master 节点，检查 etcd 和 kube-apiserver 服务是否正常，如果异常，尝试重启服务

- 3.1 `systemctl status etcd`  / `systemctl restart etcd` 如果单个 etcd 重启失败，请尝试三台节点的 etcd 同时重启
- 3.2 `systemctl status kube-apiserver`  / `systemctl restart kube-apiserver`

## 11. UK8S 节点 NotReady 了怎么办

1. `kubectl describe node node-name` 查看节点 notReady 的原因，也可以直接在 console 页面上查看节点详情。
2. 如果可以登陆节点，`journalctl -u kubelet` 查看 kubelet 的日志， `system status kubelet`查看 kubelet 工作是否正常。
3. 对于节点已经登陆不了的情况，如果希望快速恢复可以在控制台找到对应主机断电重启。
4. 查看主机监控，或登陆主机执行`sar`命令，如果发现磁盘 cpu 和磁盘使用率突然上涨, 且内存使用率也高，一般情况下是内存 oom
   导致的。关于内存占用过高导致节点宕机，由于内存占用过高，磁盘缓存量很少，会导致磁盘读写频繁，进一步增加系统负载，打高cpu的恶性循环
5. 内存 oom 的情况需要客户自查是进程的内存情况，k8s 建议 request 和 limit 设置的值不宜相差过大，如果相差较大，比较容易导致节点宕机。
6. 如果对节点 notready 原因有疑问，请按照[UK8S人工支持](#uk8s-人工支持)联系人工支持

## 12. 为什么我的集群连不上外网?

UK8S 使用 VPC 网络实现内网互通，默认使用了 UCloud 的 DNS，wget 获取信息需要对 VPC 的子网配置网关，需要在 UK8S 所在的区域下进入VPC产品，对具体子网配置 NAT
网关，使集群节点可以通过 NAT 网关拉取外网数据，具体操作详见[VPC创建NAT网关](https://docs.ucloud.cn/vpc/briefguide/step4) 。

## 13. 为什么在 K8S 节点 Docker 直接起容器网络不通

1. UK8S 使用 UCloud 自己的 CNI 插件，而直接用 Docker 起的容器并不能使用该插件，因此网络不通。
2. 如果需要长期跑任务，不建议在 UK8S 节点用 Docker 直接起容器，应该使用 pod
3. 如果只是临时测试，可以添加`--network host` 参数，使用 hostnetwork 的模式起容器

## 14. 使用 ULB4 时 Vserver 为什么会有健康检查失效

1. 如果 svc 的 externalTrafficPolicy 为 Local 时，这种情况是正常的，失败的节点表示没有运行对应的 pod
2. 需要在节点上抓包 `tcpdump -i eth0 host <ulb-ip>` 查看是否正常, ulb-ip 替换为 svc 对应的实际 ip
3. 查看节点上 kube-proxy 服务是否正常 `systemctl status kube-proxy`
4. 执行`iptables -L -n -t nat |grep KUBE-SVC` 及 `ipvsadm -L -n`查看转发规则是否下发正常

## 15. ULB4 对应的端口为什么不是 NodePort 的端口

1. K8S 节点上对 ulb_ip+serviceport 的端口组合进行了 iptables 转发，所以不走 nodeport
2. 如果有兴趣，可以通过在节点上执行`iptables -L -n -t nat` 或者`ipvsadm -L -n` 查看对应规则 

## 16. 我想在删除LoadBalancer类型的Service并保留EIP该怎么操作？

修改 Service 类型，原 `type: LoadBalancer` 修改为 NodePort 或者 ClusterIP，再进行删除 Service 操作，EIP 和 ULB 会保留。

因该操作 EIP 和 ULB 资源将不再受 UK8S 管理，所以需要手动至 ULB 和 EIP 页面进行资源解绑和绑定。

## 17. Pod 的时区问题

在 Kubernetes 集群中运行的容器默认使用格林威治时间，而非宿主机时间。如果需要让容器时间与宿主机时间一致，可以使用 "hostPath" 的方式将宿主机上的时区文件挂载到容器中。

大部分linux发行版都通过 "/etc/localtime" 文件来配置时区，我们可以通过以下命令来获取时区信息：

```bash
# ls -l /etc/localtime
lrwxrwxrwx. 1 root root 32 Oct 15  2015 /etc/localtime -> ../usr/share/zoneinfo/Asia/Shanghai
```

通过上面的信息，我们可以知道宿主机所在的时区为Asia/Shanghai，下面是一个Pod的yaml范例，说明如何将容器内的时区配置更改为Asia/Shanghai，和宿主机保持一致。

```yaml
apiVersion: app/v1
kind: Pod
metadata:
 name: nginx
 labels:
   name: nginx
spec:
    containers:
    - name: nginx
      image: nginx
      imagePullPolicy: "IfNotPresent"
      resources:
        requests:
          cpu: 100m
          memory: 100Mi
      ports:
         - containerPort: 80
      volumeMounts:
      - name: timezone-config
        mountPath: /etc/localtime
    volumes:
      - name: timezone-config
        hostPath:
           path: /usr/share/zoneinfo/Asia/Shanghai
```

如果容器之前已经创建了，只需要在 yaml 文件中加上 `volumeMounts` 及 `volumes` 参数，再使用 `kubectl apply` 命令更新即可。
