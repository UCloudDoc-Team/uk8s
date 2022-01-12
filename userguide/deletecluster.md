## 删除集群

你可以通过控制台直接删除现有集群，此操作为不可逆操作，请谨慎执行。

如果您在使用过程中创建过PVC、LoadBlancer类型的Service，UK8S会替代你创建UDisk、ULB等资源。建议你删除集群之前，把集群内部的Workloads、Services先删除掉，避免集群删除后，由K8S创建的一些资源依然产生费用。

![](/images/userguide/delete.png)
