## 集群日志调整ElasticSearch内存大小
### 前言
Elasticsearch 作为一个分布式搜索与分析引擎，对内存资源尤其敏感。JVM 堆内存（heap size）的配置直接影响到系统的查询性能、索引吞吐量及节点的稳定性。随着数据规模的增长和业务需求的变化，固定的内存配置可能无法满足集群的实际运行需求。因此，了解并掌握如何合理调整 Elasticsearch 的内存大小，是保障系统高可用性与性能的关键步骤。本文将围绕 JVM 堆内存的调整进行说明，涵盖判断依据、配置方法及注意事项等内容，为运维和开发人员提供参考。

### 调整内存参考
> **注意: 日志 ELK 默认部署在集群 default 命名空间,如果部署在自定义命名空间，请替换相应命名空间名称**
>

#### 前置条件
本教程适用于基于 UK8S 自建日志服务的场景。请确保以下条件已满足：

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

+ `-Xmx4g -Xms4g`：将堆内存上限和初始值设置为 4GB，你可以根据实际需求替换为 2g、3g 等其他数值。
+ `limits.memory: "8Gi"`：设置容器可用的最大内存限制，通常建议为 heap size 的 2～3 倍。
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
