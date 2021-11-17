# 故障现象

在Uk8s服务控制台, 集群应用中心，日志ELK页面,开启集群日志插件,使用一段时间后，遇到故障现象如下:
1. 日志ELK,日志查询页面无最新日志
![](./images/log/plugin_ELK_problem_search_empty.png)

2. 日志ELK,组件状态页面显示最近10分钟日志总数 0 条
![](./images/log/plugin_ELK_problem_zero_items.png)
 
## 故障排查参考

**日志ELK默认部署在集群default命名空间,如果部署在自定义命名空间，执行命令请替换default名称**
 
* 查看logstash组件日志, 登录集群master节点，执行命令:`kubectl logs -f uk8s-elk-release-logstash-0 -n default`可见不断打印如下信息:
```
[2021-11-16T09:55:31,753][INFO ][logstash.outputs.elasticsearch] retrying failed action with response code: 403 ({"type"=>"cluster_block_exception", "reason"=>"index [uk8s-vidxqjoo-kube-system-2021.11.16] blocked by: [FORBIDDEN/12/index read-only / allow delete (api)];"})
[2021-11-16T09:55:31,753][INFO ][logstash.outputs.elasticsearch] Retrying individual bulk actions that failed or were rejected by the previous bulk request. {:count=>1}
```
* 查看ES组件存储卷使用率,登录集群master节点，执行命令: 
```
for pod in multi-master-0 multi-master-1 multi-master-2
do
  kubectl exec -t -i $pod -- sh -c 'df -h| grep /usr/share/elasticsearch/data' -n default
done
```
可以看到空间磁盘使用率高达96%
```
/dev/vdb         20G   19G  933M  96% /usr/share/elasticsearch/data
/dev/vdb         20G   19G  939M  96% /usr/share/elasticsearch/data
/dev/vdc         20G   19G  933M  96% /usr/share/elasticsearch/data
```
* 通过ES API 查询索引状态，登录集群master节点，执行命令:
```
ES_CLUSTER_IP=`kubectl get svc multi-master | awk 'NR>1 {print $3}'`
curl http://${ES_CLUSTER_IP}:9200/_all/_settings?pretty
```
可以看到返回信息中包含"read_only_allow_delete": "true" 从这里可以定位故障原因，虽然磁盘没有写满，但是触发了ES的保护机制：

- ES cluster.routing.allocation.disk.watermark.low，控制磁盘使用的低水位线（watermark） 默认值85%，超过后，es不会再为该节点分配分片;
- ES cluster.routing.allocation.disk.watermark.high，控制高水位线，默认值90%，超过后，将尝试将分片重定位到其他节点;
- ES cluster.routing.allocation.disk.watermark.flood_stage 控制洪泛水位线。默认值95%，超过后，ES集群将强制将所有索引都标记为只读，导致新增日志无法采集，无法查询最新日志,如需恢复，只能手动将 index.blocks.read_only_allow_delete 改成false.


# 参考处理方式

## 1. ES PVC扩容

**日志ELK默认部署在集群default命名空间,如果部署在自定义命名空间，执行命令请替换default名称**

* 登录集群master节点， 查看ES pod使用的pvc 执行命令:`kubectl get pvc -n default` 其中如下名字的pvc是ES使用的
```
multi-master-multi-master-0
multi-master-multi-master-1
multi-master-multi-master-2
```
执行 kubectl edit pvc pvc名字 -n default，将 spec.resource.requests.storage 的值调大，保存后退出，大概在一分钟左右，PV、PVC 以及容器内的文件系统就完成了在线扩容，详细操作参考[2.3在线扩容PVC](/uk8s/volume/expandvolume)。

扩容后参考检查步骤

* 确认 pv/pvc状态 kubectl get pv | grep multi-master && kubectl get pvc
* 解除ES索引只读模式
```
#!/bin/sh
ES_CLUSTER_IP=`kubectl get svc multi-master | awk 'NR>1 {print $3}'`
curl -H "Content-Type: application/json" -XPUT http://${ES_CLUSTER_IP}:9200/_all/_settings -d '{ "index.blocks.read_only_allow_delete": false }'
```
* 确认 ES集群状态

```
#!/bin/sh
ES_CLUSTER_IP=`kubectl get svc multi-master | awk 'NR>1 {print $3}'` 
curl http://${ES_CLUSTER_IP}:9200/_cat/allocation?pretty
curl http://${ES_CLUSTER_IP}:9200/_cat/health
curl http://${ES_CLUSTER_IP}:9200/_all/_settings | jq
```

## 2. 调整ES配置 

如果目前 ES PVC 容量非常大，按照ES默认配置 90% 存储依然剩余大量空余空间，可以调大ES参数阈值, 解除索引只读模式 , 将ES集群恢复至正常状态

```
#!/bin/sh
ES_CLUSTER_IP=`kubectl get svc multi-master | awk 'NR>1 {print $3}'`

curl -H "Content-Type: application/json" -XPUT http://${ES_CLUSTER_IP}:9200/_cluster/settings -d '{
  "persistent": {
    "cluster.routing.allocation.disk.watermark.low": "90%",
    "cluster.routing.allocation.disk.watermark.high": "95%",
    "cluster.routing.allocation.disk.watermark.flood_stage": "97%",
    "cluster.info.update.interval": "1m"
  }
}'
curl -H "Content-Type: application/json" -XPUT http://${ES_CLUSTER_IP}:9200/_all/_settings -d '{ 
  "index.blocks.read_only_allow_delete": false
}'
```
ES相关参数说明：

* cluster.routing.allocation.disk.watermark.low，控制磁盘使用的低水位线（watermark），它默认为85%，这意味着 Elasticsearch 不会将分片分配存储空间使用率超过85%的节点。它还可以设置为绝对字节值（如500MB），以防止 Elasticsearch 在可用空间少于指定数量时分配分片。此设置对新创建索引的主分片没有影响，特别是对以前从未分配过的任何分片。 
* cluster.routing.allocation.disk.watermark.high，控制高水位线，它默认为90%，这意味着 Elasticsearch 将尝试将分片从存储使用率高于90%的节点重新定位。它还可以设置为绝对字节值（类似于低水位线），以便在分片的可用空间小于指定数量时将其重新定位到远离节点的位置。此设置影响所有分片的分配，无论以前是否分配。
* cluster.routing.allocation.disk.watermark.flood_stage，控制洪泛水位线。它默认为95%，一旦有一个ES节点存储空间超过了洪泛阶段 Elasticsearch 将对索引块强制执行只读设置 index.blocks.read_only_allow_delete: true 这是防止节点耗尽存储空间的最后手段。一旦有足够的空间允许索引操作继续，则必须手动调整 index.blocks.read_only_allow_delete: false 取消索引只读属性。
