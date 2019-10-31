## 获取集群信息-DescribeUK8SCluster

获取某个集群的详细信息

### Request Parameters
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Region|string|所属区域|**Yes**|
|ProjectId|string|项目id|No|
|ClusterId|string|k8s集群ID|**Yes**|


### Response Elements
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|RetCode|int|操作返回码|**Yes**|
|Action|string|操作名称|**Yes**|
|ClusterName|string|资源名字|**Yes**|
|ClusterId|string|集群ID|**Yes**|
|VPCId|string|所属VPC|**Yes**|
|SubnetId|string|所属子网|**Yes**|
|ServiceCIDR|string|ClusterIP网段,仅用于集群内部|**Yes**|
|PodCIDR|string|Pod网段，与集群所属子网相同|**Yes**|
|MasterList|array|Master节点配置信息，具体参考UhostInfo|**Yes**|
|MasterCount|string|Master 节点数量|**Yes**|
|NodeList|array|Node节点配置信息,具体参考UhostInfo|No|
|NodeCount|int|Node节点数量|No|
|CreateTime|int|创建时间|No|
|ApiServer|string|集群apiserver地址|No|
|ExternalApiServer|string|集群外部apiserver地址|No|
|Status|string|状态|No|
|UpdateTime|int|更新时间|No|

### UhostInfo
节点配置信息
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Zone|string|所在机房|**Yes**|
|Name|string|主机名称|**Yes**|
|CPU|int|Cpu数量|**Yes**|
|Memory|int|内存|**Yes**|
|IPSet|array|节点IP信息|**Yes**|
|DiskSet|array|节点磁盘信息|**Yes**|
|NodeId|string|节点ID|**Yes**|
|Image|string|镜像信息|**Yes**|
|CreateTime|int|创建时间|**Yes**|
|ExpireTime|int|到期时间|**Yes**|
|State|string|主机状态|**Yes**|
|NodeType|string|节点类型：uhost表示云主机;uphost表示物理云主机|**Yes**|

### IPSet
节点的IP信息

|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Type|string|国际: Internation，BGP: Bgp，内网: Private|No|
|IPId|string|IP资源ID (内网IP无对应的资源ID)|No|
|IP|string|IP地址|No|
|Bandwidth|int|IP对应的带宽, 单位: Mb (内网IP不显示带宽信息)|No|
|Default|string|是否默认的弹性网卡的信息。true: 是默认弹性网卡；其他值：不是。|No|

### DiskSet
节点磁盘信息
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Type|string|磁盘类型。系统盘: Boot，数据盘: Data,网络盘：Udisk|No|
|DiskId|string|磁盘长ID|No|
|Name|int|UDisk名字（仅当磁盘是UDisk时返回）|No|
|Drive|string|磁盘盘符|No|
|Size|int|磁盘大小，单位: GB|No|
|BackupType|string|备份方案，枚举类型：BASIC_SNAPSHOT,普通快照；DATAARK,方舟。无快照则不返回该字段。|No|
|IOPS|int|当前主机的IOPS值|No|
|DiskShortId|string|磁盘短ID|No|
|Encrypted|string|Yes: 加密 No: 非加密|No|
|DiskType|string|LOCAL_NOMAL| CLOUD_NORMAL| LOCAL_SSD| CLOUD_SSD|EXCLUSIVE_LOCAL_DISK|No|
|IsBoot|string|True| False|No|

### Request Example
```
https://api.ucloud.cn/?Action=DescribeUK8SCluster
&Region=zfXlbPNP
&Zone=dSenpJQB
&ClusterID=kCvoCLjV
```
### Response Example
```
{
    "RetCode": 0,
    "Action": "DescribeUK8SClusterResponse",
    "ExternalApiServer": "GVZVJyHy"
}
```
