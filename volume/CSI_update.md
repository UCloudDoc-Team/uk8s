# CSI 变更记录及更新方法

> CSI升级操作仅支持 UK8S 集群大于 1.14 版本且在使用 CSI 插件的集群，如您删除过 CSI 插件则需要重新部署 userdata 信息。

## 1. 版本查看及插件升级

<!--### 1.1 控制台操作-->

在 UK8S 集群控制台管理页面「插件-存储插件」页面，开启 CSI 存储插件升级功能，开启 CSI 插件功能会在集群中执⾏ CSI 插件查询任务，⼤约需要 3
分钟，在此过程中请不要操作集群。升级功能开启后，即可看到 CSI 插件版本信息，点击「升级 CSI」即可进行升级。

升级过程约需要 1 分钟，升级过程中「当前版本」字段会显示为「升级中」，升级完成后显示最新版本号，如升级失败，请与我们技术支持联系。

当所有节点都升级成功后，可关闭插件升级服务，后续有升级需求时再开启。

> ⚠️ 集群进行存储插件升级时，请勿进行服务发布等操作

> ⚠️ 21.09.1 版本之前的CSI进行升级，会造成使用US3/UFile的pod挂载点失效，如果您的业务使用了US3/UFile，请务必确认当前版本，如有疑问，请与我们技术支持联系。

<!--### 1.2 命令行操作

#### 集群缺失userdata的重装方法

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

#### 更新 UDisk CSI 插件

```bash
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/udisk.21.11.1/csi-controller.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/udisk.21.11.1/csi-node.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/udisk.21.11.1/rbac-controller.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/udisk.21.11.1/rbac-node.yml
```

#### 更新 US3 CSI 插件

```bash
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/us3.21.11.1/csi-controller.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/us3.21.11.1/csi-node.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/us3.21.11.1/rbac-controller.yml
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/volume/us3.21.11.1/rbac-node.yml
```
-->

## 2. 变更记录

| 版本          | 更新时间       | 更新内容                                                                                     |
| ----------- | ---------- | ---------------------------------------------------------------------------------------- |
| **21.11.2** | 2021.11.22 | 1. csi udisk支持方舟模式; <br>2. csi udisk支持指定业务组; <br>3. 优化us3 挂载参数                           |
| **21.11.1** | 2021.11.04 | 1. 适配了 s3fs 返回成功而实际挂载失败的情况；<br>2. 修复因 US3 公私钥长度变化导致的挂载失败；<br>3. 始终通过节点 us3lancher 服务操作挂载 |
| **21.09.1** | 2021.09.07 | 将s3fs挂载操作放在Node上进行                                                                       |
| **21.08.1** | 2021.08.12 | 优化 CSI 插件调度机制，避免被驱逐                                                                      |
| **21.07.1** | 2021.07.05 | 支持云盘裸金属                                                                                  |
| **21.04.1** | 2021.04.28 | 支持 UDisk 相关参数暴露在 Kubelet Metrics 中                                                       |
| **21.03.1** | 2021.03.15 | 解决节点被删除后，volumeattachment 未被删除导致存储无法卸载的问题                                                |
| **21.01.1** | 2021.01.13 | UDisk的起始大小变更为1GB                                                                         |
| **20.10.1** | 2020.10.14 | 支持CSI限制节点最大可挂载卷的数量<br>避免UCloud API客户端可能产生的并发竞争行为                                         |
