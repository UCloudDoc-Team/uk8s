## 1. 故障现象

在 UK8S 服务控制台, 集群应用中心，日志 ELK 页面,开启集群日志插件,使用一段时间后，遇到故障现象如下:

1. 日志 ELK,日志查询页面无最新日志

![](/images/log/plugin_ELK_problem_search_empty.png)

2. 日志ELK,组件状态页面显示最近10分钟日志总数 0 条

![](/images/log/plugin_ELK_problem_zero_items.png)

## 2. 故障排查参考

**日志 ELK 默认部署在集群 default 命名空间,如果部署在自定义命名空间，执行命令请替换 default 名称**

step 1. 查看 logstash 组件日志, 登录集群master节点，执行命令:
`kubectl logs -f uk8s-elk-release-logstash-0 -n default` 可见不断打印如下信息:

```
[2021-11-16T09:55:31,753][INFO ][logstash.outputs.elasticsearch] retrying failed action with response code: 403 ({"type"=>"cluster_block_exception", "reason"=>"index [uk8s-vidxqjoo-kube-system-2021.11.16] blocked by: [FORBIDDEN/12/index read-only / allow delete (api)];"})
[2021-11-16T09:55:31,753][INFO ][logstash.outputs.elasticsearch] Retrying individual bulk actions that failed or were rejected by the previous bulk request. {:count=>1}
```

step 2. 查看ES组件存储卷使用率,登录集群master节点，执行命令:

```bash
for pod in multi-master-0 multi-master-1 multi-master-2
do
  kubectl exec -t -i $pod -- sh -c 'df -h| grep /usr/share/elasticsearch/data' -n default
done
```

可以看到空间磁盘使用率高达 96%

```bash
/dev/vdb         20G   19G  933M  96% /usr/share/elasticsearch/data
/dev/vdb         20G   19G  939M  96% /usr/share/elasticsearch/data
/dev/vdc         20G   19G  933M  96% /usr/share/elasticsearch/data
```

step 3. 通过ES API 查询索引状态，登录集群 master 节点，执行命令:

```bash
ES_CLUSTER_IP=`kubectl get svc multi-master | awk 'NR>1 {print $3}'`
curl http://${ES_CLUSTER_IP}:9200/_all/_settings?pretty
```

可以看到返回信息中包含 `"read_only_allow_delete": "true"` 从这里可以定位故障原因，虽然磁盘没有写满，但是触发了ES的保护机制：

- ES cluster.routing.allocation.disk.watermark.low，控制磁盘使用的低水位线（watermark） 默认值85%，超过后，es不会再为该节点分配分片;
- ES cluster.routing.allocation.disk.watermark.high，控制高水位线，默认值90%，超过后，将尝试将分片重定位到其他节点;
- ES cluster.routing.allocation.disk.watermark.flood_stage
  控制洪泛水位线。默认值95%，超过后，ES集群将强制将所有索引都标记为只读，导致新增日志无法采集，无法查询最新日志,如需恢复，只能手动将
  index.blocks.read_only_allow_delete 改成false.

## 3. 参考处理方式

## 3.1 ES PVC 扩容

**日志 ELK 默认部署在集群 default 命名空间，如果部署在自定义命名空间，执行命令请替换 default 名称**

Step 1. 登录集群 Master 节点， 执行命令:`kubectl get pvc -n default` 查看 PVC，其中如下名字的 PVC 是 ES 使用的

```bash
multi-master-multi-master-0
multi-master-multi-master-1
multi-master-multi-master-2
```

执行 `kubectl edit pvc {pvc-name} -n default`，将 `spec.resource.requests.storage`
的值调大，保存后退出，大概在一分钟左右，PV、PVC 以及容器内的文件系统就完成了在线扩容，详细操作参考[UDisk 动态扩容](/uk8s/volume/expandvolume)。

扩容后确认 PV/PVC 状态：`kubectl get pv | grep multi-master && kubectl get pvc | grep multi-master`

Step 2. 解除 ES 索引只读模式

```bash
ES_CLUSTER_IP=`kubectl get svc multi-master | awk 'NR>1 {print $3}'`
curl -H "Content-Type: application/json" -XPUT http://${ES_CLUSTER_IP}:9200/_all/_settings -d '{ "index.blocks.read_only_allow_delete": false }'
```

Step 3. 确认 ES集群状态

```bash
ES_CLUSTER_IP=`kubectl get svc multi-master | awk 'NR>1 {print $3}'` 
curl http://${ES_CLUSTER_IP}:9200/_cat/allocation?pretty
curl http://${ES_CLUSTER_IP}:9200/_cat/health
curl http://${ES_CLUSTER_IP}:9200/_all/_settings | jq
```

## 3.2 调整 ES 配置 

如果目前 ES PVC 容量非常大，按照 ES 默认配置 90% 存储依然剩余大量空余空间，可以调大 ES 参数阈值, 解除索引只读模式 , 将 ES 集群恢复至正常状态

```bash
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

## 3.3 ES 相关参数说明：

- cluster.routing.allocation.disk.watermark.low，控制磁盘使用的低水位线（watermark），它默认为 85%，这意味着 Elasticsearch
  不会将分片分配存储空间使用率超过 85% 的节点。它还可以设置为绝对字节值（如 500MB），以防止 Elasticsearch
  在可用空间少于指定数量时分配分片。此设置对新创建索引的主分片没有影响，特别是对以前从未分配过的任何分片。
- cluster.routing.allocation.disk.watermark.high，控制高水位线，它默认为 90%，这意味着 Elasticsearch 将尝试将分片从存储使用率高于
  90% 的节点重新定位。它还可以设置为绝对字节值（类似于低水位线），以便在分片的可用空间小于指定数量时将其重新定位到远离节点的位置。此设置影响所有分片的分配，无论以前是否分配。
- cluster.routing.allocation.disk.watermark.flood_stage，控制洪泛水位线。它默认为 95%，一旦有一个 ES 节点存储空间超过了洪泛阶段
  Elasticsearch 将对索引块强制执行只读设置 index.blocks.read_only_allow_delete: true
  这是防止节点耗尽存储空间的最后手段。一旦有足够的空间允许索引操作继续，则必须手动调整 index.blocks.read_only_allow_delete: false 取消索引只读属性。

参考：[Elasticsearch 官方文档](https://github.com/elastic/elasticsearch/tree/master/docs)


## 4. ES 内存扩容
### 调整内存参考
> **注意: 日志 ELK 默认部署在集群 default 命名空间,如果部署在自定义命名空间，请替换相应命名空间名称**
#### 前置条件
本参考适用于基于 UK8S 自建日志服务的场景。请确保以下条件已满足：

+ 已在 **“UK8S 控制台 > 详情 > 应用中心 > 日志 ELK”** 中开启服务，且安装类型为 **“新建”**。
+ 可通过以下命令确认服务状态是否正常

```plain
kubectl get sts multi-master -n default
```

若命令返回结果中未出现 `error`，则表示服务运行正常。

#### 修改内存配置
```plain
kubectl patch sts multi-master -n default --patch '
spec:
  template:
    spec:
      containers:
      - name: elasticsearch
        env:
        - name: ES_JAVA_OPTS
          value: "-Xmx4g -Xms4g"
        resources:
          limits:
            memory: "8Gi"
'
```

+ `-Xmx4g -Xms4g`：将堆内存的最大值和初始值都设置为 4GB，你可以根据实际情况将其替换为 2g、3g 等其他数值。请确保最大值和初始值相同,使 JVM 在启动时就一次性分配固定大小的堆内存，避免运行期间动态扩缩带来的 GC 抖动问题。
+ `limits.memory: "8Gi"`：调整后，无论 Elasticsearch 是否有实际负载，JVM 都会一次性申请并保留与配置相同大小的堆内存。因此，容器的最大可用内存应设置为堆内存大小的 2～3 倍，以确保操作系统、线程栈、缓存和 off-heap 内存有足够的可用空间，避免 OOM（内存溢出）问题。
+ 无需修改 `requests`，除非你也希望调整资源预留，以便更好地与调度策略匹配。
+ **注意：`ES_JAVA_OPTS` 中设置的堆内存大小必须小于 `limits.memory`，同时 `limits.memory` 必须小于节点（宿主机）总内存，否则可能导致 OOM 或调度失败。**

#### 重启ElasticSearch
```shell
kubectl rollout restart sts multi-master -n default
```

#### 生效检测
```shell
kubectl exec -it multi-master-0 -n default -- curl -s http://multi-master:9200/_nodes/stats/jvm?pretty   | grep -E '"heap_used_in_bytes"|"heap_max_in_bytes"|"heap_used_percent"'
```

#### 示例输出
```plain
          "heap_used_in_bytes" : 1731749680,
          "heap_used_percent" : 40,
          "heap_max_in_bytes" : 4294967296,
          "heap_used_in_bytes" : 1786740736,
          "heap_used_percent" : 41,
          "heap_max_in_bytes" : 4294967296,
          "heap_used_in_bytes" : 2153311232,
          "heap_used_percent" : 50,
          "heap_max_in_bytes" : 4294967296,
```

+ `heap_used_in_bytes`：当前堆内存使用量（字节数）。
+ `heap_max_in_bytes`：堆内存的最大可用内存（字节数）。`4294967296` → 4GB（`-Xmx4g`）
+ `heap_used_percent`：堆内存使用的百分比。

至此，我们已经详细介绍了如何调整 Elasticsearch 集群的堆内存大小，涵盖了从修改内存配置到验证生效的各个步骤。通过合理的内存配置，可以显著提升 Elasticsearch 的性能和稳定性，确保其在大规模数据处理时依然高效运行。调整配置时要牢记内存大小的匹配规则，并注意集群资源的整体分配。
