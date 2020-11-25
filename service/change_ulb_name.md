# ULB属性修改的处理方法

> 如没有实际需要，请避免修改ULB名称及注释

根据cloudprovider插件[使用提醒](/uk8s/service/externalservice?id=_1%e3%80%81%e4%bd%bf%e7%94%a8%e6%8f%90%e9%86%92)，由UK8S cloudprovider创建的ULB不允许修改ULB名称，如果您修改过ULB名称，可以参考以下操作进行关联，避免影响线上业务。

## 操作方法

1. 修改UK8S集群中的service注释，**以下注释仅限由UK8S创建的ULB添加**。

```yaml
# 增加ULB-id进行关联
service.beta.kubernetes.io/ucloud-load-balancer-id-provision: <ulb-id>  
```

2. 升级UK8S集群cloudprovider插件至最新版本。

    UK8S cloudprovider插件在20.10.1版本后已经默认支持关联ULB-id，避免用户修改ULB名称后影响cloudprovider重建ULB，[升级文档](/uk8s/introduction/vulnerability/cloudprovider)。
