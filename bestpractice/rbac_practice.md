# 自定义 RBAC 权限

本文主要通过一个例子来介绍如何基于 Kubernetes 的 RBAC 实现授权决策，允许集群管理员通过 Kubernetes API 动态配置策略，让非集群管理员具有某个 namespace
下的所有权限，并可通过 Dashboard 或者 kubectl 来管理该 ns 下的资源。

如果要更加深入地了解和掌握 RBAC，可以查看[官方文档](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)。

K8S里面有两类用户，
* Service Account，Kubernetes 中一种用于非人类用户的账号，在 Kubernetes 集群中提供不同的身份标识。详细可参考[官方文档](https://kubernetes.io/docs/concepts/security/service-accounts/)
* 普通用户(user)，K8S本身不并管理user，而是交由外部独立服务管理，不能通过K8SAPI来创建user;

目前是通过kubectl和Dashboard来管理集群，Service
account已经足够满足要求，而且可以在Kubernetes中直接管理。因此这里不介绍如何使用user这个对象来管理集群。


## 1. 创建NS

```
kubectl create ns pre
```

上面的示例创建了一个名为"pre"的命名空间，用于部署预发布的服务。

## 2. 创建Service Account

```
kubectl create sa mingpianwang -n pre
```

在pre的命名空间下创建一个名为"mingpianwang"的Service account，给到某个特定的用户使用。

## 3. 赋予权限

由于我们已经预先说明，需要给mingpianwang这个用户赋予pre 这个命名空间下的所有权限，即admin权限。

**重点来了**，[RoleBinding](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#rolebinding-and-clusterrolebinding)对象是可以引用一个ClusterRole对象的，然后这个ClusterRole所拥有的权限只会在这个NS下面有效。这一点允许管理员在整个集群范围内首先定义一组通用的角色，然后再在不同的名字空间中复用这些角色。

我们先看下集群内默认的ClusterRole有哪些，执行get
clusterrole命名可以看到，有admin、cluster-admin、edit等角色，那我们可以直接使用admin这个clusterrole角色，通过rolebinding的方式赋予”mingpianwang“这个用户。

```
[root@10-9-149-7 ~]# kubectl get clusterrole
NAME AGE
admin 4h53m
cluster-admin 4h53m
edit 4h53m
```

示例的yaml如下，我们只要执行下kubectl apply -f rolebinding.yaml 即可。

```
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kubernetes-dashboard-minimal
  namespace: pre
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: admin
subjects:
- kind: ServiceAccount
  name: mingpianwang
  namespace: pre
```

当然，我们也可以创建一个Namespace级别的role，并将这个角色绑定到ServiceAccount。

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: pre
  name: admin
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["*"]
  verbs: ["*"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kubernetes-dashboard-minimal
  namespace: pre
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: admin
subjects:
- kind: ServiceAccount
  name: mingpianwang
  namespace: pre
```

只是这个role不能复用到其他Namespace，一般只有在做精细化权限管理的时候，我们才会创建Role对象，比如一个只能查看pod
名称为test-pod的Role。其他场景下，我们推荐集群管理员使用ClusterRole。

## 4. 访问Dashboard

在 Kubernetes 1.22 之前的版本中，Kubernetes 会以Secret 形式为ServciceAccount 提供一个长期的有效的静态令牌， Kubernetes v1.22 及更高版本中，需要用户自己配置；详细的可参考官方文档[手动获取 ServiceAccount 凭据](https://kubernetes.io/docs/concepts/security/service-accounts/#assign-to-pod)

#### Kubernetes 1.22 之前的版本
就要获取到”mingpianwang“的token，其实就是secret了。通过下面的方式来获取，最后的token复制下来就可以了。

```
bash-4.4# kubectl describe sa/mingpianwang -n pre
Name:                mingpianwang
Namespace:           pre
Labels:              <none>
Annotations:         <none>
Image pull secrets:  <none>
Mountable secrets:   mingpianwang-token-4l8xj
Tokens:              mingpianwang-token-4l8xj
Events:              <none>
bash-4.4# kubectl describe secret/mingpianwang-token-4l8xj -n pre
Name:         mingpianwang-token-4l8xj
Namespace:    pre
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: mingpianwang
              kubernetes.io/service-account.uid: d7bb847d-7621-11e9-9679-5254007e7ba9

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1359 bytes
namespace:  5 bytes
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9/....
```

#### Kubernetes 1.22 之后的版本

如果你需要为 ServiceAccount 获得一个 API 令牌，你可以创建一个新的、带有特殊注解 kubernetes.io/service-account.name 的 Secret 对象。详细可参考官方文档[手动获取一个长久的Token](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#manually-create-a-long-lived-api-token-for-a-serviceaccount)

```
bash-4.4# kubectl -n pre apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: mingpianwang-secret
  annotations:
    kubernetes.io/service-account.name: mingpianwang
type: kubernetes.io/service-account-token
EOF
```

可以通过下面的命令来查看 Secret：
```
bash-4.4# kubectl -n pre describe secrets/mingpianwang-secret
Name:         mingpianwang-secret
Namespace:    pre
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: mingpianwang
              kubernetes.io/service-account.uid: 0c3e9a16-6962-45ee-9e6e-e7f0107cd9a8

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1359 bytes
namespace:  3 bytes
token:     ...
```

这里将 token 的内容抹去了。当你删除一个与某 Secret 相关联的 ServiceAccount 时，Kubernetes 的控制面会自动清理该 Secret 中长期有效的令牌。

可以使用以下命令查看 ServiceAccount:
```
kubectl -n pre get serviceaccount mingpianwang -o yaml
```
在 ServiceAccount API 对象中看不到 mingpianwang-secret Secret， .secrets 字段， 因为该字段只会填充自动生成的 Secret。


#### 登陆Dashboard

复制到登录框，我们发现可以登录到Dashboard首页，不过需要注意的是，由于这个账号只有pre这个命名空间的权限，而Dashboard默认是default，所以进去之后会报一堆错咯，没关系，只要将左侧的NS改为pre即可。

## 5. 通过 kubectl 管理集群

由于我们还需要支持 kubectl 命令行管理 NS，因此还需要为 mingpianwang 生成kubeconfig，一个用户还好，多个用户就很麻烦了，因此这里我们使用一个自动生成
kubeconfig 的脚本，代码如下：

```
#!/bin/bash -e
# Usage ./k8s-service-account-kubeconfig.sh ( namespace ) ( service account name )
TEMPDIR=$( mktemp -d )
trap "{ rm -rf $TEMPDIR ; exit 255; }" EXIT
SA_SECRET=$( kubectl get sa -n $1 $2 -o jsonpath='{.secrets[0].name}' )
# Pull the bearer token and cluster CA from the service account secret.
BEARER_TOKEN=$( kubectl get secrets -n $1 $SA_SECRET -o jsonpath='{.data.token}' | base64 -d )
kubectl get secrets -n $1 $SA_SECRET -o jsonpath='{.data.ca\.crt}' | base64 -d > $TEMPDIR/ca.crt
CLUSTER_URL=$( kubectl config view -o jsonpath='{.clusters[0].cluster.server}' )
KUBECONFIG=kubeconfig

kubectl config --kubeconfig=$KUBECONFIG \
    set-cluster \
    $CLUSTER_URL \
    --server=$CLUSTER_URL \
    --certificate-authority=$TEMPDIR/ca.crt \
    --embed-certs=true

kubectl config --kubeconfig=$KUBECONFIG \
    set-credentials $2 --token=$BEARER_TOKEN

kubectl config --kubeconfig=$KUBECONFIG \
    set-context registry \
    --cluster=$CLUSTER_URL \
    --user=$2 \
    --namespace=$1

kubectl config --kubeconfig=$KUBECONFIG \
    use-context registry

echo "kubeconfig written to file \"$KUBECONFIG\""
```

直接在master节点执行`sh kubeconfig.sh pre mingpianwang`，即可自动生成一个kubeconfig文件，将这个kubeconfig文件分发给使用者，让其复制到~/.kube/config下即可，而且默认NS就是pre，get
nodes等操作都是不被允许的。

自动生成kubeconfig的源代码在这里，[generator kubeconfig](https://gist.github.com/ericchiang/d2a838ddad3f44436ae001a342e1001e)，我们只是加了一个默认NS，这样不需要在执行kubectl命令的时候追加-n
pre。
