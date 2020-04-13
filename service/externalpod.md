# 通过EIP访问Pod

## 其它方式

UK8S支持使用ULB访问Service

* [通过内网ULB访问Service](uk8s/service/internalservice)
* [通过外网ULB访问Service](uk8s/service/externalservice)

## 直接使用EIP访问Pod

本文主要针对需要使用EIP直接绑定Pod提供服务的使用场景进行讲解，如需要外网的批处理任务等场景。

### 安装插件

为了在UK8S中实现Pod绑定EIP，需要额外部署支持EIP绑定的组件，直接在UK8S通过kubectl命令安装即可。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/service/cni-vpc-ipamd.yml
```

### Pod绑定EIP

完成插件安装后，我们就可以在创建Pod的时候增加EIP的绑定声明，如下所示。

```
apiVersion: v1
kind: Pod
metadata:
  name: podeip
  annotations:
    network.kubernetes.io/eip: "true"
    network.kubernetes.io/security-group-id: "firewall-rx3xsw24"
    network.kubernetes.io/eip-bandwidth: "6"
spec:
  containers:
  - name: http
    image: uhub.service.ucloud.cn/wxyz/helloworld:1.0
    imagePullPolicy: Always
    resources:
      limits:
        ucloud.cn/uni: 1
    ports:
    - containerPort: 8080
      protocol: TCP
```

我们将Pod信息保存为podeip.yaml，并执行`kubectl apply -f podeip.yaml`，执行完成Pod的EIP可以通过`kubectl describe pod podeip`查看annotations里的EIP的信息。

```
[root@10-19-22-90 ~]# kubectl describe po podeip 
Name:         podeip
Namespace:    default
Priority:     0
Node:         10.19.162.2/10.19.162.2
Start Time:   Mon, 13 Apr 2020 14:23:17 +0800
Labels:       <none>
Annotations:  kubectl.kubernetes.io/last-applied-configuration:
                {"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{"network.kubernetes.io/eip":"true","network.kubernetes.io/eip-bandwidth":"6","n...
              network.kubernetes.io/eip: true
              network.kubernetes.io/eip-addr: 117.50.135.126
              network.kubernetes.io/eip-bandwidth: 6
              network.kubernetes.io/security-group-id: firewall-rx3xsw24
              network.kubernetes.io/uni-id: uni-bhld3swq
Status:       Running
......
```

访问annotations里的EIP地址117.50.135.126，我们可以看到页面已经可以正常访问了。

![](/images/service/podeip.png)


#### 在这个例子里需要进行以下两个参数声明

* metadata.annotations
  
  声明是否需要EIP或者绑定已有EIP等信息，如例子所示，需要`network.kubernetes.io/eip: "true"`开启EIP，需要`network.kubernetes.io/security-group-id: "firewall-0j2ifbaf"`绑定防火墙(需要开相应的端口)，需要`network.kubernetes.io/eip-bandwidth: "6"`设定带宽。

* spec.containers[0].resources.limits

需要声明`ucloud.cn/uni: 1`，注意此步骤非常重要，对于pod来说有且只能有一个container声明此参数。


### Deployment控制Pod绑定EIP

Deployment控制与直接Pod绑定EIP类似，如下所示。

```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: podeip
  name: podeip
spec:
  replicas: 1
  selector:
    matchLabels:
      app: podeip
  template:
    metadata:
      labels:
        app: podeip
      annotations:
        network.kubernetes.io/eip: "true"
        network.kubernetes.io/security-group-id: "firewall-rx3xsw24"
        network.kubernetes.io/eip-bandwidth: "6"
    spec:
      containers:
      - name: http
        image: uhub.service.ucloud.cn/wxyz/helloworld:1.0
        imagePullPolicy: Always
        resources:
          limits:
            ucloud.cn/uni: 1
        ports:
        - containerPort: 8080
          protocol: TCP
```

#### 在Deployment中需要增加以下两个参数声明

* spec.template.metadata.annotations

  同Pod，声明是否需要EIP或者绑定已有EIP等信息。

* spec.template.spec.containers[0].resources.limits

  同Pod，需要声明`ucloud.cn/uni: 1`。



### Annotations详细参数

在使用Pod绑定EIP功能时，可以参考以下参数设定所需要绑定的EIP参数。

```
    "network.kubernetes.io/eip": ”true“ # 开启Pod绑定EIP，如不指定则新建一个EIP，Pod删除时一并删除
    "network.kubernetes.io/security-group-id": "firewall-xxdsad239d" #必填项，防火墙ID
    "network.kubernetes.io/eip-id": "eip-xsda8de" # 指定EIP，Pod删除时不会删除该EIP，且付款模式和带宽设置等都以原有EIP设置为准
    "network.kubernetes.io/eip-paymode": "sharebandwidth" # 付款模式，支持traffic、bandwidth、sharebandwidth，默认为bandwidth(带宽计费)
    "network.kubernetes.io/sharebandwidth-id": "bwshare-d8dklw" # 共享带宽id，paymode为sharebandwidth时需要传入
    "network.kubernetes.io/eip-bandwidth": "2"  # 共享带宽模式下无需指定，或者配置为0，bandwidth和traffic下默认为2Mbps
    "network.kubernetes.io/eip-chargetype": "month" # EIP付费模式，支持month，year，dynamic，默认为dynamic
    "network.kubernetes.io/eip-quantity": "1" # 付费时长，默认为1,dynamic下只默认且只能为1
```
