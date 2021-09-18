## 插件相关问题

UK8S通过Kubernetes提供的CNI、CSI、CCM接口整合了UCloud云资源，当你在创建Kubernetes对象（如Pod、PVC、LoadBalancer的Service）时，可能会遇到以下类型的报错，下面详细描述下相关报错的意义及其解决办法。



### 一、Pod相关错误及解决办法

Pod创建时，需要调用AllocatableSecondaryIP，为Pod分配一个VPC IP，当Pod无法启动时，通过kubectl describe pod/$pod-name，查看该Pod的events是否出现相关错误码。


|错误码|错误码意义|解决办法|
|-------|-------------|----------|
|172|授权给UK8S的账号被注销或删除，导致调用API失败|为UK8S集群授权新的账号并修改现有集群节点的账号配置信息|
|173|授权给UK8S的账号被限制、冻结，导致调用API失败|联系UCloud技术支持将账号解冻，或者请主账号管理者确认该子账号是否被删除。|
|294|贵司主账号开启了API访问白名单，导致UK8S的插件调用UCloud其他云产品API被拒绝|请主账号所有者在API白名单处添加10.10.10.10|


### 二、PVC相关错误及解决办法


当你通过UK8S创建底层存储介质为UDisk或Ufile的PVC时，UK8S的CSI插件将使用授权账号调用UDisk或UFile API创建云资源，当你发现PVC一直处于Pending状态时，可通过kubectl describe pvc/$pvc-name，查看该PVC的events是否出现相关错误码。

|错误码|错误码意义|解决办法|
|-------|-------------|----------|
|172|主账号被注销或删除，导致调用API失败|
|173|授权给UK8S的子账号被限制、冻结|联系主账号
|240|贵司主账号没有该产品权限，或该可用区无该产品|联系客户经理开启产品权限或更换产品类型，比如某个可用区无SSD类型的UDisk，可改换SATA类型的UDisk|
|291|授权给UK8S的子账号权限不足，无该产品操作权限|请主账号管理者为授权给UK8S的子账号授予UDisk的增删改查权限|
|294|开启了api访问白名单，导致uk8s的插件调用ucloud其他云产品api被拒绝|请主账号管理者在API白名单处添加10.10.10.10|
|520|账户余额不足|充值|



### 三、Service相关错误及解决办法

当你通过UK8S创建LoadBalancer类型的Service时，UK8S的CCM插件将使用授权账号调用ULB的API接口管理ULB，当你发现Service的External-IP一直处于Peding状态时，可通过kubectl describe service/$service-name，查看该Service的events是否出现相关错误码。

|错误码|错误码意义|解决办法|
|-------|-------------|----------|
|172|主账号被注销或删除，导致调用API失败|
|173|授权给UK8S的子账号被限制、冻结|联系主账号
|240|贵司主账号没有该产品权限，或该可用区无该产品|联系客户经理开启产品权限或更换产品类型，比如某个可用区无SSD类型的UDisk，可改换SATA类型的UDisk|
|291|授权给UK8S的子账号权限不足，无该产品操作权限|请主账号管理者为授权给UK8S的子账号授予UDisk的增删改查权限|
|294|开启了api访问白名单，导致uk8s的插件调用ucloud其他云产品api被拒绝|请主账号管理者在API白名单处添加10.10.10.10|
|520|账户余额不足|充值|
