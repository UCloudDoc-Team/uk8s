{{indexmenu_n>0}}
## 使用ELK自建UK8S日志解决方案

下面我们介绍下如何使用Elasticsearch+Filebeat+Kibana来搭建UK8S日志解决方案。


### 一、部署Elasticsearch

#### 1、关于Elasticsearch

Elasticsearch（ES）是一个基于Lucene构建的开源、分布式、RESTful接口的全文搜索引擎。Elasticsearch还是一个分布式文档数据库，其中每个字段均可被索引，而且每个字段的数据均可被搜索，ES能够横向扩展至数以百计的服务器存储以及处理PB级的数据。可以在极短的时间内存储、搜索和分析大量的数据。通常作为具有复杂搜索场景情况下的核心发动机

#### 2、环境要求

Elasticsearch运行时要求vm.max_map_count内核参数必须大于262144，因此开始之前需要确保这个参数正常调整过。
```
sysctl -w vm.max_map_count=262144
```
也可以在ES的的编排文件中增加一个initContainer来修改内核参数，但这要求kublet启动的时候必须添加了--allow-privileged参数，uk8s默认开启了该参数，在后面的示例中采用initContainer的方式。

#### 3、ES节点角色

ES的节点Node可以分为几种角色：

Master-eligible node，是指有资格被选为Master节点的Node，可以统称为Master节点。设置node.master: true

Data node，存储数据的节点，设置方式为node.data: true。

Ingest node，进行数据处理的节点，设置方式为node.ingest: true。

Trible node，为了做集群整合用的。

对于单节点的Node，默认是master-eligible和data，对于多节点的集群，需要根据需求仔细规划每个节点的角色。

#### 4、Elasticsearch部署

为了方便演示，我们把本文所有的对象资源都放置在一个名为 elk 的 namespace 下面，所以我们需要添加创建一个 namespace：
```
kubectl create namespace elk
```
**不区分节点角色**

这种模式下，集群中的节点不做角色的区分，配置文件请参考[elk-cluster.yaml](https://github.com/quchenyuan/uk8s-app/blob/master/elk/elk-cluster.yaml)

```
bash-4.4# kubectl apply -f elk-cluster.yaml
deployment.apps/kb-single created
service/kb-single-svc created
statefulset.apps/es-cluster created
service/es-cluster-nodeport created
service/es-cluster created
bash-4.4# kubectl get po -n elk
NAME                         READY   STATUS    RESTARTS   AGE
es-cluster-0                 1/1     Running   0          2m18s
es-cluster-1                 1/1     Running   0          2m15s
es-cluster-2                 1/1     Running   0          2m12s
kb-single-69ddfc96f5-lr97q   1/1     Running   0          2m18s
bash-4.4# kubectl get svc -n elk
NAME                  TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)                         AGE
es-cluster            ClusterIP      None            <none>         9200/TCP,9300/TCP               2m20s
es-cluster-nodeport   NodePort       172.17.177.40   <none>         9200:31200/TCP,9300:31300/TCP   2m20s
kb-single-svc         LoadBalancer   172.17.129.82   117.50.40.48   5601:38620/TCP                  2m20s
bash-4.4#

```
通过kb-single-svc的EXTERNAL-IP，便可以访问Kibana。

**区分节点角色**

如果需要区分节点的角色，就需要建立两个StatefulSet部署，一个是Master集群，一个是Data集群。Data集群的存储示例中简单使用了emptyDir，可以根据需要使用localStorage或者hostPath，关于存储的介绍，可以参考[Kubernetes官网](https://kubernetes.io/docs/concepts/storage/)。这样就可以避免Data节点在本机重启时发生数据丢失而重建索引，但是如果发生迁移的话，如果想保留数据，只能采用共享存储的方案了。具体的编排文件在这里[elk-role-cluster.yaml](https://github.com/quchenyuan/uk8s-app/blob/master/elk/elk-role-cluster.yaml)

```
bash-4.4# kubectl apply -f elk-role-cluster.yaml
deployment.apps/kb-single created
service/kb-single-svc created
statefulset.apps/es-cluster created
statefulset.apps/es-cluster-data created
service/es-cluster-nodeport created
service/es-cluster created
bash-4.4# kubectl get po -n elk
NAME                         READY   STATUS    RESTARTS   AGE
es-cluster-0                 1/1     Running   0          53s
es-cluster-1                 1/1     Running   0          50s
es-cluster-2                 1/1     Running   0          47s
es-cluster-data-0            1/1     Running   0          53s
es-cluster-data-1            1/1     Running   0          50s
es-cluster-data-2            1/1     Running   0          47s
kb-single-69ddfc96f5-lxsn8   1/1     Running   0          53s
bash-4.4# kubectl get statefulset -n elk
NAME              READY   AGE
es-cluster        3/3     2m
es-cluster-data   3/3     2m
bash-4.4# kubectl get svc -n elk
NAME                  TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)                         AGE
es-cluster            ClusterIP      None            <none>         9200/TCP,9300/TCP               44s
es-cluster-nodeport   NodePort       172.17.63.138   <none>         9200:31200/TCP,9300:31300/TCP   44s
kb-single-svc         LoadBalancer   172.17.183.59   117.50.92.74   5601:32782/TCP 

```

### 二、部署FileBeat

在进行日志收集的过程中，我们首先想到的是使用Logstash，因为它是ELK stack中的重要成员，但是在测试过程中发现，Logstash是基于JDK的，在没有产生日志的情况单纯启动Logstash就大概要消耗500M内存，在每个Pod中都启动一个日志收集组件的情况下，使用logstash有点浪费系统资源，因此我们更推荐一个轻量级的日志采集工具Filebeat，经测试单独启动Filebeat容器大约只会消耗12M内存。
具体的编排文件可以参考[filebeat.yaml](https://github.com/quchenyuan/uk8s-app/blob/master/elk/filebeat.yaml)，本例采用DaemonSet的方式编排。

```
bash-4.4# kubectl apply -f filebeat.yaml
configmap/filebeat-config created
daemonset.extensions/filebeat created
clusterrolebinding.rbac.authorization.k8s.io/filebeat created
clusterrole.rbac.authorization.k8s.io/filebeat created
serviceaccount/filebeat created
```

编排文件中将filebeat使用到的配置ConfigMap挂载到/home/uk8s-filebeat/filebeat.yaml，实际启动filebeat时使用该自定义配置。有关filebeat的配置可以参见 [Configuring Filebeat](https://www.elastic.co/guide/en/beats/filebeat/current/configuring-howto-filebeat.html)中相应的说明。

Filebeat命令行参数可以参考 [Filebeat Command Reference](https://www.elastic.co/guide/en/beats/filebeat/current/command-line-options.html)，本例中使用到的参数说明如下：

* -c, --c FILE

> 指定Filebeat使用的配置文件，如果不指定则使用默认的配置文件/usr/share/filebeat/filebeat.yaml

* -d, --d SELECTORS

> 为指定的selectors打开调试模式， selectors是以逗号分隔的列表，-d "*" 表示对所有组件进行调试。在实际生产环境中请关闭该选项，初次配置时打开可以有效排错。

* -e, --e

> 指定日志输出到标准错误输出，关闭默认的syslog/file输出


### 三、部署Logstash（可选）

由于Filebeat对message的过滤功能有限，在实际生产环境中通常会结合logstash。这种架构中Filebeat作为日志收集器，将数据发送到Logstash，经过Logstash解析、过滤后，将其发送到Elasticsearch存储，并由Kibana呈献给用户。

#### 1、创建配置文件

创建Logstash的配置文件，可以参考[elk-log.conf](https://github.com/quchenyuan/uk8s-app/blob/master/elk/elk-log.conf)，更详细的配置信息见[Configuring Logstash](https://www.elastic.co/guide/en/logstash/current/configuration.html)。大部分Logstash配置文件都可以分为3部分：input, filter 和 output，示例配置文件中指定Logstash从Filebeat获取数据，并输出到Elasticsearch。

#### 2、根据配置文件创建一个名为elk-pipeline-config的ConfigMap，如下：

```
bash-4.4# kubectl create configmap elk-pipeline-config --from-file=elk-log.conf --namespace=elk
configmap/elk-pipeline created
bash-4.4# kubectl get configmap -n elk
NAME                  DATA   AGE
elk-pipeline-config   1      9s
filebeat-config       1      21m

```
#### 3、在K8S集群部署logstash。

编写 [logstash.yaml](https://github.com/quchenyuan/uk8s-app/blob/master/elk/logstash.yaml) ，在yaml文件中挂载之前创建的ConfigMap。需要注意的是，此处使用了logstash-oss镜像，关于oss和non-oss版本的区别请参考[链接](https://discuss.elastic.co/t/what-are-the-differences-between-the-kibana-oss-and-non-oss-build/152364)。

```
bash-4.4# kubectl apply -f logstash.yaml
deployment.extensions/elk-log-pipeline created
service/elk-log-pipeline created
bash-4.4# kubectl get po -n elk
NAME                                READY   STATUS    RESTARTS   AGE
elk-log-pipeline-55d64bbcf4-9v49w   1/1     Running   0          50m

```

#### 4、查看logstash是否正常工作，出现如下内容，则表明logstash正常工作

```
bash-4.4# kubectl logs -f elk-log-pipeline-55d64bbcf4-9v49w -n elk
[2019-03-19T08:56:03,631][INFO ][logstash.agent           ] Successfully started Logstash API endpoint {:port=>9600}
...
[2019-03-19T08:56:09,845][INFO ][logstash.inputs.beats    ] Beats inputs: Starting input listener {:address=>"0.0.0.0:5044"}
[2019-03-19T08:56:09,934][INFO ][logstash.pipeline        ] Pipeline started succesfully {:pipeline_id=>"main", :thread=>"#<Thread:0x77d5c9b5 run>"}
[2019-03-19T08:56:10,034][INFO ][org.logstash.beats.Server] Starting server on port: 5044

```

#### 5、修改 filebeat.yaml的output参数，将其输出指向Logstash

```
items:
- apiVersion: v1
  kind: ConfigMap
  metadata:
    ...
  data:
    filebeat.yml: |
     ...
      output.logstash:
        hosts: ["elk-log-pipeline:5044"]
     ...

```


### 四、收集应用日志

前面我们已经部署好了Filebeat用于采集应用日志，并将采集到的日志输出到Elasticsearch，下面我们以一个nginx应用为例，来测试日志能否正常采集、索引、展示。

#### 1、部署nginx应用

创建一个Nginx的部署和LoadBalancer服务，这样可以通过eip访问Nginx。配置文件请参考[nginx.yaml](https://github.com/quchenyuan/uk8s-app/blob/master/elk/nginx.yaml)，我们将Nginx访问日志的输出路径以hostPath的形式挂载到宿主的/var/log/nginx/路径下。


```
bash-4.4# kubectl apply -f nginx.yaml
deployment.apps/nginx-deployment unchanged
service/nginx-cluster configured
bash-4.4# kubectl get svc -n elk nginx-cluster
NAME            TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)          AGE
nginx-cluster   LoadBalancer   172.17.153.144   117.50.25.74   5680:48227/TCP   19m
bash-4.4# kubectl get po -n elk -l app=nginx
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-6c858858d5-7tcbx   1/1     Running   0          36m
nginx-deployment-6c858858d5-9xzh8   1/1     Running   0          36m


```

#### 2、Filebeat配置

在之前部署Filebeat时，由于我们已经将/var/log/nginx/加入到inputs.paths中，Filebeat已经可以对nginx的日志实现监控采集。

```
 filebeat.modules:
      - module: system
      filebeat.inputs:
      - type: log
        paths:
          - /var/log/containers/*.log
          - /var/log/messages
          - /var/log/nginx/*.log
          - /var/log/*
        symlinks: true
        include_lines: ['hyperkube']
      output.logstash:
        hosts: ["elk-log-pipeline:5044"]
      logging.level: info
      index: filebeat-
```

#### 3、通过公网访问nginx服务，产生访问日志

![](/images/log/nginx.png)

#### 4、通过Kibana验证日志的采集情况

![](/images/log/kibana.png)







