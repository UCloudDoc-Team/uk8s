{{indexmenu_n>2}}

## 容器常见问题

### Pod的时区问题

在Kubernetes集群中运行的容器默认使用格林威治时间，而非宿主机时间。如果需要让容器时间与宿主机时间一致，可以使用`hostPath`的方式将宿主机上的时区文件挂载到容器中。

大部分linux发行版都通过`/etc/localtime`文件来配置时区，我们可以通过以下命令来获取时区信息：

```
# ls -l /etc/localtime
lrwxrwxrwx. 1 root root 32 Oct 15  2015 /etc/localtime -> ../usr/share/zoneinfo/Asia/ShangHai
```

通过上面的信息，我们可以知道宿主机所在的时区为Asia/ShangHai，下面是一个Pod的yaml范例，说明如何将容器内的时区配置更改为Asia/ShangHai，和宿主机保持一致。

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
           path: /usr/share/zoneinfo/Asia/ShangHai
```
如果容器之前已经创建了，只需要在yaml文件中加上`volumeMounts`及`volumes`参数，再使用**kubectl apply **命令更新即可。

### 一个PVC可以挂载到多个pod吗？
UDisk不支持多点读写，如需要多点读写请使用UFS。

### 我想在删除LoadBalancer类型的Service并保留EIP该怎么操作？

修改Service类型，原`type: LoadBalancer`修改为NodePort或者ClusterIP，再进行删除Service操作，EIP和ULB会保留。

因该操作EIP和ULB资源将不再受UK8S管理，所以需要手动至ULB和EIP页面进行资源解绑和绑定。

### 怎么在UK8S集群中拉取Uhub以外的镜像？

UK8S使用VPC网络实现内网互通，拉取Uhub镜像不受影响，拉取外网镜像时需要对VPC的子网配置网关，需要在UK8S所在的区域下进入VPC产品，对具体子网配置NAT网关，使集群节点可以通过NAT网关拉取外网镜像，具体操作详见[VPC创建NAT网关](/network/vpc/briefguide/step4)
。

### Pod删除后，如何复用原先的云盘？

可以使用静态创建PV的方法进行原有云盘绑定的方法进行复用原有云盘，详见[在UK8S中使用已有UDISK]((/compute/uk8s/volume/statusudisk)
)