# APIServer 审计功能


**审计功能使得集群管理员能够回答以下问题：**

* 发生了什么？
* 什么时候发生的？
* 谁触发的？
* 活动发生在哪个（些）对象上？
* 在哪观察到的？
* 它从哪触发的？
* 活动的后续处理行为是什么？

> 审计日志记录功能会增加 API server 的内存消耗，因为需要为每个请求存储审计所需的某些上下文。 此外，内存消耗取决于审计日志记录的配置。

## 1. 审计策略

通过编辑文件 `/etc/kubernetes/audit-policy.yaml`，设定自己的审计策略

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
  - "RequestReceived"
rules:
  # The following requests were manually identified as high-volume and low-risk,
  # so drop them.
  - level: None
    users: ["system:kube-proxy"]
    verbs: ["watch"]
    resources:
      - group: "" # core
        resources: ["endpoints", "services", "services/status"]
  - level: None
    users: ["system:unsecured"]
    namespaces: ["kube-system"]
    verbs: ["get"]
    resources:
      - group: "" # core
        resources: ["configmaps"]
  - level: None
    users: ["kubelet"] # legacy kubelet identity
    verbs: ["get"]
    resources:
      - group: "" # core
        resources: ["nodes", "nodes/status"]
  - level: None
    userGroups: ["system:nodes"]
    verbs: ["get"]
    resources:
      - group: "" # core
        resources: ["nodes", "nodes/status"]
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
  - level: None
    users: ["system:apiserver"]
    verbs: ["get"]
    resources:
      - group: "" # core
        resources: ["namespaces", "namespaces/status", "namespaces/finalize"]
  - level: None
    users: ["cluster-autoscaler"]
    verbs: ["get", "update"]
    namespaces: ["kube-system"]
    resources:
      - group: "" # core
        resources: ["configmaps", "endpoints"]
  # Don't log HPA fetching metrics.
  - level: None
    users:
      - system:kube-controller-manager
    verbs: ["get", "list"]
    resources:
      - group: "metrics.k8s.io"

  # Don't log these read-only URLs.
  - level: None
    nonResourceURLs:
      - /healthz*
      - /version
      - /swagger*

  # Don't log events requests because of performance impact.
  - level: None
    resources:
      - group: "" # core
        resources: ["events"]

  # node and pod status calls from nodes are high-volume and can be large, don't log responses for expected updates from nodes
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

  # Secrets, ConfigMaps, TokenRequest and TokenReviews can contain sensitive & binary data,
  # so only log at the Metadata level.
  - level: Metadata
    resources:
      - group: "" # core
        resources: ["secrets", "configmaps", "serviceaccounts/token"]
      - group: authentication.k8s.io
        resources: ["tokenreviews"]

  # Get responses can be large; skip them.
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
      
  # Default level for known APIs
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
  # Default level for all other requests.
  - level: Metadata
```

### 1.1 阶段（omitStages）
|  阶段   | 含义  |
|  ----  | ----  |
| RequestReceived | 此阶段对应审计处理器接收到请求后，并且在委托给 其余处理器之前生成的事件 |
| ResponseStarted | 在响应消息的头部发送后，响应消息体发送前生成的事件。 只有长时间运行的请求（例如 watch）才会生成这个阶段 |
| ResponseComplete | 当响应消息体完成并且没有更多数据需要传输的时候 |
| Panic | 当 panic 发生时生成 |

### 1.2 审计级别（level）
|  级别   | 含义  |
|  ----  | ----  |
| None  | 符合这条规则的日志将不会记录 |
| Metadata  | 记录请求的元数据（请求的用户、时间戳、资源、动词等等），但是不记录请求或者响应的消息体 |
| Request | 记录事件的元数据和请求的消息体，但是不记录响应的消息体。 这不适用于非资源类型的请求 |
| RequestResponse | 记录事件的元数据，请求和响应的消息体。这不适用于非资源类型的请 |

## 2. 审计日志配置

分别登录 3 台 Master 节点，在 APIServer 配置文件 `/etc/kubernetes/apiserver` 中添加以下参数，并通过 `systemctl restart kube-apiserver` 重启 APIServer：

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

## 3. 说明

* 在收到请求后不立即记录日志，当返回体Header发送后才开始记录。
* kube-proxy watch请求，kubelet和system:nodes对于节点的get请求，kube组件在kube-system下对于endpoint的操作，以及API Server对于Namespaces的get请求等不作审计。
* 对于/healthz*，/version*/swagger*等只读URL不作审计。
* kubelet、system:node-problem-detector和system:nodes对于节点的update和patch请求，等级设置为Request，记录元数据和请求的消息体。
* 对于可能包含敏感信息或二进制文件的Secrets，ConfigMaps，tokenreviews接口的日志等级设为Metadata。
* 对于一些返回体比较大的get, list, watch请求，设置为Request。
* 其他请求都设置为Metadata。

## 4. 参考

* [Kubernetes 官方文档 - 审计](https://kubernetes.io/zh/docs/tasks/debug-application-cluster/audit/)