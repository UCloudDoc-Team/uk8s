# CSI 变更记录及更新方法

> CSI升级操作仅支持 UK8S 集群大于 1.14 版本且在使用 CSI 插件的集群，如您删除过 CSI 插件则需要重新部署 userdata 信息。

> 后续CSI更新工作，将添加至集群插件中进行点击更新。

## 变更记录

### 更新版本：21.04.1

更新时间：2021.04.28

更新内容：

* 支持 UDisk 相关参数暴露在 Kubelet Metrics 中

### 更新版本：21.03.1

更新时间：2021.03.15

更新内容：

* 解决节点被删除后，volumeattachment 未被删除导致存储无法卸载的问题

### 更新版本: 21.01.1

更新时间： 2021.01.13

更新内容：

* UDisk的起始大小变更为1GB。

### 更新版本：20.10.1

更新时间：2020.10.14

更新内容：

* 支持CSI限制节点最大可挂载卷的数量。
* 避免UCloud API客户端可能产生的并发竞争行为。


## 更新操作

### 集群缺失userdata的重装方法

需要复制以下yaml文件，修改`data`中的参数，然后进行`kubectl apply -f`部署这个`configMap`


```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: uk8sconfig
  namespace: kube-system
data:
  UCLOUD_REGION_ID: 'cn-bj2' ## 集群所在地域，参照：https://docs.ucloud.cn/api/summary/regionlist
  UCLOUD_PROJECT_ID: 'org-xxxxxxxx' ## 项目 ID
  UCLOUD_VPC_ID: 'uvnet-xxxxxxxx'  ## 集群所在 VPC ID
  UCLOUD_SUBNET_ID: 'subnet-xxxxxxxx' ## 集群 Master 节点所在子网 ID
  UCLOUD_API_ENDPOINT: 'http://api.service.ucloud.cn'
  UCLOUD_UK8S_CLUSTER_ID: 'uk8s-3aqwlaey'  ## 集群 ID

```

### 更新UDisk CSI插件

```bash
kubectl apply -f https://git.ucloudadmin.com/uk8s/csi-uk8s/-/blob/21.04.1/deploy/udisk/csi-controller.yml
kubectl apply -f https://git.ucloudadmin.com/uk8s/csi-uk8s/-/blob/21.04.1/deploy/udisk/csi-node.yml
kubectl apply -f https://git.ucloudadmin.com/uk8s/csi-uk8s/-/blob/21.04.1/deploy/udisk/rbac-controller.yml
kubectl apply -f https://git.ucloudadmin.com/uk8s/csi-uk8s/-/blob/21.04.1/deploy/udisk/rbac-node.yml
```

### 更新UFile CSI插件

```bash
kubectl apply -f https://git.ucloudadmin.com/uk8s/csi-uk8s/-/blob/21.04.1/deploy/ufile/csi-controller.yml
kubectl apply -f https://git.ucloudadmin.com/uk8s/csi-uk8s/-/blob/21.04.1/deploy/ufile/csi-node.yml
kubectl apply -f https://git.ucloudadmin.com/uk8s/csi-uk8s/-/blob/21.04.1/deploy/ufile/rbac-controller.yml
kubectl apply -f https://git.ucloudadmin.com/uk8s/csi-uk8s/-/blob/21.04.1/deploy/ufile/rbac-controller.yml
```
