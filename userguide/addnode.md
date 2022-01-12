# 添加 Node 节点

单个集群的 Node 节点上限为 5000 个，在控制台页面一次最多可添加 50 个 Node 节点。 在集群详情页，节点列表页，点击**新增 Node 节点**，添加 Node 节点。

| 配置项      | 描述                                                                                                                                                                                            |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 所属子网     | 设置初始节点及 Pod 所处的子网，集群中 Node 可处于同一 VPC 下的不同子网                                                                                                                                                   |
| 类型       | Node 节点类型，支持 UHost 云主机（包括 GPU 云主机）、PHost 物理云主机及裸金属服务器                                                                                                                                         |
| 可用区      | Master/Node 节点所在可用区，在具有多个可用区的地域可以选择多可用区 UK8S 集群，建议在创建集群时将 Master 节点分布于多个可用区。                                                                                                                  |
| 节点镜像     | 设置集群节点的 UHost 镜像，您可以选择自定义镜像，但必须基于 UK8S 标准镜像制作，请参考[制作自定义镜像](uk8s/administercluster/custom_image)                                                                                               |
| 节点规格     | 包括机型、CPU 平台、CPU、内存、系统盘类型、数据盘类型、数据盘大小等配置，不同类型机型配置详见：[云主机 UHost](/uhost/introduction/uhost/type_new) / [GPU云主机](/gpu/README) / [物理云主机 UPHost](uphost/README) / [裸金属服务器](/uphost/type/baremetal) |
| 硬件隔离组    | Master 节点默认位于同一硬件隔离组，硬件隔离组能严格确保组内的每一台云主机都落在不同的物理机上。每个隔离组在单个可用区至多可以添加 7 台云主机，详见[硬件隔离组](uhost/guide/isolationgroup)                                                                             |
| 最大 Pod 数 | 单个 Node 节点可支持承载的最大 Pod 数量                                                                                                                                                                     |
| 标签       | Node 节点标签，详见 Kubernetes 官方文档：[标签和运算符](https://kubernetes.io/zh/docs/concepts/overview/working-with-objects/labels/)                                                                           |
| 污点       | Node 节点污点，详见 Kubernetes 官方文档：[污点和容忍度](https://kubernetes.io/zh/docs/concepts/scheduling-eviction/taint-and-toleration/)                                                                       |
| 禁用节点     | 开启禁用节点选项，节点将作为不可调度节点加入集群，可按需启用节点。                                                                                                                                                             |
| 自定义数据    | 是指主机初次启动或每次启动时，系统自动运行的配置脚本，该脚本可由控制台 API 等传入元数据服务器，并由主机内的 cloud-init 程序获取，脚本遵循标准 CloudInit 语法。该脚本会阻塞 UK8S 的安装脚本，即只有该脚本执行完毕后，才会开始K8S相关组件的安装，如Kubelet、Scheduler等。                                |
| 初始化脚本    | 该脚本只在 UK8S 启动后执行一次，且是在 K8S 相关组件安装成功后执行。遵循标准shell语法， 执行结果会存入到 `/var/log/message/` 目录下。                                                                                                         |
