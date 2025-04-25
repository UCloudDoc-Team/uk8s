# 添加 Node 节点

单个集群的 Node 节点上限为 5000 个，在控制台页面一次最多可添加 50 个 Node 节点。 在集群详情页，节点列表页，点击**新增 Node 节点**，添加 Node 节点。

或者进入 **节点池** 页面，选择一个节点池，点击 **增加节点** 按钮在节点池增加节点

| 配置项      | 描述                                                                                                                                                                                            |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 所属子网     | 设置初始节点及 Pod 所处的子网，集群中 Node 可处于同一 VPC 下的不同子网                                                                                                                                                   |
| 类型       | Node 节点类型，支持 UHost 云主机（包括 GPU 云主机）                                                                                                                                         |
| 可用区      | Master/Node 节点所在可用区，在具有多个可用区的地域可以选择多可用区 UK8S 集群，建议在创建集群时将 Master 节点分布于多个可用区。                                                                                                                  |
| 节点镜像     | 设置集群节点的 UHost 镜像，您可以选择自定义镜像，但必须基于 UK8S 标准镜像制作，请参考[制作自定义镜像](uk8s/administercluster/custom_image) <br> 若您要使用GPU节点，镜像选择参考[GPU节点中的镜像说明](/uk8s/administercluster/gpu-node)，CPU机器镜像可选择：`Centos 7.6`,`Ubuntu 20.04`,`Anolis 8.6`镜像中的任意一种。                                                                                               |
| 节点规格     | 包括机型、CPU 平台、CPU、内存、系统盘类型、数据盘类型、数据盘大小等配置，不同类型机型配置详见：[云主机 UHost](/uhost/introduction/uhost/type_new) / [GPU云主机](/gpu/README) / [物理云主机 UPHost](uphost/README) / [裸金属服务器](/uphost/type/baremetal) |
| 硬件隔离组    | Master 节点默认位于同一硬件隔离组，硬件隔离组能严格确保组内的每一台云主机都落在不同的物理机上。每个隔离组在单个可用区至多可以添加 7 台云主机，详见[硬件隔离组](uhost/guide/isolationgroup)                                                                             |
| 最大 Pod 数 | 单个 Node 节点可支持承载的最大 Pod 数量                                                                                                                                                                     |
| 标签       | Node 节点标签，详见 Kubernetes 官方文档：[标签和运算符](https://kubernetes.io/zh/docs/concepts/overview/working-with-objects/labels/)                                                                           |
| 污点       | Node 节点污点，详见 Kubernetes 官方文档：[污点和容忍度](https://kubernetes.io/zh/docs/concepts/scheduling-eviction/taint-and-toleration/)                                                                       |
| 禁用节点     | 开启禁用节点(cordon 节点)选项，节点将作为不可调度节点加入集群，可按需启用节点。                                                                                                                                                             |
| 自定义数据    | 是指主机初次启动或每次启动时，系统自动运行的配置脚本，该脚本可由控制台 API 等传入元数据服务器，并由主机内的 cloud-init 程序获取，脚本遵循标准 CloudInit 语法。该脚本会阻塞 UK8S 的安装脚本，即只有该脚本执行完毕后，才会开始K8S相关组件的安装，如Kubelet、Scheduler等。                                |
| 初始化脚本    | 该脚本只在 UK8S 启动后执行一次，且是在 K8S 相关组件安装成功后执行。遵循标准shell语法， 执行结果会存入到 `/var/log/message/` 目录下。                                                                                                         |

## 节点操作

增加节点后，可以在集群页面的节点列表页面查看节点列表。并且对节点进行：“禁用”、“删除”、“详情”、“绑定EIP”、“修改外网防火墙”等操作

![](/images/userguide/addnode/node-list.png)
![](/images/userguide/addnode/node-info.png)
#### 禁用

禁用是对节点执行`kubectl cordon node` 命令，使节点`Unschedulable`，但是不会驱逐当前节点上的Pod；
![](/images/userguide/addnode/node-cordon.png)

#### 删除
删除节点时，可以勾选同时删除云主机资源和云主机上的数据盘，如果不勾选则仅从集群内把节点删除；

建议： 先驱逐节点上服务再做删除节点操作，确保服务可用性。
![](/images/userguide/addnode/node-delete.png)
![](/images/userguide/addnode/node-delete1.png)

## 节点标签
您可以在节点列表页面，通过`修改标签`按钮为 Worker 节点添加、修改或删除标签。节点标签是 Kubernetes 中用于标识节点特征的键值对，可用于 Pod 的调度策略。

#### 标签的格式要求：
- 标签以键值对（key=value）的形式表示
- 单次操作仅支持**20对**及以下标签的修改操作
- 标签键（key）的限制：
    - 不建议使用 `kubernetes.io`、`k8s.io` 作为前缀，这些前缀为k8s系统保留标签
    - 使用系统保留前缀可能会导致调度异常或与系统标签冲突
    - 针对系统默认添加的标签，不建议修改，修改可能会导致系统服务问题。
- 键和值需符合 Kubernetes 标准命名规范

#### 操作步骤：

1. 在节点列表中，选择目标节点的"更多操作"
2. 点击"修改标签"
3. 在弹出的对话框中添加或修改标签
4. 点击"确定"完成修改
   ![](/images/userguide/addnode/update-label.png)

## 节点污点
可以在节点列表页面，通过`修改污点`按钮为 Worker 节点添加、修改或删除污点。节点污点（Taint）用于控制哪些 Pod 可以被调度到该节点上，需要配合 Pod 的容忍度（Toleration）使用。

#### 污点的格式要求：
- 污点以 `key=value:effect` 的形式表示
- 单次操作仅支持**10对**及以下污点的更新操作
- effect 必须是以下三种之一：
    - NoSchedule：不允许新的 Pod 调度到该节点（已有 Pod 不受影响）
    - PreferNoSchedule：尽量避免将新的 Pod 调度到该节点
    - NoExecute：不允许新的 Pod 调度到该节点，并驱逐已有的不能容忍该污点的 Pod

#### 操作步骤：
1. 在节点列表中，选择目标节点的"更多操作"
2. 点击"修改污点"
3. 在弹出的对话框中添加或修改污点
4. 点击"确定"完成修改
   ![](/images/userguide/addnode/update-taint.png)