## 添加节点（物理云主机）-AddUK8SPHostNode

为UK8S集群添加物理云主机节点

### Request Parameters
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Zone|string|可用区|**Yes**|
|ProjectId|string|项目ID|No|
|Region|string|地域|**Yes**|
|ClusterId|string|集群ID|**Yes**|
|Count|int|节点数量（不超过10台）|**Yes**|
|Password|string|节点密码|**Yes**|
|ChargeType|string|付费方式|**Yes**|
|Quantity|int|购买时长。默认: 1。按小时购买(Dynamic)时无需此参数。 月付时，此参数传0，代表了购买至月末。|No|
|Labels|string|key=value,多组用”,“隔开，最多5组|No|
|MaxPods|int|默认110|No|
|Type|string|物理机类型，默认为：DB-2(基础型-SAS-V3)|No|
|Raid|string|Raid配置，默认Raid10 支持:Raid0、Raid1、Raid5、Raid10，NoRaid|No|
|NIC|string|网络环境，可选千兆：1G ，万兆：10G， 默认1G|No|


### Response Elements
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|RetCode|int|操作返回码|**Yes**|
|Action|string|操作名称|**Yes**|
|Message|string||**Yes**|

### Request Example
```
https://api.ucloud.cn/?Action=AddUK8SPHostNode
&Zone=mASwhOwS
&ProjectId=TtFuuCvl
&Region=ephfLtkg
&ClusterId=gCCKbTeA
&CPU=7
&Count=3
&Password=UiYvduOo
&Mem=2
&ChargeType=wmcAhsnG
&BootDiskType=zmNhZzRf
&DataDiskType=GKVjMCWI
&DataDiskSize=fAJBjatE
&Quantity=8
&MachineType=hYudGdxE
&MinmalCpuPlatform=pXPBzsJd
&GpuType=ilPxSGRq
&GPU=9
&Labels=JUQASjlI
&Kubelet.MaxPods=1
&Type=qxQEPxPH
&Raid=ypSBWSeV
&NIC=gzqVBNpS
&Type=fTtSpRXy
&Raid=iUVCnclz
&NIC=YctuhWeH
```
### Response Example
```
{
    "Message": "ovAEHXng",
    "RetCode": 0,
    "Action": "AddUK8SPHostNodeResponse"
}
```
