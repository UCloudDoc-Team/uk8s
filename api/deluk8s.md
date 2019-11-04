# 删除集群-DelUK8SCluster

### Request Parameters
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Region|string|所属区域|**Yes**|
|ProjectId|string|项目id|No|
|ClusterId|string|集群id|**Yes**|


### Response Elements
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|RetCode|int|操作返回码|**Yes**|
|Action|string|操作名称|**Yes**|
|ErrMsg|string|错误说明|**Yes**|

### Request Example
```
https://api.ucloud.cn/?Action=DelUK8SCluster
&Region=gySoehip
&Zone=fhfpHbDR
&ClusterID=GGNfKAhZ
&ProjectID=JwRrSANU
```
### Response Example
```
{
    "RetCode": 0,
    "Action": "DelUK8SClusterResponse"
}
```
