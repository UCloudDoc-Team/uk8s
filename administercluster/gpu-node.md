# 使用GPU节点

可通过以下方式在UK8s中使用GPU云主机作为集群节点：
- [创建集群](#创建集群)
- [新增Node节点](#新增Node节点)
- [添加已有主机](#添加已有主机)

## 镜像说明
在UK8s集群中使用**高性价比显卡**的云主机机型（如高性价比显卡3、高性价比显卡4、高性价比显卡5、高性价比显卡6）作为节点时，需使用标准镜像`Ubuntu 20.04-高性价比`。
- 高性价比显卡支持可用区
  - 华北二A
  - 上海二B
  - 北京二B

| 标准镜像名            | 适用显卡                                | Nvidia驱动版本 | CUDA版本 |
|-----------------------|-----------------------------------------|----------------|--------------|
| Ubuntu 20.04-高性价比 | 高性价比显卡（如高性价比显卡3/4/5/6等） | 550.120        | 12.4         |
| Ubuntu 20.04          | 非高性价比显卡（如T4、V100S、P40等）    | 550.90.12      | 12.4         |
| Centos 7.6            | 非高性价比显卡（如T4、V100S、P40等）    | 450.80.02      | 11.0         |

## 创建集群
创建集群时，在Node节点配置中，选择机型为“GPU型G”，然后选择具体的GPU卡型及配置。
  ![](/images/gpu/image.png)
注：如果选择了高性价比显卡，需要在节点镜像中使用标准镜像`Ubuntu 20.04-高性价比`。
  ![](/images/gpu/image-0.png)
## 新增Node节点
在已有集群中新增Node节点时，选择机型为“GPU型G”，然后选择具体的GPU卡型及配置。
![](/images/gpu/image-1.png)
## 添加已有主机
将已创建的GPU云主机添加进已有集群，选择合适的节点镜像。
![](/images/gpu/image-2.png)

## 使用说明
1. 默认情况下，容器之间不共享 GPU，每个容器可以请求一个或多个 GPU。无法请求 GPU 的一小部分。
2. 集群的 Master 节点暂不支持 GPU 机型。
3. UK8S提供的标准镜像中，已安装nvidia驱动，并且，集群中默认安装了`nvidia-device-plugin`组件，GPU资源添加到集群后可以被自动识别和注册。
4. 如何验证GPU节点的正常使用：
    1. 查看节点是否具有`nvidia.com/gpu`的资源。
![](/images/gpu/image-3.png)
    2. 运行如下示例使用`nvidia.com/gpu`资源类型请求 NVIDIA GPU，并查看日志结果是否正确。
    ```bash
    $ cat <<EOF | kubectl apply -f -
    apiVersion: v1
    kind: Pod
    metadata:
      name: gpu-pod
    spec:
      restartPolicy: Never
      containers:
        - name: cuda-container
          image: uhub.service.ucloud.cn/uk8s/cuda-sample:vectoradd-cuda10.2
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
- 方法一：使用 `kubectl set image` 将 `nvidia-device-plugin-daemonset` 的镜像版本更改为 `v0.14.1`：
    ```bash
    $ kubectl set image daemonset nvidia-device-plugin-daemonset -n kube-system nvidia-device-plugin-ctr=uhub.service.ucloud.cn/uk8s/nvidia-k8s-device-plugin:v0.14.1
    daemonset.apps/nvidia-device-plugin-daemonset image updated
    ```
- 方法二：更改 `nvidia-device-plugin-daemonset` 的 yaml 文件：
    1. 输入如下指令：
        ```bash
        $ kubectl edit daemonset nvidia-device-plugin-daemonset -n kube-system
        ```
    2. 此时会得到 `nvidia-device-plugin-daemonset` 的配置，找到 `spec.template.spec.containers.image` 后，可以看到目前镜像信息：
        ```yaml
        - image: uhub.service.ucloud.cn/uk8s/nvidia-k8s-device-plugin:1.0.0-beta4
        ```
    3. 更改镜像为 `uhub.service.ucloud.cn/uk8s/nvidia-k8s-device-plugin:v0.14.1`，随后保存。

## 裸金属云主机绑核
想要让裸金属云主机绑核，需要在主机加入 uk8s 集群前进行一些配置。

### 配置方法
1. 选择好裸金属云主机后，在【添加已有主机】界面的最底下点击【更多设置】。

    ![](/images/gpu/image-4.png)
2. 确保【禁用节点】已开启。

    ![](/images/gpu/image-5.png)
3. 在【初始化脚本】的输入框内加入绑核脚本：
    ```bash
    #!/bin/bash
    cp /etc/kubernetes/kubelet /etc/kubernetes/kubelet.backup
    sed -i 's/^"$/                --cpu-manager-policy=static \\\
                    --topology-manager-policy=best-effort \\\
    "/' /etc/kubernetes/kubelet
    rm /var/lib/kubelet/cpu_manager_state
    systemctl restart kubelet

    sleep 1
    KUBELET_STATUS=$(systemctl is-active kubelet)

    if [[ "$KUBELET_STATUS" == "activating" ]]; then
        for i in {1..10}; do
            sleep 1
            KUBELET_STATUS=$(systemctl is-active kubelet)
            if [[ "$KUBELET_STATUS" == "active" ]]; then
                rm /etc/kubernetes/kubelet.backup
                break
            fi
        done
    elif [[ "$KUBELET_STATUS" == "active" ]]; then
        rm /etc/kubernetes/kubelet.backup
    fi

    if [[ "$KUBELET_STATUS" != "active" ]]; then
        mv /etc/kubernetes/kubelet.backup /etc/kubernetes/kubelet
        systemctl restart kubelet
    fi
    ```
    点击确定后，等待节点添加完成。

4. 现在我们可以看到节点状态为 `Ready,SchedulingDisabled`。

    ![](/images/gpu/image-6.png)

    输入指令：`kubectl uncordon <节点名称>` 来让节点处于 `Ready` 的状态。

### 验证绑核成功

1. 创建测试 Pod 前，需要注意以下几点：
    - 确保 `limits` 和 `requests` 是一致的，不一致会导致绑核失败。
    - 因为 kubelet 预留 1 核 CPU，最多可以申请 `总核数 - 1` 核 CPU。
    - 可以将 `spec.nodeName` 设置为裸金属云主机的 ip 地址，确保 Pod 被调度到该节点上。
    - 在配置 Pod 的 CPU 和 GPU 请求大小时，推荐让 GPU 亲和的 numa 节点数量等于 CPU 亲和的 numa 节点数量。这里需要提前了解使用的裸金属配置以决定 Pod 申请 CPU 和 GPU 的参数设置。
      
      例如：现在有一台裸金属云主机配置如下：

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

      通过指令 `nvidia-smi topo -m` 我们可以得知 NUMA 节点和 GPU 的关系：

      ![](/images/gpu/image-11.png)

      可以看出每个 NUMA 节点包含了 16 核 CPU 和 1 个 GPU。为了可以确保 CPU 和 GPU 亲和都亲和相同的 NUMA 节点，我们的配置需要保证 **GPU 亲和的 numa 节点数量等于 CPU 亲和的 numa 节点数量，否则可能导致亲和节点不一致**。下面是几种情况：

      | CPU | GPU | 结果 |
      | --- | --- | --- |
      | 1 ~ 16 | 1 | 亲和同节点 |
      | > 16 | 1 | 亲和不同节点 |
      | 1 ~ 16 | > 1 | 亲和不同节点 |
      | (数量 / 16) = (GPU 数量 / 1) | (数量 / 1) = (CPU 数量 / 16) | 亲和同节点 |
      | (数量 / 16) ≠ (GPU 数量 / 1) | (数量 / 1) ≠ (CPU 数量 / 16) | 亲和不同节点 |
      > 计算全部向上取整。
      
      > 这里的 16 和 1 是根据上文的方法查看配置得到的。不同机器的配置是不一样的，需要自行查看。

    现在我们来创建 Pod：
    ```YAML
    apiVersion: v1
    kind: Pod
    metadata:
      name: dcgmproftester
    spec:
      nodeName: "10.60.159.170" # 这里替换为裸金属节点的ip
      restartPolicy: OnFailure
      containers:
      - name: dcgmproftester12-1
        image: uhub.service.ucloud.cn/uk8s/dcgm:3.3.0
        command: ["/usr/bin/dcgmproftester12"]
        args: ["--no-dcgm-validation", "-t 1004", "-d 3600"] # 这里 -d 为运行时间
        resources: # 这里的数值需要按照上文介绍的方法根据不同机器配置进行修改
          limits:
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

2. 等待 Pod 状态为 `Running` 之后，通过 ssh 进入裸金属节点内。

3. 输入指令 `crictl ps` 来获取当前节点内容器列表。根据创建时间或者容器名称找到我们刚刚创建的容器的 ID。

4. 输入指令 `crictl inspect <容器ID> | grep pid`，获取进程的 pid。

5. 如果设置 Pod 请求的 GPU 数量大于 1，输入指令 `ps -ef | grep <pid>`, 获取刚刚得到的 pid 的多个子进程：
    
    ![](/images/gpu/image-9.png)
  
    通过这张图，可以看出我们获取了 pid 为 66917 相关的进程信息。每一行 `root` 后的两个数字，第一个是子进程，第二个是父进程。那么我们就可以知道 24147 进程的子进程有两个：66952 和 66953。

6. 现在输入指令 `nvidia-smi` 来获取 gpu 信息，检查 GPU 亲和性：

    ![](/images/gpu/image-7.png)
    
    下方的 Process 框中记录了哪一个 GPU 在运行，图中为 GPU2 在运行。如果运行的是多 GPU，可以通过对比第 5 步得到的子进程 pid 查看到哪一个 GPU 在运行哪一个子进程。

7. 通过指令 `nvidia-smi topo -m` 来检查 GPU 和 CPU 是否在同一个 NUMA 节点上：

    ![](/images/gpu/image-8.png)

    输入指令 `taskset -c -p <pid>` 来获取 CPU 亲和性信息：

    ![](/images/gpu/image-10.png)
    
    我们可以看出 GPU2 的 CPU Affinity 为 `0-7,64-71`。进程的 CPU Affinity list 为 `1-5,65-69`。这证明了 GPU 和 CPU 对应了同一个 NUMA 节点。
