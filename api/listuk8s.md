## 获取集群列表-ListUK8SCluster

查看某地域下所有UK8S集群

### Request Parameters
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Region|string|所属区域|**Yes**|
|ProjectId|string|项目id|No|
|Offset|int|偏移量（默认为0）|No|
|Limit|int|数量（如果传0或者不传则默认为20）|No|


### Response Elements
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|RetCode|int|操作返回码|**Yes**|
|Action|string|操作名称|**Yes**|
|ClusterCount|int|集群数量|**Yes**|
|ClusterInfo|array[ClusterBaseInfo]|集群信息，具体参考ClusterBaseInfo|No|

### ClusterBaseInfo

集群基础信息

|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|ClusterId|string|集群id|**Yes**|
|ClusterName|string|集群名字|**Yes**|
|APIService|string|内网ApiServer地址|**Yes**|
|VPCId|string|所属VPC|**Yes**|
|SubnetId|string|所属子网|**Yes**|
|NodeCount|int|节点数量|**Yes**|
|CreateTime|int|创建时间，时间戳|**Yes**|
|Status|string|集群状态|**Yes**|

### Request Example
```
https://api.ucloud.cn/?Action=ListUK8SCluster
&Region=BMmKNTGm
&Zone=hueLNiYC
&ProjectID=isSspeFf
&Offset=5
&Limit=8
```
### Response Example
```
{
    "RetCode": 0,
    "Action": "ListUK8SClusterResponse"
}
```
