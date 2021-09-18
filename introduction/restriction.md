# 使用须知


## 1. 集群

1. 使用UK8S服务，必须通过UCloud实名认证服务；
2. 集群中master节点为管理节点，不建议服务调度到管理集群运行；
3. 单个UK8S集群最多添加5000个Node节点，生产集群建议不超过1000个；
4. 支持的Kubernetes版本会落后社区2个版本，具体以产品页面为准；
5. 如果的云账户开启了[API白名单](https://console.ucloud.cn/uaccount/userinfo)，请在控制台**账号安全**页面**访问限制**栏中，将 10.10.10.10/32 网段将入允许 API 访问的列表。

## 2. 节点

1. Node节点使用的云主机镜像默认为 Centos7.6，如果重装系统或擅自修改系统配置，可能导致集群不可用；
2. Node节点使用的云主机系统盘默认为SSD，支持添加数据盘，添加数据盘后，容器启动后默认运行在数据盘；
3. 云主机默认使用N机型，您也可以选择其他机型（如O型、C型)；
4. 节点标签**UhostID=xxx**为主机管理使用标签，请勿删除修改，以免导致集群数据不正常；

## 3. 存储卷

1. 当前支持SATA、SSD UDisk以及UFS；

    [在UK8S中使用UDisk](uk8s/volume/udisk)

    [在UK8S中使用UFS](uk8s/volume/ufs)

    [在UK8S中使用UFile](uk8s/volume/ufile)

2. 当前支持共享存储的地域：

|产品|地域|
|--|--|
|UDisk|北京、上海、广州、台北、东京、首尔、曼谷、新加坡、雅加达、胡志明、洛杉矶、华盛顿|
|UFS|北京、上海、广州|

## 4. 其他

当你创建UK8S集群后，UK8S会以你的名义在当前项目下创建UHost、ULB、UDisk、EIP等资源，更改配置或删除可能导致集群不可用，请谨慎操作。主要如下：

#### 1. 由UK8S管理服务创建的资源，其命名规范如下：

1.1 uk8s-xxxxxxxx-master-m 或 uk8s-xxxxxxxx-n-xxxxx 为 Master / Node 节点的名称，名称，作为集群的Master节点；

1.2 uk8s-xxxxxxxx-master-ulb4 / uk8s-xxxxxxxx-master-ulb4-external 为内外网 ULB 名称，作为 ApiServer 的内外网入口；

1.3 system_udisk_uk8s-xxxxxxxx-n-xxxxx / data_udisk_uk8s-xxxxxxxx-n-xxxxx 为 UDisk 名称，作为集群节点的系统盘 / 数据盘。

#### 2. 由UK8S插件创建的资源，其命名规范如下：

2.1 ULB名称为ingress-nginx.ingress.svc.uk8s-xy7udsa的，由UK8S的ULB插件创建，用于LoadBalancer类型的Service，且其备注为UID-xx-xxx，实为Service在UK8S中的uuid。其命名规范为svc-name.namespace.svc.uk8s-id。

2.2 Vserver名称为TCP_443_xxx-xxxxx的，由UK8S的ULB插件创建，对应LoadBalancer类型的Service中不同的端口。其命名规范为service-protocol_service-port_service_uuid。

2.3 UDisk名称为pvc-9393f66f-c0b5-11e9-bd6d-5254001935f2的，由UK8S的存储插件创建，对应UK8S中的PVC。其命名规范为pvc-pvc_uuid。

