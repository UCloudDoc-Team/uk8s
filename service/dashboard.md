
## 通过ULB暴露Kubernetes Dashboard


Dashboard是Kubernetes社区的一个Web开源项目，你可以通过Dashboard来部署更新应用、排查应用故障以及管理Kubernetes集群资源。另外，Dashboard还提供了集群的状态，以及错误日志等信息。下面我们介绍下如何在UK8S上部署、访问DashBoard。

### 部署Dashboard

UK8S集群没有默认安装Dashboard，如果你希望体验社区原生Dashboard，需要自行安装，下载yaml示例，在集群中输入如下命令即可：

```
kubectl apply -f dashboard-ui.yaml
```

具体的yaml示例如下，涉及的Kubernetes对象有Deployment、LoadBalancer Service、Role、RoleBinding、ServiceAccount等。需要注意的是，Service的访问类型为HTTP，如果您希望使用HTTPS，请先购买SSL证书。

```
# ------------------- Dashboard Deployment ------------------- #
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    k8s-app: kubernetes-dashboard-http
  name: kubernetes-dashboard-http
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: kubernetes-dashboard-http
  template:
    metadata:
      labels:
        k8s-app: kubernetes-dashboard-http
    spec:
      containers:
      - args:
        - --enable-insecure-login=true
        - --insecure-bind-address=0.0.0.0
        - --disable-skip=true
        image: uhub.service.ucloud.cn/library/kubernetes-dashboard-http
        imagePullPolicy: IfNotPresent
        name: kubernetes-dashboard-http
        ports:
        - containerPort: 9090
          protocol: TCP
        volumeMounts:
        - name: kubernetes-dashboard-certs
          mountPath: /certs
          # Create on-disk volume to store exec logs
        - mountPath: /tmp
          name: tmp-volume
      volumes:
      - name: kubernetes-dashboard-certs
        secret:
          secretName: kubernetes-dashboard-certs
      - name: tmp-volume
        emptyDir: {}
      serviceAccountName: kubernetes-dashboard

---
# ------------------- Dashboard Token ------------------- #
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: dashboard-ui-rolebind
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: dashboard-ui
  namespace: kube-system
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: dashboard-ui
  namespace: kube-system
  labels:
    kubernetes.io/cluster-service: "true"
    addonmanager.kubernetes.io/mode: Reconcile

---
# ------------------- Dashboard Secret ------------------- #

apiVersion: v1
kind: Secret
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard-certs
  namespace: kube-system
type: Opaque

---
# ------------------- Dashboard Service Account ------------------- #

apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kube-system

---

kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: kubernetes-dashboard-minimal
  namespace: kube-system
rules:
  # Allow Dashboard to create 'kubernetes-dashboard-key-holder' secret.
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["create"]
  # Allow Dashboard to create 'kubernetes-dashboard-settings' config map.
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["create"]
  # Allow Dashboard to get, update and delete Dashboard exclusive secrets.
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["kubernetes-dashboard-key-holder", "kubernetes-dashboard-certs"]
  verbs: ["get", "update", "delete"]
  # Allow Dashboard to get and update 'kubernetes-dashboard-settings' config map.
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["kubernetes-dashboard-settings"]
  verbs: ["get", "update"]
  # Allow Dashboard to get metrics from heapster.
- apiGroups: [""]
  resources: ["services"]
  resourceNames: ["heapster"]
  verbs: ["proxy"]
- apiGroups: [""]
  resources: ["services/proxy"]
  resourceNames: ["heapster", "http:heapster:", "https:heapster:"]
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kubernetes-dashboard-minimal
  namespace: kube-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: kubernetes-dashboard-minimal
subjects:
- kind: ServiceAccount
  name: kubernetes-dashboard
  namespace: kube-system

---
apiVersion: v1
kind: Service
metadata:
  name: kubernetes-dashboard-http
  namespace: kube-system
  annotations:
    service.beta.kubernetes.io/ucloud-load-balancer-eip-chargetype: dynamic
  labels:
    k8s-app: kubernetes-dashboard
    kubernetes.io/cluster-service: "true"
    addonmanager.kubernetes.io/mode: Reconcile
spec:
  type: LoadBalancer
  selector:
    k8s-app: kubernetes-dashboard-http
  ports:
  - port: 80
    targetPort: 9090
    protocol: TCP

```

### 二、访问Dashboard

在上面的实例中，我们创建了一个名为kubernetes-dashboard-http的Service，service type为LoadBalancer，可直接通过Service 的外网IP（实际为ULB的外网IP）访问Dashboard。

```kubectl get svc -n kube-system | grep kubernetes-dashboard-http ```


获取到外网IP后，我们直接在浏览器中输入IP，到达登录页面，Dashboard支持kubeconfig和token两种身份验证方式，此处我们选择Token验证方式。


在之前的yaml里，我们创建了一个dashboard-ui的ServiceAccount，我们可通过以下命名获取该服务账号的Token，用来登录Dashboard。

```
kubectl describe secret dashboard-ui -n kube-system
```

将获取的token复制到输入框，点击登录，即可开始使用Dashboard。
