# Pod 资源视图
Pod资源视图插件基于[Kubernetes Admission Webhook](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/)和[Lxcfs](https://github.com/lxc/lxcfs)，以获取Pod中CPU、内存等资源的实际占用情况。

默认情况下，在容器内执行top、free等命令时，由于读取的/proc文件系统并未与Pod所在节点隔离，因此显示的是节点自身资源信息，而非该容器被实际分配的资源信息。

## 基本原理
Lxcfs从容器的Cgroup中读取Pod实际资源信息，并将其映射到/var/lib/lxc/lxcfs目录下。通过将这些目录挂载到容器的/proc路径中，在容器内执行top、free等命令时，读取到的就是Cgroup分配的真实数据。Lxcfs目录挂载过程由Admission Webhook在Pod创建时自动完成。
详见[UK8S Lxcfs Github](https://github.com/ucloud/lxcfs-admission-webhook).

![pod-lxcfs-intro.png](/images/monitor/pod/pod-lxcfs-intro.png)

> 注意：
> - Pod资源视图只作用于新建的Pod
> - 出于安全和稳定考虑，该插件不对`kube-system`、`kube-public` Namespace生效 

## 安装Pod资源图
点击 插件管理 -> Pod资源视图 -> 开启。

![install.png](/images/monitor/pod/pod-lxcfs-install.png)

## 开始使用
1. 指定某些Namespace开启pod资源视图。开启后，Label `app.kubernetes.io/lxcfs: enable` 会被添加到选中的Namespace上。

![getting-started-1.png](/images/monitor/pod/pod-lxcfs-getting-started-a.png)

2. 创建Pod, 并为Pod指定limit资源限制

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: uhub.service.ucloud.cn/library/nginx:1.9.7
          resources:
            requests:
              cpu: "50"
              memory: "50Mi"
            limits:
              cpu: "100"
              memory: "100Mi"
          ports:
            - containerPort: 80
              name: http

```
3. 查看Pod的CPU, 内存信息
```shell
$ kubectl get pod
$ kubectl exec -it <your-pod> -- free -mh
        total       used       free     shared    buffers     cached
Mem:    100M       2.4M        97M         4K         0B        72K

$ kubectl exec -it <your-pod> -- top
```
