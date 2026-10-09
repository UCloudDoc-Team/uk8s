# 使用GPU节点

可通过以下方式在UK8s中使用GPU云主机作为集群节点：

- [创建集群](#创建集群)
- [新增Node节点](#新增Node节点)
- [添加已有主机](#添加已有主机)

## 镜像说明

在UK8s集群中使用GPU云主机作为节点时，可选择以下标准镜像。

| 标准镜像名   | Nvidia驱动版本 | CUDA版本 |
|--------------|----------------|----------|
| Ubuntu 24.04 | 595.71.05      | 13.2     |
| Ubuntu 22.04 | 595.71.05      | 13.2     |
| Rocky 9.7    | 595.71.05      | 13.2     |

## 创建集群

创建集群时，在Node节点配置中，选择机型为“GPU型G”，然后选择具体的GPU卡型及配置。
  ![](/images/gpu/image-0.png)

## 新增Node节点

在已有集群中新增Node节点时，选择机型为“GPU型G”，然后选择具体的GPU卡型及配置。
![](/images/gpu/image-1.png)

## 添加已有主机

将已创建的GPU云主机添加进已有集群，选择合适的节点镜像。
![](/images/gpu/image-2.png)

## 使用说明

1. 默认情况下，GPU 资源以整卡为单位分配给容器，每个容器可以申请一个或多个 GPU，不支持申请部分 GPU 资源。
2. UK8S 集群的 Master 节点暂不支持 GPU 机型。
3. UK8S 提供的标准 GPU 节点镜像已预装 NVIDIA 驱动，并且，集群默认部署 nvidia-device-plugin 组件，GPU 节点加入集群后可以被自动识别和注册。
4. 如何验证GPU节点的正常使用：
    - 查看节点是否具有`nvidia.com/gpu`的资源。
    ![](/images/gpu/image-3.png)
    - 运行如下示例使用`nvidia.com/gpu`资源类型请求 NVIDIA GPU，并查看日志结果是否正确。
```yaml
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  restartPolicy: Never
  containers:
    - name: cuda-container
      image: uhub.service.ucloud.cn/uk8s/cuda-sample:vectoradd-cuda12.5.0-ubi8
      resources:
        limits:
          nvidia.com/gpu: 1 # requesting 1 GPU
  tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule
EOF
```

```bash
$ kubectl logs gpu-pod
[Vector addition of 50000 elements]
Copy input data from the host memory to the CUDA device
CUDA kernel launch with 196 blocks of 256 threads
Copy output data from the CUDA device to the host memory
Test PASSED
Done
```

5. GPU云主机NCCL TOPO文件透传pod

   如果在GPU pod内NCCL性能测试没有达到理想值，考虑从虚机上把topology.xml文件透传到pod内；具体操作如下：
   > 前提：您的node为8卡高性价比显卡6/高性价比显卡6pro/A800/等GPU

   1. 确认GPU node `/var/run/nvidia-topologyd/` 路径下是否存在 `virtualTopology.xml`文件
     - 若存在执行第2步
     - 若不存在请咨询技术支持，将提供您该文件，拷贝文件保存至GPU node的 `/var/run/nvidia-topologyd/virtualTopology.xml`后执行第2步
   2. gpu-pod.yaml添加以下内容

```yaml
    containers:
      volumeMounts:
      - mountPath: /var/run/nvidia-topologyd
        name: topologyd
        readOnly: true
    volumes:
    - name: topologyd
      hostPath:
        path: /var/run/nvidia-topologyd
        type: Directory
```

## 插件升级

将 nvidia-device-plugin 升级到最新版本，以解决 GPU 节点不稳定的情况。

### 升级方法

- 方法一：使用 `kubectl set image` 将 `nvidia-device-plugin-daemonset` 的镜像版本更改为 `v0.20.1`：

    ```bash
    $ kubectl set image daemonset nvidia-device-plugin-daemonset -n kube-system nvidia-device-plugin-ctr=uhub.service.ucloud.cn/uk8s/nvidia-k8s-device-plugin:v0.20.1
    daemonset.apps/nvidia-device-plugin-daemonset image updated
    ```

- 方法二：更改 `nvidia-device-plugin-daemonset` 的 yaml 文件：
    1. 输入如下指令：

        ```bash
        kubectl edit daemonset nvidia-device-plugin-daemonset -n kube-system
        ```

    2. 此时会得到 `nvidia-device-plugin-daemonset` 的配置，找到 `spec.template.spec.containers.image` 后，可以看到目前镜像信息：

        ```yaml
        - image: uhub.service.ucloud.cn/uk8s/nvidia-k8s-device-plugin:v0.14.1
        ```

    3. 更改镜像为 `uhub.service.ucloud.cn/uk8s/nvidia-k8s-device-plugin:v0.20.1`，随后保存。

## 裸金属云主机绑核

目前裸金属云主机默认支持绑核，在某些场景下绑核提高GPU效率。

通过删除裸金属节点文件"/var/lib/kubelet/cpu_manager_state"，且默认配置`Kubelet`如下参数来支持绑核功能；相关官方文档可参考[Topology Manager Policy](https://kubernetes.io/docs/tasks/administer-cluster/topology-manager/)，[CPU Mangaer Policy](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/)

```
  --cpu-manager-policy=static \
  --topology-manager-policy=best-effort \
```

节点是否配置了支持绑核的参数，可登录节点，通过以下命令检查相关参数：

```
ps -aux|grep kubelet|grep topology-manager-policy 
```

### 验证绑核成功

1. 创建测试 Pod

    创建前，请根据目标裸金属节点调整以下配置：
    - 将 CPU、内存和 GPU 的 `requests` 与对应的 `limits` 设置为相同值，且 CPU 数量必须为整数，以满足 CPU 独占分配的条件。
    - 将 `spec.nodeName` 设置为目标节点的名称，可通过 `kubectl get nodes` 查看；如果节点以 IP 地址命名，则填写该 IP 地址。

    以下示例申请 10 个逻辑 CPU、10 GiB 内存和 1 张 GPU，运行 3600 秒的测试：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dcgmproftester
spec:
  nodeName: "10.60.159.170" # 这里替换为裸金属节点的ip
  restartPolicy: OnFailure
  containers:
  - name: dcgmproftester
    image: uhub.service.ucloud.cn/uk8s/dcgm:3.3.0
    command: ["/usr/bin/dcgmproftester12"]
    args: ["--no-dcgm-validation", "-t 1004", "-d 3600"] # 这里 -d 为运行时间
    resources: # 根据机器配置修改数值
      limits:  # limits与requests保持一致
        nvidia.com/gpu: 1
        memory: 10Gi
        cpu: 10
      requests:
        nvidia.com/gpu: 1
        memory: 10Gi
        cpu: 10
    securityContext:
      capabilities:
        add: ["SYS_ADMIN"]
```

2. 等待 Pod 状态为 `Running` 之后，通过 SSH 登录裸金属节点。

3. 获取容器主进程 PID

    在目标裸金属节点上查看容器列表：

    ```bash
    crictl ps
    ```

    找到名称为 `dcgmproftester` 的容器，记录其容器 ID，然后获取容器主进程的 PID：

    ```bash
    crictl inspect <容器ID> | jq -r '.info.pid'
    ```

4. 检查容器 CPU 亲和性

    使用上一步获取的 PID，查看容器主进程允许运行的 CPU 列表：

    ```bash
    taskset -c -p <PID>
    ```

    示例输出：

    ```text
    pid 9070's current affinity list: 1-5,65-69
    ```
    
    该进程允许运行在逻辑 CPU `1-5,65-69` 上，共 10 个，与 Pod 申请的 CPU 数量一致，表明进程的 CPU 运行范围已按预期受到限制。

5. 确认测试进程使用的 GPU

    在目标裸金属节点上执行以下命令，查看 GPU 设备及进程信息：

    ```bash
    nvidia-smi
    ```

    输出如下：

    ```bash
    ...
    +-----------------------------------------------------------------------------------------+
    | Processes:                                                                              |
    |  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
    |=========================================================================================|
    |    3   N/A  N/A           9110      C   /usr/bin/dcgmproftester12               782MiB |
    +-----------------------------------------------------------------------------------------+
    ```

    在输出的 Processes 区域，可以查看各 GPU 上运行的进程及其显存使用情况。

    从示例中可以看到，dcgmproftester12 进程正在使用 GPU3，说明测试工作负载已成功使用该 GPU 设备。

6. 验证 CPU 与 GPU 的 NUMA 亲和性

   检查 GPU 和 CPU 是否在同一个 NUMA 节点上：

   ```bash
   nvidia-smi topo -m
   ```

   输出如下：

    ```
            GPU0  GPU1  GPU2  GPU3  GPU4  GPU5  GPU6  GPU7  CPU Affinity    NUMA Affinity  GPU NUMA ID
    GPU0     X    SYS   SYS   SYS   SYS   SYS   SYS   SYS   24-31,88-95     3              N/A
    GPU1    SYS    X    SYS   SYS   SYS   SYS   SYS   SYS   16-23,80-87     2              N/A
    GPU2    SYS   SYS    X    SYS   SYS   SYS   SYS   SYS   8-15,72-79      1              N/A
    GPU3    SYS   SYS   SYS    X    SYS   SYS   SYS   SYS   0-7,64-71       0              N/A
    GPU4    SYS   SYS   SYS   SYS    X    SYS   SYS   SYS   56-63,120-127   7              N/A
    GPU5    SYS   SYS   SYS   SYS   SYS    X    SYS   SYS   48-55,112-119   6              N/A
    GPU6    SYS   SYS   SYS   SYS   SYS   SYS    X    SYS   40-47,104-111   5              N/A
    GPU7    SYS   SYS   SYS   SYS   SYS   SYS   SYS    X    32-39,96-103    4              N/A
    ```

   从输出结果可以看到，GPU3 对应的 CPU 亲和性范围为 `0-7,64-71`，而第 4 步中获取的容器主进程 CPU 亲和性范围为 `1-5,65-69`。

   容器主进程允许使用的 CPU 均位于 GPU3 对应的 CPU 亲和性范围内，说明 CPU 与 GPU 的 NUMA 亲和性配置符合预期。

7. Best-effort 策略补充说明
  
    使用 `best-effort` 策略时，需要提前了解使用的裸金属配置以决定 Pod 申请 CPU 和 GPU 的参数设置。
    
    例如现在有一台裸金属云主机配置如下：

    | CPU | GPU | 内存 (不影响绑核) | NUMA 节点数量 |
    | --- | --- | --- | --- |
    | 128 | 8 | 1024 | 8 |

    > CPU 和 NUMA 参数可以通过指令 `lscpu` 获取。GPU 参数可以通过指令 `nvidia-smi topo -m` 获取。

    通过指令 `lscpu` 我们可以得知 NUMA 节点和 CPU 核心的关系：
    ```bash
    ...
    NUMA node0 CPU(s):               0-7,64-71
    NUMA node1 CPU(s):               8-15,72-79
    NUMA node2 CPU(s):               16-23,80-87
    NUMA node3 CPU(s):               24-31,88-95
    NUMA node4 CPU(s):               32-39,96-103
    NUMA node5 CPU(s):               40-47,104-111
    NUMA node6 CPU(s):               48-55,112-119
    NUMA node7 CPU(s):               56-63,120-127
    ...
    ```

    通过指令 `nvidia-smi topo -m` 可以得知 NUMA 节点和 GPU 的关系：

    ```
            GPU0  GPU1  GPU2  GPU3  GPU4  GPU5  GPU6  GPU7  CPU Affinity    NUMA Affinity  GPU NUMA ID
    GPU0     X    SYS   SYS   SYS   SYS   SYS   SYS   SYS   24-31,88-95     3              N/A
    GPU1    SYS    X    SYS   SYS   SYS   SYS   SYS   SYS   16-23,80-87     2              N/A
    GPU2    SYS   SYS    X    SYS   SYS   SYS   SYS   SYS   8-15,72-79      1              N/A
    GPU3    SYS   SYS   SYS    X    SYS   SYS   SYS   SYS   0-7,64-71       0              N/A
    GPU4    SYS   SYS   SYS   SYS    X    SYS   SYS   SYS   56-63,120-127   7              N/A
    GPU5    SYS   SYS   SYS   SYS   SYS    X    SYS   SYS   48-55,112-119   6              N/A
    GPU6    SYS   SYS   SYS   SYS   SYS   SYS    X    SYS   40-47,104-111   5              N/A
    GPU7    SYS   SYS   SYS   SYS   SYS   SYS   SYS    X    32-39,96-103    4              N/A
    ```

    可以看出每个 NUMA 节点包含了 16 核 CPU 和 1 个 GPU。为了可以确保 CPU 和 GPU 都亲和相同的 NUMA 节点，我们的配置需要保证 **GPU 亲和的 NUMA 节点数量等于 CPU 亲和的 NUMA 节点数量，否则可能导致亲和节点不一致**。下面是能够实现亲和的情况：

    | GPU | CPU |
    | --- | --- |
    | 1 | 1 ~ 16 |
    | n | > 16 * (n-1), 且 ≤ 16 * n |

    > 这里的 16 和 1 是根据上文的方法查看配置得到的。不同机器的配置是不一样的，需要自行查看。

    除了以上 GPU/CPU 配比，其他情况均无法达到 NUMA 亲和的效果。

    具体可参考[官方文档](https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/topology-manager/)
