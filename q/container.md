

## 容器常见问题

### Pod的时区问题

在Kubernetes集群中运行的容器默认使用格林威治时间，而非宿主机时间。如果需要让容器时间与宿主机时间一致，可以使用"hostPath"的方式将宿主机上的时区文件挂载到容器中。

大部分linux发行版都通过"/etc/localtime"文件来配置时区，我们可以通过以下命令来获取时区信息：

```
# ls -l /etc/localtime
lrwxrwxrwx. 1 root root 32 Oct 15  2015 /etc/localtime -> ../usr/share/zoneinfo/Asia/Shanghai
```

通过上面的信息，我们可以知道宿主机所在的时区为Asia/Shanghai，下面是一个Pod的yaml范例，说明如何将容器内的时区配置更改为Asia/Shanghai，和宿主机保持一致。

```
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
如果容器之前已经创建了，只需要在yaml文件中加上“volumeMounts"及"volumes"参数，再使用**kubectl apply **命令更新即可。

### 我想在删除LoadBalancer类型的Service并保留EIP该怎么操作？

修改Service类型，原“type: LoadBalancer”修改为NodePort或者ClusterIP，再进行删除Service操作，EIP和ULB会保留。

因该操作EIP和ULB资源将不再受UK8S管理，所以需要手动至ULB和EIP页面进行资源解绑和绑定。