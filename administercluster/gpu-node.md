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

| 显卡                                 | 标准镜像名            | Driver Version | CUDA Version |
|-------------------------------------|----------------------|----------------|--------------|
| 高性价比显卡（如高性价比显卡3/4/5/6等）  | Ubuntu 20.04-高性价比  | 550.120        | 12.4         |
| 非高性价比显卡（如T4、V100S、P40等）    | Ubuntu 20.04          | 550.90.12      | 12.4         |
| 非高性价比显卡（如T4、V100S、P40等）    | Centos 7.6            | 450.80.02      | 11.0         |

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
