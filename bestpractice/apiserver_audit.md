# APIServer 审计功能

**审计功能使得集群管理员能够回答以下问题：**

- 发生了什么？
- 什么时候发生的？
- 谁触发的？
- 活动发生在哪个（些）对象上？
- 在哪观察到的？
- 它从哪触发的？
- 活动的后续处理行为是什么？

> 审计日志记录功能会增加 API server 的内存消耗，因为需要为每个请求存储审计所需的某些上下文。 此外，内存消耗取决于审计日志记录的配置。

## 1. 审计策略

通过编辑文件 `/etc/kubernetes/audit-policy.yaml`，设定自己的审计策略

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
  - "RequestReceived"
rules:
  # 集群中包含大量以下低风险请求，建议不做审计（不记录日志）
  # kube-proxy 的 watch 请求
  - level: None
    users: ["system:kube-proxy"]
    verbs: ["watch"]
    resources:
      - group: "" # core
        resources: ["endpoints", "services", "services/status"]
  # 在 kube-system namespace 下对 configmap 的 get 请求
  - level: None
    users: ["system:unsecured"]
    namespaces: ["kube-system"]
    verbs: ["get"]
    resources:
      - group: "" # core
        resources: ["configmaps"]
  # kubelet 对于 node 节点的 get 请求
  - level: None
    users: ["kubelet"] # legacy kubelet identity
    verbs: ["get"]
    resources:
      - group: "" # core
        resources: ["nodes", "nodes/status"]
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
  # apiserver 对于 namespace 的 get 请求
  - level: None
    users: ["system:apiserver"]
    verbs: ["get"]
    resources:
      - group: "" # core
        resources: ["namespaces", "namespaces/status", "namespaces/finalize"]
  # cluster-autoscaler 集群伸缩组件在 kube-system namespace 下对 configmap、endpoint 的 get/update 请求
  - level: None
    users: ["cluster-autoscaler"]
    verbs: ["get", "update"]
    namespaces: ["kube-system"]
    resources:
      - group: "" # core
        resources: ["configmaps", "endpoints"]
  # HPA 通过 controller manager 获取 metrics 信息的请求
  - level: None
    users:
      - system:kube-controller-manager
    verbs: ["get", "list"]
    resources:
      - group: "metrics.k8s.io"
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

### 1.1 阶段（omitStages）

| 阶段               | 含义                                                      |
| ---------------- | ------------------------------------------------------- |
| RequestReceived  | 此阶段对应审计处理器接收到请求后，并且在委托给 其余处理器之前生成的事件                    |
| ResponseStarted  | 在响应消息的头部发送后，响应消息体发送前生成的事件。 只有长时间运行的请求（例如 watch）才会生成这个阶段 |
| ResponseComplete | 当响应消息体完成并且没有更多数据需要传输的时候                                 |
| Panic            | 当 panic 发生时生成                                           |

### 1.2 审计级别（level）

| 级别              | 含义                                          |
| --------------- | ------------------------------------------- |
| None            | 符合这条规则的日志将不会记录                              |
| Metadata        | 记录请求的元数据（请求的用户、时间戳、资源、动词等等），但是不记录请求或者响应的消息体 |
| Request         | 记录事件的元数据和请求的消息体，但是不记录响应的消息体。 这不适用于非资源类型的请求  |
| RequestResponse | 记录事件的元数据，请求和响应的消息体。这不适用于非资源类型的请             |

## 2. 审计日志配置

分别登录 3 台 Master 节点，在 APIServer 配置文件 `/etc/kubernetes/apiserver` 中添加以下参数，并通过
`systemctl restart kube-apiserver` 重启 APIServer：

```
# 指定用来写入审计事件的日志文件路径。不指定此标志会禁用日志后端
--audit-log-path=/var/log/audit.log
# 指定审计策略配置文件
--audit-policy-file=/etc/kubernetes/audit-policy.yaml
# 定义保留旧审计日志文件的最大天数
--audit-log-maxage=7
# 定义要保留的审计日志文件的最大数量
--audit-log-maxbackup=10
# 定义审计日志文件的最大大小（兆字节）
--audit-log-maxsize=1000
```

## 3. 参考

- [Kubernetes 官方文档 - 审计](https://kubernetes.io/zh/docs/tasks/debug-application-cluster/audit/)
