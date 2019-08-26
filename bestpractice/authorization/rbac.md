{{indexmenu_n>0}}
## 了解RBAC


### 简介
RBAC是一种基于角色来管理对计算机或网络资源访问策略的方法。

我们知道，对K8S内所有API对象的操作都是通过访问kube-apiserver来完成的，因此kube-apiserver需要校验访问者是否具备操作这些API对象的权限。而K8S中负责授权和权限校验(Authorization&Authentication)的这套机制，则是RBAC：基于角色的访问控制（Role-Based Access Control ）

在Kubernetes的RBAC模型里面，有三个基本的概念：

+ Role：角色，其实是一组权限规则的集合，定义了一组对Kubernetes API 对象的操作权限。

+ Subject：主体，即被授予角色的"人"或"物"，即可以是Kubernetes里面的Service Account，也可以是外部User，为了简单起见，本文主要以Service Account来做演示。

+ RoleBinding：定义了'Role'与'Subject'的绑定关系。

而至于ClusterRole、ClusterRoleBinding，在概念上与Role、RoleBinding非常相似，只是作用域不同而已。

### Role & ClusterRole

#### 1、Role---namespace维度的权限集合

首先我们来介绍下Role，Role本身也是Kubernetes中的一个 API 对象，其定义如下：

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

首先，我们注意到这个名为"pod-reader"的Role，通过''namespace: default''指定了他能产生作用的Namespace。

Namespace是Kubernetes中的一个逻辑管理单位，Kubernetes中大部分业务类API对象（如Pod、Service）都是Namespace级别的，在操作时需要显式指明Namespace，如：kubectl edit role/pod-reader -n namespace2.

然后是rules字段，一个Role对象所拥有的权限，其实就是通过rules字段来定义了。

* apiGroups：apiGroup代表API对象所属的组，可以通过kubectl api-resources来查看API对象属于哪个组，上文示例""代表Core API group。

* resources： 用于声明该角色可访问的API对象。

* verbs：用于声明该角色可对API对象进行的操作，在Kubernetes中，verbs的全集为"get", "list", "watch", "create", "update", "patch", "delete"，如果我们要赋予某个role对某个API对象的所有权限，指定verbs的全部集合即可。

* resourceName：resourceName表示具体的K8S资源，需要注意的是，当声明了resourceName时，则verbs中不能再赋予list操作，该字段较少使用，一般用于较细粒度的权限管理。

了解了Role每个字段的含义后，上文Role示例的意义其实就很清楚了：**一组可对default命名空间下所有的Pod，进行GET、WATCH、LIST操作的权限集合，名称为pod-reader。**

#### 2、ClusterRole---Cluster维度的权限集合

ClusterRole的API定义与Role基本相同，你可以给一个ClusterRole赋予与Role一样的权限。但由于其cluster-wide的特性，ClusterRole可以被赋予一些不同的权限：

* 集群级别的API对象访问权限，如nodes、namespace、pv；

* 非资源类型endpoints的访问权限，如"/healthz";

* 所有Namespace下资源的访问权限，如kubectl get pods --all-namespaces；

下文是一个ClusterRole的示例，与Role最大的区别就在于不需要声明namespace。

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  # "namespace" omitted since ClusterRoles are not namespaced
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

值得注意的是，Kubernetes内置了很多为系统保留的ClusterRole，你可以通过kubectl get clusterrole查看到他们。一般来说，这些ClusterRole，是绑定给系统组件对应的service account使用的。比如，其中一个名为system:controller:cronjob-controller的ClusterRole，定义的权限规则是Cronjob这个控制器运行所必要的权限。你可以通过如下示例查看查看其权限规则。

```
bash-4.4# kubectl describe clusterrole system:controller:cronjob-controller
Name:         system:controller:cronjob-controller
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
  Resources                  Non-Resource URLs  Resource Names  Verbs
  ---------                  -----------------  --------------  -----
  jobs.batch                 []                 []              [create delete get list patch update watch]
  events                     []                 []              [create patch update]
  pods                       []                 []              [delete list]
  cronjobs.batch             []                 []              [get list update watch]
  cronjobs.batch/finalizers  []                 []              [update]
  cronjobs.batch/status      []                 []              [update]

```

除此以外，还有几个预先的定义的CluterRole值得留意下，后面给其他集群用户配置权限的时候，我们可能会用到：

* view

* edit

* admin

* cluster-admin

其所拥有的权限，通过其名称我们也能猜到大概，具体的权限规则可以通过kubectl describe clusterrole clusterrole-name来查看。

了解了Role和ClusterRole后，我们知道如何在Kubernetes集群内声明一组权限集合，那怎么把权限赋予某个具体的"人"或"物"呢？答案就是RoleBinding和ClusterRoleBinding啦。

### RoleBinding&ClusterRoleBinding

#### 1、Rolebinding---在Namespace范围内授予权限

Rolebinding可将角色中定义的权限授予用户或用户组，它包含subject（user、group或Service Account），以及所引用的角色。RoleBinding可以在同一命名空间中引用Role（意味着Role和Rolebinding必须位于同一Namespace）。 

以下RoleBinding的示例，将“pod-reader”角色授予“default”命名空间中的“jane”。 这允许“jane”读取“默认”命名空间中的pod。

```
apiVersion: rbac.authorization.k8s.io/v1
# This role binding allows "jane" to read pods in the "default" namespace.
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: jane # must create a ServiceAccount jane in default namespace
  namespace: default
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role #this must be Role or ClusterRole
  name: pod-reader # this must match the name of the Role or ClusterRole you wish to bind to
  apiGroup: rbac.authorization.k8s.io
```

值得注意的是，一个RoleBinding也可以引用ClusterRole，这样ClusterRole中所定义的Namespace级别的权限将会被赋予Subject，当然只在rolebinding所在的Namespace有效。这样做的好处是，集群管理员可以预先创建一些通用的ClusterRole，然后在不同的Namespace中使用他们，比如在上个章节提到的view、admin.

如下文所示，虽然"view-only"这个RoleBinding引用了ClusterRole，但"ucloud"这个ServiceAccount只拥有查看"development"这个命名空间下所有资源的权限，而不能查看所有命名空间下的资源。
```
apiVersion: rbac.authorization.k8s.io/v1
# This role binding allows "dave" to read secrets in the "development" namespace.
kind: RoleBinding
metadata:
  name: view-only
  namespace: development # This only grants permissions within the "development" namespace.
subjects:
- kind: ServiceAccount
  name: ucloud # Create a ServiceAccount in your cluster before test
  namespace: production # The namespace of subject can be different with Rolebinding
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
```
#### 2、ClusterRoleBinding---在Cluster范围内授予权限

下面我们来了解下ClusterRoleBinding，前面我们提到过，Role和RoleBinding都是Namespace级别的资源，也就是说他们所声明的权限规则都只在Namespace范围内有效。
那如果我们

1. 想让某个Subject（用户）拥有所有Namespace的查看权限；

2. 或者想让某个Pod拥有查看Node的权限；

应该怎么办呢？这就需要用到ClusterRole和ClusterRoleBinding这对组合了，和ClusterRole一样，ClusterRoleBinding与RoleBinding的最大不同其实就是不需要声明"namespace"这个字段了。

首先我们来看一个示例，我们想让techleader拥有所有Namespace的查看权限，注意roleRef，对于ClusterRoleBinding，只能引用ClusterRole，而不能是Role。

```
apiVersion: rbac.authorization.k8s.io/v1
# This cluster role binding allows a service account named "techleader" to view resource in any namespace.
kind: ClusterRoleBinding
metadata:
  name: techleader-read-global
subjects:
- kind: ServiceAccount
  name: techleader   
  namespace: default
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
```

其次，我们还希望为techleader赋予查看nodes的权限，所以我们需要在创建一个ClusterRole和ClusterRoleBinding。

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  # "namespace" omitted since ClusterRoles are not namespaced
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "watch", "list"]
```

```
apiVersion: rbac.authorization.k8s.io/v1
# This cluster role binding allows a service account named "techleader" to view resource in any namespace.
kind: ClusterRoleBinding
metadata:
  name: techleader-read-node
subjects:
- kind: ServiceAccount
  name: techleader   
  namespace: default
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

本文介绍了Kubernetes RBAC 模型中四个最主要的API对象，即Role、ClusterRole、RoleBinding、ClusterRoleBinding，大致了解了RBAC的工作原理和使用方法，如果要更加深入地了解和掌握RBAC，可以查看[官方文档](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)。
