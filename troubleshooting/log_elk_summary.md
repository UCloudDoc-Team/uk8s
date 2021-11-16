# 故障现象

Elasticsearch 配置 cluster.routing.allocation.disk.watermark.low* 控制磁盘空间使用的默认配置是90%，磁盘使用率超过阈值，ES集群中的所有索引都标记为只读，导致新增日志无法采集，无法查询最新日志。

# 参考处理方式

## 1. ES PVC扩容

```
kubectl edit pvc multi-master-multi-master-0
kubectl edit pvc multi-master-multi-master-1
kubectl edit pvc multi-master-multi-master-2
```
详细操作参考[2.3在线扩容PVC](https://docs.ucloud.cn/uk8s/volume/expandvolume)

扩容后
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

如果目前 ES PVC 容量非常大，按照ES默认配置 95% 存储依然剩余大量空余空间，可以调大ES参数阈值, 解除索引只读模式 , 将ES集群恢复至正常状态

```
#!/bin/sh
ES_CLUSTER_IP=`kubectl get svc multi-master | awk 'NR>1 {print $3}'`

curl -H "Content-Type: application/json" -XPUT http://${ES_CLUSTER_IP}:9200/_cluster/settings -d '{
  "persistent": {
    "cluster.routing.allocation.disk.watermark.low": "94%",
    "cluster.routing.allocation.disk.watermark.high": "96%",
    "cluster.routing.allocation.disk.watermark.flood_stage": "98%",
    "cluster.info.update.interval": "1m"
  }
}'
curl -H "Content-Type: application/json" -XPUT http://${ES_CLUSTER_IP}:9200/_all/_settings -d '{ 
  "index.blocks.read_only_allow_delete": false
}'
```
