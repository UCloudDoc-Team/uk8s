# 使用须知

## 1. 集群

1. 使用 UK8S 服务，必须通过 UCloud 实名认证服务；
2. 集群中 master 节点为管理节点，不建议服务调度到 master 节点运行；
3. 单个 UK8S 集群最多添加 5000 个 Node 节点，生产集群建议不超过 1000 个；
4. 支持的 Kubernetes 版本会落后社区 2 个版本，具体以产品页面为准；
5. 如果云账户开启了 [API 白名单](https://console.ucloud.cn/uaccount/userinfo)，请在控制台**账号安全**页面**访问限制**栏中，将
   10.10.10.10/32 网段加入允许 API 访问的列表。

## 2. 节点

1. Node 节点使用的云主机镜像默认为 Centos7.6，如果重装系统或擅自修改系统配置，可能导致集群不可用；
2. Node 节点使用的云主机系统盘默认为 SSD，支持添加数据盘，添加数据盘后，容器启动后默认运行在数据盘；
3. 云主机默认使用 N 机型，您也可以选择其他机型（如 O 型、C 型）；
4. 节点标签**UhostID=xxx**为主机管理使用标签，请勿删除修改，以免导致集群数据不正常；

## 3. 存储卷

#### 支持类型
当前支持 SATA、SSD UDisk 以及 UFS 和 UFile；

   [在 UK8S 中使用 UDisk](uk8s/volume/udisk)

   [在 UK8S 中使用 UFS](uk8s/volume/ufs)

   [在 UK8S 中使用 UFile](uk8s/volume/ufile)

#### 支持地域

请参考[存储相关文档说明](uk8s/volume/intro?id=uk8s支持存储挂载的地域)


## 4. 资源命名规范

当你创建 UK8S 集群后，UK8S 会以你的名义在当前项目下创建 UHost、ULB、UDisk、EIP 等资源，更改配置或删除可能导致集群不可用，请谨慎操作。涉及的资源主要如下：

#### 1. 由 UK8S 管理服务创建的资源，其命名规范如下：

* `uk8s-xxxxxxxx-master-m` 为 Master 节点的名称，作为集群的 Master 节点；
* `uk8s-xxxxxxxx-n-xxxxx` 为 Node 节点的名称，作为集群的 Node 节点；
* `uk8s-xxxxxxxx-master-ulb4` 为集群 ApiServer 内网 ULB 名次，作为集群内部入口；
* `uk8s-xxxxxxxx-master-ulb4-external` 为 ApiServer 外网 ULB 名称，作为集群外部入口；
* `system_udisk_uk8s-xxxxxxxx-n-xxxxx` 为 UDisk 资源名称，作为集群节点的系统盘；
* `data_udisk_uk8s-xxxxxxxx-n-xxxxx` 为 UDisk 资源名称，作为集群节点的数据盘。

#### 2. 由 UK8S 插件创建的资源，其命名规范如下：

* `ingress-nginx.ingress.svc.uk8s-xxxx` 是 ULB 资源名称，由 UK8S 的 ULB 插件创建，用于 LoadBalancer 类型的Service，且其备注为 UID-xx-xxx，实为 Service 在 UK8S 中的 uuid。其命名规范为 `svc-name.namespace.svc.uk8s-id`。

* `TCP_443_xxx-xxxxx` 为 Vserver 名称，由 UK8S 的 ULB 插件创建，对应 LoadBalancer 类型的 Service 中不同的端口。其命名规范为 `service-protocol_service-port_service_uuid`。

* `pvc-9393f66f-c0b5-11e9-bd6d-5254001935f2` 为 UDisk 名称，由 UK8S 的存储插件创建，对应 UK8S 中的 PVC。其命名规范为
`pvc-pvc_uuid`。
