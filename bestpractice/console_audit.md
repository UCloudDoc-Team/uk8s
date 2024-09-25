# 在控制台使用集群审计功能

**审计功能使得集群管理员能够回答以下问题：**

- 发生了什么？
- 什么时候发生的？
- 谁触发的？
- 活动发生在哪个（些）对象上？
- 在哪观察到的？
- 它从哪触发的？
- 活动的后续处理行为是什么？

> 审计日志记录功能会增加 API server 的内存消耗，因为需要为每个请求存储审计所需的某些上下文。 此外，内存消耗取决于审计日志记录的配置。

您可以通过UK8S的控制台来方便地开启集群审计功能，并将审计日志上传到ES中以方便进行查询。

## 准备

在开始前，您需要准备一个ES服务，以保存集群的审计日志。我们支持两种方式的ES：

- 直接使用UK8S提供的[日志ELK](/uk8s/log/ELKplugin)。（推荐）
- 使用外部ES，可以是您自建的或是我们的[UES服务](https://console.ucloud.cn/ues/manage)。需要确保该ES跟UK8S集群在同一个VPC中。

对于第一种方式，您需要打开控制台的`应用中心 / 日志ELK`功能。

![audit1](/images/bestpractice/audit1.png)

## 开启集群审计

> ⚠️ 开启集群审计时，会重启集群的APIServer，请在业务低谷期操作！

您可以直接到`应用中心 / 集群审计`页面开启审计：

![audit2](/images/bestpractice/audit2.png)

在开启时，如果您打算直接将审计日志上传到集群内部ELK，直接选择`集群日志ELK`即可。注意这需要您的集群开启了日志ELK插件功能：

![audit3](/images/bestpractice/audit3.png)

如果您需要使用外链ES，则选择`已有UES`，这需要您填入外部ES的子网和IP地址。如果您的ES开启了认证，还需要填入认证信息：

![audit4](/images/bestpractice/audit4.png)

点击确定，我们会启动一个异步任务，分别在3各master节点上做下面的事情：

- 上传审计策略文件到`/etc/kubernetes/yaml/audit-policy.yaml`。具体策略文件见下一节。
- 修改APIServer配置文件，增加审计相关参数：
  - `--audit-log-path=/var/log/kubernetes/audit.log`
  - `--audit-policy-file=/etc/kubernetes/yaml/audit-policy.yaml`
  - `--audit-log-maxage=7`
  - `--audit-log-maxbackup=10`
  - `--audit-log-maxsize=1000`
- 重启APIServer，以让审计开始生效。
- 启动一个filebeat服务，将审计日志上传到上面配置的ES中。

该过程会顺序执行，需要消耗几分钟时间来完成，请耐心等待。

## 审计策略

在默认情况下，我们会为您准备好一个审计策略文件。它适用于大多数情况：

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
  - "RequestReceived"
rules:
  # 集群中包含大量以下低风险请求，建议不做审计（不记录日志）
  - level: None
    users:
      - admin
      - kubelet
      - system:apiserver
      - system:kube-controller-manager
      - system:kube-proxy
      - system:serviceaccount:kube-system:cni-vpc-ipamd
      - system:unsecured
    verbs:
      - get
      - list
      - watch

  # system:node 用户组对于 node 节点的 get 请求
  - level: None
    userGroups: ["system:nodes"]
    verbs: ["get"]
    resources:
      - group: "" # core
        resources: ["nodes", "nodes/status"]

  # 系统组件在 kube-system namespace 下对于 endpoints 的 get/update 请求
  - level: None
    users:
      - system:kube-controller-manager
      - system:kube-scheduler
      - system:serviceaccount:kube-system:endpoint-controller
    verbs: ["get", "update"]
    namespaces: ["kube-system"]
    resources:
      - group: "" # core
        resources: ["endpoints"]

  # cluster-autoscaler 集群伸缩组件在 kube-system namespace 下对 configmap、endpoint 的 get/update 请求
  - level: None
    users: ["cluster-autoscaler"]
    verbs: ["get", "update"]
    namespaces: ["kube-system"]
    resources:
      - group: "" # core
        resources: ["configmaps", "endpoints"]

  # 以下只读 URL
  - level: None
    nonResourceURLs:
      - /healthz*
      - /version
      - /swagger*

  # event 事件
  - level: None
    resources:
      - group: "" # core
        resources: ["events"]

  # 集群插件有大量对lease的操作，不做审计
  - level: None
    resources:
      - group: "coordination.k8s.io"
        resources: ["leases"]

  # cloudprovider对endspoints的操作
  - level: None
    users: ["system:serviceaccount:kube-system:cloudprovider-ucloud"]
    resources:
      - group: ""
        resources: ["endpoints"]

  # kubelet、system:node-problem-detector 和 system:nodes 对于节点的 update 和 patch 请求，等级设置为 Request，记录元数据和请求的消息体
  - level: Request
    users: ["kubelet", "system:node-problem-detector", "system:serviceaccount:kube-system:node-problem-detector"]
    verbs: ["update","patch"]
    resources:
      - group: "" # core
        resources: ["nodes/status", "pods/status"]
  - level: Request
    userGroups: ["system:nodes"]
    verbs: ["update","patch"]
    resources:
      - group: "" # core
        resources: ["nodes/status", "pods/status"]

  # 对于可能包含敏感信息或二进制文件的 Secrets，ConfigMaps，tokenreviews 接口的日志等级设为 Metadata
  - level: Metadata
    resources:
      - group: "" # core
        resources: ["secrets", "configmaps", "serviceaccounts/token"]
      - group: authentication.k8s.io
        resources: ["tokenreviews"]

  # 对于一些返回体比较大的 get, list, watch 请求，设置为 Request
  - level: Request
    verbs: ["get", "list", "watch"]
    resources:
      - group: "" # core
      - group: "admissionregistration.k8s.io"
      - group: "apiextensions.k8s.io"
      - group: "apiregistration.k8s.io"
      - group: "apps"
      - group: "authentication.k8s.io"
      - group: "authorization.k8s.io"
      - group: "autoscaling"
      - group: "batch"
      - group: "certificates.k8s.io"
      - group: "extensions"
      - group: "metrics.k8s.io"
      - group: "networking.k8s.io"
      - group: "node.k8s.io"
      - group: "policy"
      - group: "rbac.authorization.k8s.io"
      - group: "scheduling.k8s.io"
      - group: "storage.k8s.io"

  # 对已知 Kubernetes API 默认设置为 RequestResponse
  - level: RequestResponse
    resources:
      - group: "" # core
      - group: "admissionregistration.k8s.io"
      - group: "apiextensions.k8s.io"
      - group: "apiregistration.k8s.io"
      - group: "apps"
      - group: "authentication.k8s.io"
      - group: "authorization.k8s.io"
      - group: "autoscaling"
      - group: "batch"
      - group: "certificates.k8s.io"
      - group: "extensions"
      - group: "metrics.k8s.io"
      - group: "networking.k8s.io"
      - group: "node.k8s.io"
      - group: "policy"
      - group: "rbac.authorization.k8s.io"
      - group: "scheduling.k8s.io"
      - group: "storage.k8s.io"

  # 对于其他请求都设置为 Metadata
  - level: Metadata
```

如果您对默认策略不满意，需要手动更改。

关于如何配置审计策略，请参考文档：[audit policy](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/#audit-policy)。

要更改审计策略，请将策略文件依次上传到3个master节点的`/etc/kubernetes/yaml/audit-policy.yaml`中，并依次执行`systemctl restart kube-apiserver`重启APIServer服务。

## 查看审计日志

开启审计之后，您可以在控制台简单地查询审计日志：

![audit5](/images/bestpractice/audit5.png)

我们支持一些简单维度的过滤操作。但是支持的字段有限，请以控制台为准。

如果您希望使用更加复杂的过滤条件，建议到ES或是Kibana中进行操作。


## 关闭集群审计

> ⚠️ 关闭集群审计时，会重启集群的APIServer，请在业务低谷期操作！

如果您不想使用集群审计了，例如觉得审计导致APIServer内存变得过高。可以在控制台进行关闭操作。直接在审计页面点击`关闭应用`即可：

![audit6](/images/bestpractice/audit6.png)

关闭审计会分别在3个master节点做下面的事情：

- 移除用于上传日志的`filebeat`服务。
- 修改APIServer配置文件，删除审计相关参数。
- 移除审计策略文件。
- 重启APIServer。
- 移除审计日志文件`/var/log/kubernetes/audit.log`。

该过程会顺序执行，需要消耗几分钟时间来完成，请耐心等待。
