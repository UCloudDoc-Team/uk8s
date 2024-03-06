# Pod 常见故障处理

在Kubernetes中发布应用时，我们经常会遇到Pod出现异常的情况，如Pod长时间处于Pending状态，或者反复重启，下面介绍下Pod 的各种异常状态及处理思路。

## 1. 常见错误

| 状态                    | 状态说明                  | 处理办法                                      |
| --------------------- | --------------------- | ----------------------------------------- |
| Error                 | Pod 启动过程中发生错误。        | 一般是由于容器启动命令、参数配置错误所致，请联系镜像制作者             |
| NodeLost              | Pod 所在节点失联。           | 检查 Pod 所在节点的状态                            |
| Unkown                | Pod 所在节点失联或其他未知异常。    | 检查 Pod 所在节点的状态                            |
| Pending               | Pod 等待被调度。            | 资源不足等原因导致，通过 kubectl describe 命令查看 Pod 事件 |
| Terminating           | Pod 正在被销毁。            | 可增加 --fore参数强制删除                          |
| CrashLoopBackOff      | 容器退出，Kubelet 正在将它重启。  | 一般是由于容器启动命令、参数配置错误所致                      |
| ErrImageNeverPull     | 策略禁止拉取镜像。             | 拉取镜像失败，确认imagePullSecret是否正确              |
| ImagePullBackOff      | 正在重试拉取。               | 镜像仓库与集群的网络连通性问题                           |
| RegistryUnavailable   | 连接不到镜像仓库。             | 联系仓库管理员                                   |
| ErrImagePull          | 拉取镜像出错。               | 联系仓库管理员，或确认镜像名是否正确                        |
| RunContainerError     | 启动容器失败。               | 容器参数配置异常                                  |
| PostStartHookError    | 执行 postStart hook 报错。 | postStart 命令有误                            |
| NetworkPluginNotReady | 网络插件还没有完全启动。          | cni 插件异常，可检查cni状态                         |

## 2. 常见命令

当我们发现 Pod 处于 上述状态时，可以使用以下命令来快速定位问题：

1. 获取 Pod 状态

```bash
kubectl -n ${NAMESPACE} get pod  -o wide
```

2. 查看 Pod 的 yaml 配置

```bash
kubectl -n ${NAMESPACE} get pod ${POD_NAME}  -o yaml
```

3. 查看 Pod 事件

```bash
kubectl  -n ${NAMESPACE} describe pod ${POD_NAME}
```

4. 查看 Pod 日志

```bash
kubectl  -n ${NAMESPACE} logs ${POD_NAME} ${CONTAINER_NAME}
```

5. 登录 Pod

```bash
kubectl -n ${NAMESPACE} exec -it  ${POD_NAME} /bin/bash
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

## 9. 为什么在 K8S 节点 Docker 直接起容器网络不通

1. UK8S 使用 UCloud 自己的 CNI 插件，而直接用 Docker 起的容器并不能使用该插件，因此网络不通。
2. 如果需要长期跑任务，不建议在 UK8S 节点用 Docker 直接起容器，应该使用 pod
3. 如果只是临时测试，可以添加`--network host` 参数，使用 hostnetwork 的模式起容器

## 10. Pod的时区问题

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