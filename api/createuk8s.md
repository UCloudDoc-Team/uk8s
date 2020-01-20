## 创建集群-CreateUK8SClusterV2

创建UK8S集群，支持单可用区或多可用区模式，当3台Master均在同一个可用区则为单可用区模式，Node也只允许落在同一可用区。当3台Master分布在不同可用区时，务必确保不同可用区均有该机型，否则集群会创建失败（UK8S前端做了交集处理，确保不会出现此情况）。
UK8S的三台Master默认属于统一个硬件隔离组，确保高可用，Node可根据需要自行配置。
因为物理云主机启动时间较长，因此创建集群时不支持添加物理云主机，可在集群创建完毕后再添加物理云主机。


### Request Parameters
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|Region|string|地域。 参见 [地域和可用区列表](api/summary/regionlist)|**Yes**|
|ProjectId|string|项目ID，不填写为默认项目，子帐号必须填写。 参见[GetProjectList接口](api/summary/get_project_list)|No|
|VPCId|string|VPC ID|**Yes**|
|SubnetId|string|子网 ID|**Yes**|
|ServiceCIDR|string|Service CIDR，如172.16.0.1/16|**Yes**|
|K8sVersion|string|K8S集群版本；不指定的话默认为当前支持的最高版本，当前支持的版本请参考UK8S控制台|No|
|ClusterName|string|集群名称|**Yes**|
|ExternalApiServer|string|外网ApiServer，推荐开启，否则外网无法访问。开启：Yes 不开启：No。默认为No。|No|
|Master.1.Zone|string|可用区。参见 [可用区列表](api/summary/regionlist)|**Yes**|
|Master.2.Zone|string|可用区。参见 [可用区列表](api/summary/regionlist)|**Yes**|
|Master.0.Zone|string|可用区。参见 [可用区列表](api/summary/regionlist)|**Yes**|
|MasterMachineType|string|云主机机型（V2.0），枚举值["N", "C"]。参考[云主机机型说明](api/uhost-api/uhost_type)|**Yes**|
|MasterCPU|string|CPU核数。单位：C。范围：[2-64],可选值参照云主机|**Yes**|
|MasterMem|string|内存大小。单位：MB。范围 ：[4096, 262144]，取值为1024的倍数|**Yes**|
|MasterMinmalCpuPlatform|string|最低cpu平台，枚举值["Intel/Auto", "Intel/IvyBridge", "Intel/Haswell", "Intel/Broadwell", "Intel/Skylake", "Intel/Cascadelake"。]|No|
|MasterBootDiskType|string|建议为SSD云盘，请参考[磁盘类型](api/uhost-api/disk_type)。|**Yes**|
|MasterDataDiskType|string|请参考[磁盘类型](api/uhost-api/disk_type)|No|
|MasterDataDiskSize|string|数据磁盘大小，单位GB。默认0。范围 ：[20, 1000]|No|
|Nodes.N.Zone|string|可用区。参见 [可用区列表](api/summary/regionlist.html)|**Yes**|
|Nodes.N.MachineType|string|云主机机型（V2.0），枚举值["N", "C", "G","O"]。|**Yes**|
|Nodes.N.CPU|int|虚拟CPU核数。可选参数：2-64（具体机型与CPU的对应关系参照控制台）|**Yes**|
|Nodes.N.Mem|int|内存大小。单位：MB。范围 ：[4096, 262144]，取值为1024的倍数（可选范围参考控制台）|**Yes**|
|Nodes.N.MinmalCpuPlatform|string|最低cpu平台，枚举值["Intel/Auto", "Intel/IvyBridge", "Intel/Haswell", "Intel/Broadwell", "Intel/Skylake", "Intel/Cascadelake"。|No|
|Nodes.N.GpuType|string|GPU类型，枚举值["K80", "P40", "V100"]|No|
|Nodes.N.GPU|string|GPU核心数。仅GPU机型支持此字段，可选范围与MachineType+GpuType相关|No|
|Nodes.N.IsolationGroup|string|隔离组Id，参见DescribeIsolationGroup|No|
|Nodes.N.MaxPods|int|Node可运行最大节点数,默认为110|No|
|Nodes.N.Labels|string|key=value，多组Labels用”,“隔开,最多支持五组	|No|
|Nodes.N.BootDiskType|string|建议为SSD云盘，请参考[磁盘类型](api/uhost-api/disk_type)。|No|
|Nodes.N.DataDiskType|string|请参考[磁盘类型](api/uhost-api/disk_type)|No|
|Nodes.N.DataDiskSize|int|数据磁盘大小，单位GB。默认0。范围 ：[20, 1000]|No|
|Nodes.N.Count|int|一组Node的数量[1-10]，当配置了硬件隔离组时，该组Node数量请勿超过7台|**Yes**|
|Password|string|Master及Node节点的SSH登录密码|**Yes**|
|ChargeType|string|计费模式。枚举值为： Year，按年付费； Month，按月付费； Dynamic，按小时付费。默认按月|No|
|Quantity|string|购买时长。默认: 1。按小时购买(Dynamic)时无需此参数。 月付时，此参数传0，代表了购买至月末。默认1|No|

### Response Elements
|Parameter name|Type|Description|Required|
|------|------|--------|----:|
|RetCode|int|操作返回码|**Yes**|
|Action|string|操作名称|**Yes**|
|ClusterId|string|集群ID|**Yes**|

### Request Example
```
https://api.ucloud.cn/?Action=CreateUK8SClusterV2
&Region=cn-zj
&Zone=cn-zj-01
&ProjectId=DUYLbuwj
&VPCId=NIUbMRrP
&SubnetId=oWAtQljO
&ServiceCIDR=iXXMZpXs
&ClusterName=gcuwXSLm
&Password=vDsbRNNQ
&ChargeType=TrFaoDAK
&Quantity=PxBiAWAo
&K8sVersion=uxAueotm
&ExternalApiServer=vasrSAjn
&Master.1.zone=rwFzpSWL
&Master.2.zone=MuzxrYho
&Master.3.zone=blItdpQD
&MasterMachineType=rBCZRPYI
&MasterMinmalCpuPlatform=wJoUcbYp
&MasterCPU=oKqzqZZh
&MasterMem=hwUjKpoK
&MasterBootDiskType=jbQIKkul
&MasterDataDiskType=RmHtwyLG
&MasterDataDiskSize=NFuIPJcm
&Nodes.N.zone=hDtZnELL
&Nodes.N.MachineType=MMuaNZIl
&Nodes.N.MinmalCpuPlatform=uLWsDWDL
&Nodes.N.GpuType=mXrWwOLD
&Nodes.N.GPU=nRsbGDlh
&Nodes.N.CPU=CiNwWCeJ
&Nodes.N.Mem=ZgEuxdnu
&Nodes.N.BootDiskType=VQGewTRm
&K8sVersion=UOoiKtNm
&ExternalApiServer=RVgMWokk
&Master.1.zone=wXjbFYSU
&Master.2.zone=YvijQPFd
&Master.3.zone=CAIJnJEp
&MasterMachineType=SiECGsDX
&MasterMinmalCpuPlatform=kElumqZJ
&MasterCPU=ODBnDKWv
&MasterMem=IQKJEydV
&MasterBootDiskType=rqEFOgqz
&MasterDataDiskType=qCJOPxEF
&MasterDataDiskSize=tkpcQGJS
&Nodes.N.zone=aLzNslLv
&Nodes.N.MachineType=hCtXDpwx
&Nodes.N.MinmalCpuPlatform=hhfNYZAU
&Nodes.N.GpuType=lEgwfaMY
&Nodes.N.GPU=pXervTpu
&Nodes.N.CPU=TqeQgstN
&Nodes.N.Mem=AhdyTtIB
&Nodes.N.BootDiskType=ePIgbSGU
&Nodes.N.DataDiskType=jLNDJqhX
&Nodes.N.DataDiskSize=2
&Nodes.N.Counts=6
&Nodes.N.DataDiskType=OlCnwgED
&Nodes.N.DataDiskSize=1
&Nodes.N.Count=4
&Nodes.N.IsolationGroup=lRBbaDzS
&Nodes.N.MaxPods=3
&Nodes.N.Labels=CqzkeSQm
&MasterIsolationGroup=dDOFtdaB
```
### Response Example
```
{
    "ClusterId": "cFlgBOGW",
    "RetCode": 0,
    "Action": "CreateUK8SClusterV2Response"
}
```
