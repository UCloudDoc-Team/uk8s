{{indexmenu_n>0}}
## 使用须知


### 集群

1. 使用UK8S服务，必须通过UCloud实名认证服务；
2. 默认情况下，你最多可以在单个地域下创建5个UK8S集群（必须分属于不同子网下）；
3. 一个子网下，有且只能创建一个UK8S集群；
4. 单个UK8S集群最多添加5000个Node节点，生产集群建议不超过1000个；
5. 当前支持的Kubernetes版本为1.12.9及1.13.5，后续还将支持更多版本，具体以产品页面为准。
6. 如果的云账户开启了[API白名单](https://console.ucloud.cn/uapi/apikey),则需要在白名单中配置10.10.10.10/32网段，详见[API白名单配置](../q/cluster)

### 节点

1. Node节点使用的云主机镜像默认为 Centos7.6，如果重装系统或擅自修改系统配置，可能导致集群不可用；
2. Node节点使用的云主机系统盘默认为SSD，支持添加数据盘，添加数据盘后，容器启动后默认运行在数据盘；
3. 云主机默认使用N2机型，如所在机房N2售罄，则使用N1机型；
4. 不支持将已有云主机加入集群；
5. 节点标签**UhostID=xxx**为主机管理使用标签，请勿删除修改，以免导致集群数据不正常；

### 存储卷

1. 当前支持SATA、SSD UDisk以及UFS；

    [在UK8S中使用UDisk](../volume/udisk)

    [在UK8S中使用UFS](../volume/ufs)

2. 当前支持共享存储的地域：

|产品|地域|
|:-:|:-|
|UDisk|北京、上海、广州、台北、东京、首尔、曼谷、新加坡、雅加达、胡志明、洛杉矶、华盛顿|
|UFS|北京、上海、广州|


> 不支持共享存储地域，可使用emptyDir和hostPath进行挂载。


### 其他

当你创建UK8S集群后，UK8S会以你的名义在当前项目下创建UHost、ULB、UDisk、EIP等资源，更改配置或删除可能导致集群不可用，请谨慎操作。主要如下：

#### 1、由UK8S管理服务创建的资源，其命名规范如下：

1.1、 uk8s-trd3u-master-3或uk8s-trd3u-m-xsdaf为UHost名称，作为集群的Master节点；

1.2、 uk8s-trd3u-node-3或uk8s-trd3u-n-xsa2f为UHost名称，作为集群的Node节点；

1.3、 uk8s-trd3u-master-ulb为ULB名称，作为ApiServer的内网入口；

1.4、 uk8s-trd3u-master-ulb-external为ULB名称，作为ApiServer的外网入口；

1.5、 数据盘_uk8s-sr0xsohz-node-6或数据盘_uk8s-sr0xsohz-n-xsa2f为UDisk名称，作为集群的Node节点数据盘；

1.6、 系统盘_uk8s-sr0xsohz-node-6或系统盘_uk8s-sr0xsohz-n-xsa2f为UDisk名称，作为集群的Node节点系统盘；

#### 2、由UK8S插件创建的资源，其命名规范如下：

2.1、 ULB名称为ingress-nginx.ingress.svc.uk8s-xy7udsa的，由UK8S的ULB插件创建，用于LoadBalancer类型的Service，且其备注为UID-xx-xxx，实为Service在UK8S中的uuid。其命名规范为<svc-name>.<namespace>.svc.<uk8s-id>。

2.2、 Vserver名称为TCP_443_xxx-xxxxx的，由UK8S的ULB插件创建，对应LoadBalancer类型的Service中不同的端口。其命名规范为<service-protocol>_<service-port>_<service_uuid>。

2.3、 UDisk名称为pvc-9393f66f-c0b5-11e9-bd6d-5254001935f2的，由UK8S的存储插件创建，对应UK8S中的PVC。其命名规范为pvc-<pvc_uuid>。

