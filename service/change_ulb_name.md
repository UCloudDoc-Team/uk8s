# ULB名称修改的处理方法

根据cloudprovider插件[使用提醒](https://docs.ucloud.cn/uk8s/service/externalservice?id=_1%e3%80%81%e4%bd%bf%e7%94%a8%e6%8f%90%e9%86%92)，由UK8S cloudprovider创建的ULB不允许修改ULB名称。

**如您在使用中的service-ULB修改过ULB名称,需要按照以下操作进行关联，否则可能导致service关联的ULB重建，影响线上业务。**

1. 修改UK8S集群中的service注释。

```yaml
# 增加ULB-id进行关联
service.beta.kubernetes.io/ucloud-load-balancer-id-provision: <ulb-id>  
```

2. 升级UK8S集群cloudprovider插件至最新版本。

    UK8S cloudprovider插件在20.10.1版本后已经默认支持关联ULB-id，避免用户修改ULB名称后影响cloudprovider重建ULB。升级文档[请查看](https://docs.ucloud.cn/uk8s/introduction/vulnerability/cloudprovider)

