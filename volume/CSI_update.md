# CSI更新20.10.1

> CSI升级操作仅支持uk8s集群大于1.14版本且在使用CSI插件的集群，如您删除过CSI插件则需要重新部署userdata信息。

> 后续CSI更新工作，将添加至集群插件中进行点击更新。

## 变更记录

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
  UCLOUD_REGION_ID: 'cn-bj2'
  UCLOUD_PROJECT_ID: 'org-1uxhh0'
  UCLOUD_VPC_ID: 'uvnet-fngihq'
  UCLOUD_SUBNET_ID: 'subnet-tk2h2v'
  UCLOUD_API_ENDPOINT: 'http://api.service.ucloud.cn'
  UCLOUD_UK8S_CLUSTER_ID: 'uk8s-3aqwlaey'

```

### 更新UDisk CSI插件

```bash
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/valume/udisk20.10.1/csi-controller.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/valume/udisk20.10.1/csi-node.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/valume/udisk20.10.1/rbac-controller.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/valume/udisk20.10.1/rbac-node.yml
```

### 更新UFile CSI插件

```bash
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/valume/ufile20.10.1/csi-controller.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/valume/ufile20.10.1/csi-node.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/valume/ufile20.10.1/rbac-controller.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/valume/ufile20.10.1/rbac-node.yml
```