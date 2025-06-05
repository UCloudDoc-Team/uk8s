# Cluster Autoscaler

## 前言

Cluster Autoscaler（CA）用于自动调整集群中Node节点的数量，以满足业务需求。

我们知道，在创建Pod的时候，我们可以为每个容器指定CPU、内存、GPU等资源的请求量(Request)，Kubernetes的调度组件(scheduler)会通过Request来判断将Pod调度到哪个Node节点。如果集群内没有节点有足够的空闲余量，则该Pod将无法被成功创建，而是一直处于Pending状态，直到有新的Node节点加入集群或者存量Pod被删除释放出空闲余量。

CA组件查找无法被成功调度的Pod，并遍历伸缩组，判断通过伸缩组模版扩容的新节点是否满足要求，如果判断新加节点可以使得Pod被成功调度，则CA将扩容集群。

CA组件同样也会缩容集群，缩容的触发条件为某个Node节点的Request请求率低于缩容阈值，不过缩容并不是马上进行的，而是等待一段时间（目前默认是10分钟），可以通过--scale-down-unneeded-time这个参数来修改。

和HPA不同，CA不是内置的，而是以Deployment的形式运行在Kubernetes集群中，UK8S已支持CA，你可以在UK8S的管理界面中配置CA。

## 工作原理

CA的扩容触发条件为**存在因为集群资源不足导致无法成功创建的Pod**，这里的资源包括**CPU、内存和GPU**。以GPU为例，当Pod申请了GPU资源`nvidia.com/gpu`（参考[GPU节点使用文档](/uk8s/administercluster/gpu-node)），但因集群中无GPU节点而处于pending状态时，CA就会在配置了GPU机型模版的伸缩组中自动扩容节点。

CA的缩容触发条件为**node节点在一定时间内（默认10分钟）资源请求率（Request）低于缩容阈值（如50%）且节点上的所有Pod都能被调度到其他节点上**。

值得注意的是**节点上的所有Pod都能被调度到其他节点**这个条件，很多配置了CA的同学会疑问某节点资源申请量低于阈值却没有触发缩容，原因其实很简单，如果这个节点上运行了一个独立的Pod（没有被任何控制器管理），因为Pod无法被重新调度，为了保证业务正常运行，则节点的缩容不会进行。

## 在UK8S中使用集群伸缩

#### 1、创建伸缩配置

![](/images/administercluster/autoscaling/wechatworkscreenshot_120eae74-0e91-463b-8c78-20c513f2c0a9.png)

#### 2、填写配置参数

一般默认值即可 ![](/images/administercluster/autoscaling/2.png)


#### 3、创建伸缩组

伸缩组中配置了触发集群扩容时，Node节点的配置；其中伸缩区间指节点最大与最小的扩容机器数。最大值主要用于防范因为DDos等导致的无限制扩容。


![](/images/administercluster/autoscaling/3.png)

#### 4、开启集群伸缩

创建完伸缩组后，我们之后还需要开启伸缩组，点击开启操作后，你的UK8S集群会出现一个Cluster-Autoscaler的Deployment，如果手动删除该Deployment，会导致集群伸缩无法正常工作，您需要在集群伸缩页面先关闭，再开启以触发重新创建。

![](/images/administercluster/autoscaling/4.png)

## CA参数说明

CA本身有很多命令参数，可以调整伸缩的一些行为。可以通过更改CA deployment的`args`参数来调整。

下面是一些CA参数以及说明：

| 参数                          | 类型     | 默认值          | 说明                                   |
| ----------------------------- | -------- | --------------- | -------------------------------------- |
| scale-down-delay-after-add    | Duration | 10min           | 扩容后进行缩容的延迟。                 |
| scale-down-delay-after-delete | Duration | 同scan-interval | 删除节点后进行缩容的延迟。             |
| scale-down-unneeded-time      | Duration | 10min           | 节点标记为unneeded之后，多久进行缩容。 |
| node-deletion-delay-timeout   | Duration | 2min            | CA等待节点删除完成的超时时间。         |
| scan-interval                 | Duration | 10s             | 多久进行一次扩缩容扫描。               |
| max-nodes-total               | int      | 0               | 最大扩容节点数量。                     |
| cores-total                   | String   | [0:32E+04]      | 集群的CPU核心扩缩容范围。              |
| memory-total                  | String   | [0:64E+05]      | 集群的内存扩缩容范围。                 |
