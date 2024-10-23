# GPU插件

## 1. 介绍
Uk8s 使用开源组件 [HAMi](https://github.com/Project-HAMi/HAMi) 实现GPU共享，包括：
- 显存划分
- 算力划分
- 错误隔离

## 2. 部署

 ⚠️ 安装前请检查系统需满足以下要求：
- **NVIDIA drivers**: 版本需不低于 `440`。
- **Kubernetes 版本**: 不低于 `1.16`。
- **glibc**: 版本需在 `2.17` 及以上，但低于 `2.3.1`。

### 2.1 将需要由 HAMi 调度的 GPU 节点打上标签：

```sh
kubectl label nodes xxx.xxx.xxx.xxx gpu=on
```

### 2.2 运行以下命令，创建安装文件

```bash
cat << 'EOF' > hami_setup.sh
#!/bin/bash
set -e
# Step 1: Install Helm
if ! command -v helm &> /dev/null
then
    echo "Helm not found, installing Helm..."
    # Add Helm's APT repository
    curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
    sudo apt install apt-transport-https --yes
    echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list

    # Update package list and install Helm
    sudo apt update
    sudo apt install helm -y
else
    echo "Helm is already installed."
fi
# Step 2: Download Helm Chart
echo "Adding hami-charts repository and pulling Helm Chart..."
helm repo add hami-charts https://project-hami.github.io/HAMi/
helm pull hami-charts/hami --untar
# Step 3: Modify image sources
VALUES_FILE="hami/values.yaml"
if [ -f "$VALUES_FILE" ]; then
    echo "Modifying image sources in values.yaml..."
    sed -i 's|registry\.cn-hangzhou\.aliyuncs\.com/google_containers/kube-scheduler|uhub.service.ucloud.cn/gpu-share/kube-scheduler|' $VALUES_FILE
    sed -i 's|imageTag: \"v1\.20\.0\"|imageTag: \"v1.26.7\"|' $VALUES_FILE
    sed -i 's|projecthami/hami|uhub.service.ucloud.cn/gpu-share/hami:fac239f|' $VALUES_FILE
    sed -i 's|liangjw/kube-webhook-certgen:v1.1.1|uhub.service.ucloud.cn/gpu-share/kube-webhook-certgen:v1.1.1|' $VALUES_FILE
    sed -i 's|projecthami/hami|uhub.service.ucloud.cn/gpu-share/hami:fac239f|' $VALUES_FILE
else
    echo "values.yaml not found!"
    exit 1
fi
# Step 4: Modify daemonsetnvidia.yaml
DAEMONSET_FILE="hami/templates/device-plugin/daemonsetnvidia.yaml"
if [ -f "$DAEMONSET_FILE" ]; then
    echo "Modifying daemonsetnvidia.yaml..."
    sed -i 's|image: {{ .Values.devicePlugin.image }}:{{ .Values.version }}|image: {{ .Values.devicePlugin.image }}|' $DAEMONSET_FILE
else
    echo "daemonsetnvidia.yaml not found!"
    exit 1
fi
# Step 5: Modify scheduler deployment
SCHEDULER_FILE="hami/templates/scheduler/deployment.yaml"
if [ -f "$SCHEDULER_FILE" ]; then
    echo "Modifying scheduler deployment.yaml..."
    sed -i 's|image: {{ .Values.scheduler.extender.image }}:{{ .Values.version }}|image: {{ .Values.scheduler.extender.image }}|' $SCHEDULER_FILE
else
    echo "deployment.yaml not found!"
    exit 1
fi
# Step 6: Install HAMi Helm Chart
echo "Installing HAMi Helm Chart..."
helm install hami ./hami -n kube-system
echo "HAMi installation completed. Please check the pod status using 'kubectl get pods -n kube-system'"
EOF

```

### 2.3 运行hami_setup.sh文件
```bash
chmod +x hami_setup.sh
sudo ./hami_setup.sh
```

### 2.4 检查安装结果
```sh
helm install hami ./hami -n kube-system
```

安装成功时，以下输出显示 Pod 运行状态：

```sh
hami-device-plugin-l4jj4                2/2     Running   0          45s
hami-scheduler-59c7f4b6ff-7g565         2/2     Running   0          3m54s
```
### 2.5 使用方法
通过YAML 文件来创建 Pod，注意 `resources.limit` 中，除了传统的 `nvidia.com/gpu` 外，增加了 `nvidia.com/gpumem` 和 `nvidia.com/gpucores` 等来指定显存大小和 GPU 算力。

- **nvidia.com/gpu**: 请求的 vGPU 数量，例如 `1`。
- **nvidia.com/gpumem**: 请求的显存大小，例如 `3000M`。
- **nvidia.com/gpumem-percentage**: 显存请求百分比，例如 `50` 表示请求 50% 的显存。
- **nvidia.com/gpucores**: 每个 vGPU 的算力占实际显卡的百分比。
- **nvidia.com/priority**: 优先级，`0` 表示高优先级，`1` 表示低优先级，默认为 `1`。

   - 对于**高优先级任务**，如果与其他高优先级任务共享 GPU 节点，则其资源利用率不会受到 `resourceCores` 的限制。换言之，当 GPU 节点上仅有高优先级任务时，它们可利用节点上所有可用的资源。
   - 对于**低优先级任务**，如果该任务是唯一占用 GPU 的任务，则其资源利用率同样不受 `resourceCores` 的限制。这意味着在无其他任务共享 GPU 的情况下，低优先级任务也可以利用节点上所有可用的资源。



## 3. 监控

### 3.1. 若未开启监控中心

开启 [监控中心](/uk8s/monitor/prometheusplugin/startmonitor) 

### 3.2. 若已开启监控中心

>  ⚠️ 如果监控中心版本 `1.0.6 > version >= 1.0.5-3` 或者 `version > 1.0.6` ，则默认安装了下面部署文件，请跳过`3.2.1`中的部署内容。

#### 3.2.1. 部署 Dcgm-Exporter
```sh
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/gpu-share/dcgm-exporter.yaml
```

#### 3.2.2. 在 uk8s 添加监控目标
在`uk8s-监控中心-监控目标`之中，按照图示的方式，在 uk8s 中添加监控目标。
![](/images/administercluster/gpu-share-monitor1.png)

### 3.3 Grafana监控
在 uk8s 添加监控目标登陆Grafana后，你需要先下载 [json 文件](https://uk8s-download.cn-bj.ufileos.com/hami-dcgm-gpu-share.json) --> 选择左侧导航栏 '+' 号 --> Import --> 第二个输入框粘贴下载的 json 内容 --> Load。

以下是Grafana监控HAMi的示意图：
![](/images/administercluster/gpu-share-monitor2.png)


### 3.4 监控指标
除了`DCGM插件`（在[GPU监控](/uk8s/administercluster/gpu-monitor)文档之中具体描述）之外的指标，HAMi还支持以下指标：
- **Device_memory_desc_of_container**：表示容器中设备内存的实时使用情况。用于监控每个容器的设备（如 GPU）内存消耗。

- **Device_utilization_desc_of_container**：表示容器设备的实时利用率。用于监控容器内部设备的使用情况，如 GPU 的工作负载。

- **HostCoreUtilization**：表示宿主机上核心的实时利用率。用于监控宿主机的 CPU 核心使用情况，可能包括容器或虚拟化的多个工作负载。

- **HostGPUMemoryUsage**：表示宿主机上 GPU 设备的实时内存使用情况。用于监控宿主机中使用 GPU 的各个容器或任务所消耗的内存。

- **vGPU_device_memory_limit_in_bytes**：表示某个容器的 vGPU（虚拟 GPU）设备内存的限制，单位是字节。这是该容器可以使用的最大 GPU 内存量。

- **vGPU_device_memory_usage_in_bytes**：表示某个容器的 vGPU 设备内存的实际使用量，单位是字节。用于监控该容器的 vGPU 内存使用情况。


## 4. 测试
### 4.1. Node GPU 资源验证
在测试环境中，物理 GPU 数量为 1，但由于 HAMi 默认配置扩容比例为 10 倍，因此理论上可以在 Node 上查看到 `1 * 10 = 10` 个 GPU。

#### 验证指令
执行以下命令获取 Node 的 GPU 资源量：

```sh
kubectl get node xxx -oyaml | grep capacity -A 8
```

得到的输出如下：

```yaml
capacity:
  cpu: "16"
  ephemeral-storage: 102687672Ki
  hugepages-1Gi: "0"
  hugepages-2Mi: "0"
  memory: 32689308Ki
  nvidia.com/gpu: "10"
  pods: "110"
  ucloud.cn/uni: "16"
```

### 4.2. GPU 显存测试
以下是 `gpu-mem-test.yaml` 的配置内容：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  containers:
    - name: ubuntu-container
      image: uhub.service.ucloud.cn/library/ubuntu:trusty-20160412
      command: ["bash", "-c", "sleep 86400"]
      resources:
        limits:
          nvidia.com/gpu: 1 # 请求1个vGPU
          nvidia.com/gpumem: 3000 # 每个vGPU申请3000MiB显存（可选，整数类型）
          nvidia.com/gpucores: 30 # 每个vGPU的算力为30%实际显卡的算力（可选，整数类型）
```

使用上述配置创建 Pod，Pod 应能正常启动，验证步骤如下：

```sh
kubectl get po
```

得到的输出：

```sh
NAME      READY   STATUS    RESTARTS   AGE
gpu-pod   1/1     Running   0          48s
```

进入 Pod 并执行 `nvidia-smi` 命令，查看 GPU 信息，可以验证到显存的限制为资源中申请的 `3000M`。



### 4.3. 多个 Pod 单个 GPU 利用率测试

#### 测试命令
首先创建 `hami-npod-1gpu.yml`，内容如下，请替换其中的 GPU 节点 IP，用于指定运行的 GPU 节点。

该配置创建了三个 Pod，建议测试完成后手动删除。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hami-npod-1gpu
spec:
  replicas: 3  # 创建三个相同的 Pod，可根据需要修改数量
  selector:
    matchLabels:
      app: pytorch
  template:
    metadata:
      labels:
        app: pytorch
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/hostname
                operator: In
                values:
                - xxx.xxx.xxx.xxx # 请替换为实际 GPU 节点 IP
      containers:
      - name: pytorch-container
        image: uhub.service.ucloud.cn/gpu-share/gpu_pytorch_test:latest
        command: ["/bin/sh", "-c"]
        args: ["cd /app/pytorch_code && python3 2.py"]
        resources:
          limits:
            nvidia.com/gpu: 1
            nvidia.com/gpumem: 3000
            nvidia.com/gpucores: 25
```

