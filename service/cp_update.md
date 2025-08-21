# CloudProvider 插件更新

UK8S 通过 CloudProvider 插件，实现集群中 LoadBalancer 类型服务（SVC）与 UCloud ULB 产品的创建和绑定。

## 版本问题

如您集群 CloudProvider 为以下版本，请您务必及时按照文档更新，避免影响业务。升级过程不影响线上业务，但仍建议您在业务闲时进行更新，如有问题请及时与我们联系。

* 低于`20.10.1`版本

`20.10.1` 之前的版本存在 bug，会在 Service 重启时发生误判，导致重复创建 ULB 实例并写入集群，造成集群相应 Service 的不可用。为此我们对 CloudProvider
插件进行了优化，完善 ULB 相关接口的调用逻辑，避免了上述问题的出现。

* `24.03.13`版本

从 `24.03.13` 版本开始支持了[应用型负载均衡ALB](/ulb/alb/intro/whatisalb)，后续版本修复了 ALB 使用中的一些问题，推荐升级到 `24.09.18` 版本来使用 ALB。

- `24.12.24`版本

从`24.12.24`版本开始支持了[网络型负载均衡NLB](/ulb/NLB/intro/whatisnlb)，推荐升级到该版本或以上来使用NLB。

## 1. 版本查看及插件升级

### 1.1 控制台操作

针对[维护版本](/uk8s/version/maintain.md)之内UK8S 集群可以在控制台管理页面「插件-CloudProvider」页面，开启 CloudProvider 插件升级功能，开启
CloudProvider 插件升级功能会在集群中执⾏ CloudProvider 插件查询任务，⼤约需要 3 分钟，在此过程中请不要操作集群。升级功能开启后，即可看到 CloudProvider
插件版本信息，点击「升级 CloudProvider」即可进行升级。

升级过程约需要 1-3 分钟，升级过程中「当前版本」字段会显示为「升级中」，升级完成后显示最新版本号，如升级失败，可以再次尝试升级，或与我们技术支持联系。

> ⚠️ 集群 CloudProvider 插件升级时，请勿进行服务发布等操作

### 1.2 手动升级

如果集群版本不在我们的维护版本之内，控制台将无法直接进行升级，参见：[UK8S版本维护说明](/uk8s/version/maintain.md)。

这时候，您可以手动升级cloudprovider，请执行下面的命令：

```bash
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/cloudprovider/24.08.13.yml
```

### 1.3 老版本升级

如果 Kubernetes 版本在 1.14 以前，或者在控制台无法查看到 CloudProvider 版本信息，则需要通过命令行进行升级。

> 登录您集群的 Master 节点，如执行`systemctl status ucloudcp`是运行状态的话，请务必在**3 个 Master 节点**关闭二进制程序ucloudcp并更新。

#### 1. 关闭老版本 CloudProvider

请分别登陆3台master节点，执行以下命令

```
systemctl stop ucloudcp
systemctl disable ucloudcp
```

#### 2. 需要配置前置ConfigMap

请填写如下相关信息并保存文件为`userdata.yaml`。

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: uk8sconfig
  namespace: kube-system
data:
  UCLOUD_ACCESS_PRIKEY: xxxxxxxxxxxxxxx  #API PRIKEY
  UCLOUD_ACCESS_PUBKEY: xxxxxxxxxxxxxxx  #API_PUBKEY
  UCLOUD_API_ENDPOINT: http://api.service.ucloud.cn
  UCLOUD_PROJECT_ID: org-xxxxxx   #集群所在的项目ID
  UCLOUD_REGION_ID: cn-bj2  #集群所在的地域，参考：https://docs.ucloud.cn/api/summary/regionlist
  UCLOUD_SUBNET_ID: subnet-xxxxxx  #集群所在的子网ID
  UCLOUD_UK8S_CLUSTER_ID: uk8s-xxxxxx  #UK8S集群名称
  UCLOUD_VPC_ID: uvnet-xxxxxx   #集群所在的VPC ID
```

#### 3. 请执行创建ConfigMap

```
kubectl apply -f userdata.yaml
```

#### 4. 请执行部署 CloudProvider

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/cloudprovider/22.07.1.yml
```

#### 5. 检查是否部署成功

如 Pod 处于非 running 状态，请您及时与我们技术支持联系，更新成功后，即可在控制台查看版本信息并进行后续升级。

```
kubectl get pod -n kube-system -l app=cloudprovider-ucloud -o wide
```

## 2. 变更记录

### 更新版本：25.08.21

更新时间： 2025 年 08 月 21 日

更新内容：

- 修复添加vserver超过20个可能失败的问题，该问题自上个版本引入

### 更新版本：25.07.23

更新时间： 2025 年 07 月 23 日

更新内容：

- ALB/NLB支持Direct Endpoint (仅在vpc-cni下支持)

### 更新版本：25.04.02

更新时间： 2025 年 04 月 02 日

更新内容：

- eip支持线路选择

### 更新版本：24.12.24

更新时间： 2024 年 12 月 24 日

更新内容：

- 支持NLB

### 更新版本：24.11.13

更新时间： 2024 年 11 月 13 日

更新内容：

- 支持在创建ULB时指定要绑定的防火墙

### 更新版本：24.11.05

更新时间： 2024 年 11 月 05 日

更新内容：

- 修复了使用**新购的内网ALB**创建svc，在svc更新时会额外绑定EIP的问题

### 更新版本：24.10.10

更新时间： 2024 年 10 月 10 日

更新内容：

- 修复了使用**已有内网ALB**创建svc时会额外购买EIP的问题

### 更新版本：24.09.18

更新时间： 2024 年 9 月 18 日

更新内容：

- 修复了创建ALB时，在service中指定subnet-id无法生效的问题

### 更新版本：24.08.13

更新时间：2024 年 8 月 13 日

更新内容：

- 修复了在集群节点超过20个之后ALB无法使用的问题

### 更新版本：24.06.28

更新时间：2024 年 6 月 28 日

更新内容：

- 修复了多个svc绑定同一个ALB时存在的问题

### 更新版本：24.03.13

更新时间：2024 年 3 月 14 日

更新内容：

- 支持ALB

### 更新版本：24.03.5

更新时间：2024 年 3 月 7 日

更新内容：

- 支持ULB4的tcp和udp协议混用

### 更新版本：23.04.2

更新时间：2023 年 7 月 6 日

更新内容：

- 减少telemetry超时时间，避免telemetry超时影响ULB的正常使用

### 更新版本：22.10.1

更新时间：2022 年 10 月 25 日

更新内容：

- 优化 ULB Backend 添加逻辑，加快 LoadBalancer 类型的 Service 获取 external IP 的速度
- 优化外网 ULB 绑定的 EIP 的默认带宽配置，如果没有在 Service 中明确指定带宽，将不会更新已有 EIP 的带宽值，对于由 Cloud Provider 新创建的 EIP，仍使用默认带宽。

### 更新版本：22.07.1

更新时间：2022 年 7 月 15 日

更新内容：

- 优化ULB的查询逻辑，提高修改、删除Service的速度。
- 增加通过EIP进行ULB匹配的兜底逻辑。从而防止因为用户手动修改了ULB名称或备注导致Service无法正确跟ULB匹配而发生ULB重建的问题。

### 更新版本：22.06.2

更新时间：2022 年 6 月 28 日

更新内容：

- 修复当 service 的 externalTrafficPolicy 属性为 Local，缺少 ULB ID 信息注入的缺陷

### 更新版本：22.06.1

更新时间：2022 年 6 月 10 日

更新内容：

- 更新依赖的 cloud provider 框架更新至v0.20.15，以引入kubernetes/cloud-provider#38 使得节点状态更新能够尽快的通知到cloud provider
master、unready 以及具有 "node.kubernetes.io/exclude-from-external-load-balancers" label的节点不会加入到 lb 的 rs 中，而不再根据SchedulingDisabled 状态（k8s cloud provider 框架升级带来行为变化）

### 更新版本：21.10.2

更新时间：2021 年 11 月 4 日

更新内容：

- 优化了对 ULB 名称的校验，修复首次创建 VServer 失败导致 Service 无法创建的问题

### 更新版本：21.10.1

更新时间：2021 年 10 月 14 日

更新内容：

- 使用指定 ULB 创建 LoadBalancer 类型 Service 时，不能指定由 CloudProvider 创建的 ULB。

### 更新版本：21.05.2

更新时间：2021 年 5 月 28 日

更新内容：

- 加上 Endpoint Controller，感知 Endpoint 变化，在 externalTrafficPolicy=Local 的情况下，只会将运行了 Pod 的主机节点加入 ULB
  VServer Backends。
- **注意：**Endpoint 频繁变动会导致 ULB API 大量调用，需要在 cloudprovider 中添加如下参数，做限速处理。如需要调整参数，则必须通过命令行的方式，对插件进行调整。

```yaml
containers:
  - name: cloudprovider-ucloud
    image: uhub.service.ucloud.cn/uk8s/cloudprovider-ucloud:21.05.2
    args:
    - "--endpoint-updates-batch-period=10"   ## 所有 Endpoint 事件每隔 N 秒处理一次，默认为 10
```

### 更新版本：21.05.1

更新时间：2021 年 5 月 11 日

更新内容：

- 支持 UDP 类型 ULB 健康检查模式，需要在 Service 的 Annotations 中声明一下参数，ULB
  健康检查机制请参考：[健康检查](/ulb/faq/ulbhealthcheck)，ULB 注释详解请参考：[ULB 参数说明](/uk8s/service/annotations)

```yaml
annotations:
  ## 以下参数仅对 UDP 类型 ULB 生效
  service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-type: "customize"      ## 设置健康检查类型为 customize，代表 UDP 健康检查
  service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-reqmsg: ""    ## 代表 UDP 健康检查发出的请求报文
  service.beta.kubernetes.io/ucloud-load-balancer-vserver-monitor-respmsg: ""   ## 代表 UDP 健康检查请求应收到的响应报文
```

### 更新版本：21.04.1

更新时间：2021 年 4 月 22 日

更新内容：

- 可通过 Service Annotation，为节点添加注释，设定其在被设置为不可调度（即执行 Cordon 节点操作）后，不会自动被 ULB 剔除

```yaml
annotations:
  ## 默认为 'true'，设置为 'false' 后节点不可调度时不会自动被 ULB 剔除
  service.beta.kubernetes.io/ucloud-load-balancer-remove-unscheduled-backend: "false"
```

### 更新版本：21.02.1

更新时间：2021 年 2 月 6 日

更新内容：

- 支持内网 ULB7
- 支持 ULB7 的 TCP 模式

### 更新版本：20.10.2

更新时间：2020年10月29日

更新内容：

- 更新支持创建指定子网的ULB，详细设置请查看[通过内网ULB访问Service](/uk8s/service/internalservice)。

### 更新版本：20.10.1

更新时间：2020年10月20日

更新内容：

- 动态创建成功LoadBalancer类型的Service后，插件将把关联的ULB Id注入到Service的Annotations中，以规避因API超时等导致的ULB重建。

### 更新版本：20.09.4

更新时间：2020年9月18日

变更内容：

- 升级UCloud Go SDK修复ULB防火墙设置，
- 增加新创建时，使用临时的ULB客户端进行API调用。

### 更新版本：20.09.3

更新时间：2020年9月17日

变更内容：

- 更新监控信息(非强制更新)。

### 更新版本：20.09.2

更新时间：2020年9月8日

变更内容：

- 增加cloudprovider重启后调用ULB相关接口的容错性，提高集群的运行的稳定性。

<!---
## 更新前置检查

1. 集群创建于2020年10月20日前，且检查cloudprovider版本低于20.10.1
2. 请处于业务闲时进行更新
3. 确定您的UK8S版本，选择对应的更新操作

### 版本查看方法

请在web kubectl页面输入以下命令，可以查看当前集群使用的cloudprovider版本

```
kubectl describe deployment cloudprovider-ucloud -n kube-system |grep Image
```

### UK8S集群版本大于等于1.14

1. 请执行部署更新cloudprovider。

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/cloudprovider/20.10.2.yml
```

2. 检查是否部署成功，如Pod处于非running状态，请您及时与我们技术支持联系。

```
kubectl get pod -n kube-system -l app=cloudprovider-ucloud -o wide
```

### UK8S集群版本小于1.14

> 如您的集群master节点，执行`systemctl status ucloudcp`是运行状态的话，请务必在`3`个节点关闭二进制程序ucloudcp并更新。

1. 请分别登陆3台master节点，执行以下

```
systemctl stop ucloudcp
systemctl disable ucloudcp
```

2. 需要配置前置ConfigMap，请填写如下相关信息并保存文件为`userdata.yaml`。

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: uk8sconfig
  namespace: kube-system
data:
  UCLOUD_ACCESS_PRIKEY: xxxxxxxxxxxxxxx  #API PRIKEY
  UCLOUD_ACCESS_PUBKEY: xxxxxxxxxxxxxxx  #API_PUBKEY
  UCLOUD_API_ENDPOINT: http://api.service.ucloud.cn
  UCLOUD_PROJECT_ID: org-xxxxxx   #集群所在的项目ID
  UCLOUD_REGION_ID: cn-bj2  #集群所在的地域
  UCLOUD_SUBNET_ID: subnet-xxxxxx  #集群所在的子网ID
  UCLOUD_UK8S_CLUSTER_ID: uk8s-xxxxxx  #UK8S集群名称
  UCLOUD_VPC_ID: uvnet-xxxxxx   #集群所在的VPC ID
  UCLOUD_ZONE_ID: 'cn-bj2-03'   #集群master节点所在可用区，可用区列表参考：https://docs.ucloud.cn/api/summary/regionlist
```

3. 请执行创建ConfigMap。

```
kubectl apply -f userdata.yaml
```

4. 请执行部署cloudprovider。

```
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/cloudprovider/20.10.2.yml
```

5. 检查是否部署成功，如Pod处于非running状态，请您及时与我们技术支持联系。

```
kubectl get pod -n kube-system -l app=cloudprovider-ucloud -o wide
```
--->
