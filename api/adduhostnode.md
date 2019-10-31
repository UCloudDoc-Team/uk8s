## 添加节点（云主机）-AddUK8SUHostNode

为集群新增云主机节点

### Request Parameters
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Zone|string|可用区|**Yes**|
|ProjectId|string|项目ID|No|
|Region|string|地域|**Yes**|
|ClusterId|string|集群ID|**Yes**|
|CPU|int|节点CPU大小|**Yes**|
|Count|int|节点数量（不超过10台）|**Yes**|
|Password|string|节点密码|**Yes**|
|Mem|int|节点Mem大小|**Yes**|
|ChargeType|string|付费方式|**Yes**|
|BootDiskType|string|磁盘类型。请参考[[api:uhost-api:disk_type|磁盘类型]]。默认为SSD云盘|No|
|DataDiskType|string|磁盘类型。请参考[[api:uhost-api:disk_type|磁盘类型]]。默认为SSD云盘|No|
|DataDiskSize|string|数据磁盘大小，单位GB。默认0。范围 ：[20, 1000]|No|
|Quantity|int|购买时长。默认: 1。按小时购买(Dynamic)时无需此参数。 月付时，此参数传0，代表了购买至月末。|No|
|MachineType|string|【新增】云主机机型（V2.0），枚举值["N", "C", "G"]。|No|
|MinmalCpuPlatform|string|最低cpu平台，枚举值["Intel/Auto", "Intel/IvyBridge", "Intel/Haswell", "Intel/Broadwell", "Intel/Skylake", "Intel/Cascadelake"。|No|
|GpuType|string|GPU类型，枚举值["K80", "P40", "V100"]|No|
|GPU|int|GPU卡核心数。仅GPU机型支持此字段|No|
|Labels|string|key=value,多组用”,“隔开，最多5组|No|
|MaxPods|int|默认110|No|
|IsolationGroup|string|隔离组Id|No|


### Response Elements
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|RetCode|int|操作返回码|**Yes**|
|Action|string|操作名称|**Yes**|
|Message|string||**Yes**|

### Request Example
```
https://api.ucloud.cn/?Action=AddUK8SUHostNode
&Zone=HjafOmlI
&ProjectId=QhySZaWP
&Region=ofGfDPlB
&ClusterId=PDncjlGz
&NodeCpu=3
&NodeNum=4
&Password=immkVITW
&NodeMem=4
&ChargeType=GLtOpVbU
&NodeUHostType=fjbWacib
&NodeBootDiskType=BcUliGXM
&NodeDataDiskType=HkETvOPs
&NodeDataDiskSize=axIciunR
&NodeDiskType=kFeAdCpF
&NodeDiskSize=5
&Quantity=2
&MachineType=MpjsOzvE
&MinmalCpuPlatform=mdRRKIma
&GpuType=PaxzMqMa
&GPU=cXzHPXgm
&Labels=vUeEMXvc
&Kubelet.MaxPods=8
&IsolationGroup=wuiIQmnd
```
### Response Example
```
{
    "Message": "XcuSztKl",
    "RetCode": 0,
    "Action": "AddUK8SUHostNodeResponse"
}
```
