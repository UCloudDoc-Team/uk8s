## 获取集群kubeconfig-GetClusterConfig

获取集群kubeconfig信息，kubeconfig为管理集群的凭证，一般保存为~/.kube/config。

### Request Parameters
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|ProjectId|string|所在项目|No|
|Region|string|所在区域|**Yes**|
|ClusterId|string|集群ID|**Yes**|


### Response Elements
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|RetCode|int|操作返回码|**Yes**|
|Action|string|操作名称|**Yes**|
|KubeConfig|string|内网ApiServer的集群凭证|**Yes**|
|ExternalKubeConfig|string|开启公网apiserver的情况下，有数据返回。|No|

### Request Example
```
https://api.ucloud.cn/?Action=GetClusterConfig
&AzGroup=OMHXXfyW
&Zone=cnWbQGjo
&ProjectID=ASjvFawh
&ClusterID=DywdxtWZ
```
### Response Example
```
{
    "RetCode": 0,
    "Action": "GetClusterConfigResponse",
    "ExternalKubeConfig": "PhycEJji"
}
```

