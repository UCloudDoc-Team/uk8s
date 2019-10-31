## 删除集群节点-DelUK8SClusterNode

删除集群中的节点

### Request Parameters
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|ProjectId|string|项目ID|No|
|Region|string||**Yes**|
|ClusterId|string|k8s集群ID|**Yes**|
|Name|string|节点名称|**Yes**|
|NodeId|string|节点ID|No|


### Response Elements
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|RetCode|int|操作返回码|**Yes**|
|Action|string|操作名称|**Yes**|

### Request Example
```
https://api.ucloud.cn/?Action=DelUK8SClusterNode
&ClusterID=lQjanthV
&NodeId=nwhWjeYw
&ProjectId=tUbUKHyg
&AzGroup=mXedDmgx
&NodeName=CJoXpVHg
```
### Response Example
```
{
    "RetCode": 0,
    "Action": "DelUK8SClusterNodeResponse"
}
```

