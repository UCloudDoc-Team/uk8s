# 权限管理

UK8S通过UCloud原生的访问控制（IAM）和Kubernetes原生的RBAC机制，支持对集群级别和集群内资源级别进行精细化的权限管理。

- IAM授权：通过UCloud原生的权限管理进行授权，属于云资源级别的授权。[详细文档](/uk8s/auth/iam)。
  - 集群：创建、查看、升级、删除
  - 节点/节点池：创建、增加、删除
  - 应用中心：开启、查看、关闭
  - 监控中心：开启、修改、查看、关闭
  - 插件管理：开启、查看、升级、关闭
  - CA集群伸缩：开启、配置、关闭
- RBAC授权：基于Kubernetes RBAC进行的授权，属于集群内部资源维度的授权。[详细文档](/uk8s/auth/rbac)
  - 工作负载：Deployment、StatefulSet、DaemonSet、Job、CronJob、Pod、ReplicaSet等
  - 网络：Service、Ingress、NetworkPolicy等
  - 存储：PV、PVC、StorageClass等
  - 弹性伸缩：HPA、CronHPA等
  - Namespace、ConfigMap 、Secrets等
  - 非页面展示的其他Kubernetes资源类型

在没有开启授权管理的情况下（历史集群默认不开启），子账号只要获得了集群的查看权限，就可以看到集群的管理凭证，并且可以通过这个凭证查看并操作集群内的所有资源。这时Kubernetes RBAC权限控制是对子账号不生效的。

目前，所有UK8S新集群都会开启授权管理以防止上述危险行为。**如果您的集群是历史集群，强烈建议开启授权管理功能，以更加精细化地管理子账号的RBAC权限，并防止集群的管理凭证被轻易泄漏**。

当前授权管理功能一旦打开将无法关闭。
