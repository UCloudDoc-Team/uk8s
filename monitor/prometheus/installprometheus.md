{{indexmenu_n>0}}
## 部署Prometheus

### 前言

对于一套Kubernetes集群而言，需要监控的对象大致可以分为以下几类：

* **Kubernetes系统组件：**Kubernetes内置的系统组件一般有apiserver、controller-manager、etcd、kubelet等，为了保证集群正常运行，我们需要实时知晓其当前的运行状态。

* **底层基础设施：** Node节点(虚拟机或物理机)的资源状态、内核事件等。

* **Kubernetes对象：** 主要是Kubernetes中的工作负载对象，如Deployment、DaemonSet、Pod等。

* **应用指标：** 应用内部需要关心的数据指标，如httpRequest。

### 部署Prometheus

1. 创建Namespace，为了管理方便，我们将Prometheus单独部署在一个Namespace下。

```
kubectl create ns monitoring
```

2. 创建ConfigMap，为Prometheus server创建配置文件，配置监控源，可根据业务情况自行修改。

```
kubectl apply -f http://uk8s.cn-bj.ufileos.com/yaml%2Fmonitor%2Fprometheus-server-conf.yaml
```

3. 创建ConfigMap，配置各种告警规则。

```
kubectl apply -f http://uk8s.cn-bj.ufileos.com/yaml%2Fmonitor%2Fprometheus-mointor-rules-conf.yaml
```
4. 声明一个PVC，用于Prometheus server的存储。

```
kubectl apply -f http://uk8s.cn-bj.ufileos.com/yaml%2Fmonitor%2Fprometheus-pvc-claim.ymal
```

5. 使用Deployment部署Prometheus，副本数为1。

```
kubectl apply -f http://uk8s.cn-bj.ufileos.com/yaml%2Fmonitor%2Fprometheus-deployment.yaml
```

6. 将Prometheus暴露到集群外部

```
kubectl apply -f http://uk8s.cn-bj.ufileos.com/yaml%2Fmonitor%2Fprometheus-service.yaml

```

7. 获取service外部访问地址，访问Prometheus管理页面

```
kubectl get svc -n monitoring
NAME                 TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)          AGE
prometheus-service   LoadBalancer   172.17.146.124   106.75.8.140   8080:39823/TCP   75m
```

选择targets，查看所有采集任务，状态为UP表示采集正常。
![](/images/monitor/prometheus/pro_good.jpg)

### 配置文件说明

在前面部署Prometheus时，我们创建了两个ConfigMap，下面我们简要说明下两个ConfigMap的作用。

1. Prometheus-server 配置文件

该Yaml主要用于声明需要Scape的jobs，如kubernetes-apiservers、ETCD等，其中ETCD这个jobs采用了静态配置的方式，你可以通过kubectl edit 修改其内容，让Prometheus能正常pull到ETCD的监控指标。

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-server-conf
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 5s
      evaluation_interval: 5s
    rule_files:
      - "/etc/prometheus-rules/*.yml"
    alerting:
      alertmanagers:
        - static_configs:
          - targets:
            - 'monitor-alertmanager.monitoring.svc:9093'
    scrape_configs:
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
        - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
        - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
          action: keep
          regex: default;kubernetes;https
     …….
      ………
      - job_name: 'master_etcd'
        scheme: https
        tls_config:
          insecure_skip_verify: true
          cert_file: /etcd-ssl/tls.crt
          key_file: /etcd-ssl/tls.key
        static_configs:
        - targets:
          - '10.9.2.106:2379'
          labels:
            app: 'master_etcd'
            hostname: '10.9.2.106'
        - targets:
          - '10.9.67.161:2379'
          labels:
            app: 'master_etcd'
            hostname: '10.9.67.161'  
        - targets:
          - '10.9.39.98:2379'
          labels:
            app: 'master_etcd'
            hostname: '10.9.39.98'

```

2. prometheus-mointor-rules-conf配置文件

该配置文件主要用于配置一些告警规则，如示例中的node cpu告警等。

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: monitor-prometheus-rules-config
  namespace: monitoring
data:
  node.rules.yml: |
    groups:
    - name: node.rules
      rules:
      - record: instance:node_cpu:rate:sum
        expr: sum(rate(node_cpu{mode!="idle",mode!="iowait"}[3m]))
          BY (instance)
      - record: instance:node_filesystem_usage:sum
        expr: sum((node_filesystem_size{mountpoint="/"} - node_filesystem_free{mountpoint="/"}))
          BY (instance)

      - record: instance:node_network_receive_bytes:rate:sum
        expr: sum(rate(node_network_receive_bytes[3m])) BY (instance)

      - record: instance:node_network_transmit_bytes:rate:sum
        expr: sum(rate(node_network_transmit_bytes[3m])) BY (instance)

      - record: instance:node_cpu:ratio
        expr: sum(rate(node_cpu{mode!="idle",mode!="iowait"}[5m])) WITHOUT (cpu, mode) / ON(instance)
          GROUP_LEFT() count(sum(node_cpu) BY (instance, cpu)) BY (instance)

      - record: cluster:node_cpu:sum_rate5m
        expr: sum(rate(node_cpu{mode!="idle",mode!="iowait"}[5m]))

      - record: cluster:node_cpu:ratio
        expr: cluster:node_cpu:rate5m / count(sum(node_cpu) BY (instance, cpu))
      - alert: NodeExporterDown
        expr: up{app="monitor-node-exporter"} != 1
        for: 3m
        labels:
          severity: warning
        annotations:
          description: '{{$labels.hostname}} {{$labels.instance}}'
          summary: A2 | Node-Exporter down

      ……
     ……………..
 
```
