# 集群GPU监控

## 1. 介绍
Uk8s 使用开源组件 [Dcgm-Exporter](https://github.com/NVIDIA/dcgm-exporter) 用于获取 GPU 相关监控指标，主要包含：
- GPU 卡利用率
- 容器 GPU 资源利用率

**GPU监控与当前版本的GPU共享插件存在兼容问题，目前暂不支持同时开启**

## 2. 部署

开启 [监控中心](/uk8s/monitor/prometheusplugin/startmonitor) 即可在 Grafana 页面查看 Dashboard `NVIDIA/DCGM/Exporter/Node`、`NVIDIA/DCGM/Exporter/Container`。


## 3. 测试

你可以通过下面命令快速启动一个 GPU Pod。该 Pod 使用 Ubuntu 24.04 和 CUDA 13.2 的 DCGM 镜像运行 `dcgmproftester13`，默认运行 120 秒后结束。运行期间可以在 Grafana 的 `NVIDIA/DCGM/Exporter/Container` Dashboard 中查看该 Pod 的 GPU 使用情况。

```sh
cat <<'EOF' | kubectl create -f -
apiVersion: v1
kind: Pod
metadata:
  name: dcgmproftester13
spec:
  restartPolicy: OnFailure
  containers:
  - name: dcgmproftester13
    image: uhub.service.ucloud.cn/andrew/dcgm:4.6.0-1-ubuntu24.04
    command: ["/usr/bin/dcgmproftester13"]
    args: ["--no-dcgm-validation", "-t", "1004", "-d", "120"]
    resources:
      limits:
        nvidia.com/gpu: 1
    securityContext:
      capabilities:
        add: ["SYS_ADMIN"]
  tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule
EOF
```

通过下面命令查看测试结果：

```sh
kubectl logs dcgmproftester13
```

日志中出现 `GPU 0, TestField 1004 test PASSED.` 和 `All Tests Passed.` 表示测试成功。验证完成后可以删除该测试 Pod：

```sh
kubectl delete pod dcgmproftester13 --ignore-not-found
```

## 4. Dashboard 图表

| Dashboard                      | Grafana图表              | 作用                                          |
| ------------------------------ | ------------------------ | --------------------------------------------- |
| NVIDIA/DCGM/Exporter/Node      | GPU Temperature          | GPU 卡温度                                    |
| NVIDIA/DCGM/Exporter/Node      | GPU Power Usage          | GPU 功耗                                      |
| NVIDIA/DCGM/Exporter/Node      | GPU SM Clocks            | GPU 时钟频率                                  |
| NVIDIA/DCGM/Exporter/Node      | GPU Utilization          | GPU 利用率                                    |
| NVIDIA/DCGM/Exporter/Node      | Tensor Core Utilization  | Tensor Pipes 平均处于 Active 状态的周期分数（设备支持时） |
| NVIDIA/DCGM/Exporter/Node      | GPU Framebuffer Mem Used | GPU 显存使用量                              |
| NVIDIA/DCGM/Exporter/Node      | GPU XID Error            | GPU XID 错误                              |
| NVIDIA/DCGM/Exporter/Container | GPU Utilization          | 容器 GPU 利用率                               |
| NVIDIA/DCGM/Exporter/Container | GPU Framebuffer Mem      | 容器 GPU 显存使用量和剩余量                    |
| NVIDIA/DCGM/Exporter/Container | GPU Memory Usage         | 容器 GPU 显存使用率                           |

> `Tensor Core Utilization`、`GPU XID Error` 等图表依赖对应 DCGM 指标。GPU 型号、驱动或 DCGM 不输出对应指标时，图表可能为空。


## 5. DCGM 常见指标

下面列出当前 `dcgm-exporter` 默认配置中的常见指标。部分指标依赖 GPU 型号、驱动和 DCGM 支持，实际是否有数据以 Prometheus 中的时间序列为准。

### 5.1. 利用率

| 指标名称                  | 指标类型 | 指标单位 | 指标含义             |
| ------------------------- | -------- | -------- | -------------------- |
| DCGM_FI_DEV_GPU_UTIL      | Gauge    | %        | GPU 利用率。         |
| DCGM_FI_DEV_MEM_COPY_UTIL | Gauge    | %        | GPU 内存带宽利用率。 |
| DCGM_FI_DEV_ENC_UTIL      | Gauge    | %        | GPU 编码器利用率。   |
| DCGM_FI_DEV_DEC_UTIL      | Gauge    | %        | GPU 解码器利用率。   |

### 5.2. 显存

> 在 GPU 里，显卡内存（显存）也被称为帧缓存。

| 指标名称            | 指标类型 | 指标单位 | 指标含义           |
| ------------------- | -------- | -------- | ------------------ |
| DCGM_FI_DEV_FB_FREE | Gauge    | MiB      | GPU 帧缓存剩余量。 |
| DCGM_FI_DEV_FB_USED | Gauge    | MiB      | GPU 帧缓存使用量。 |

### 5.3. 频率

| 指标名称              | 指标类型 | 指标单位 | 指标含义           |
| --------------------- | -------- | -------- | ------------------ |
| DCGM_FI_DEV_SM_CLOCK  | Gauge    | MHz      | GPU SM 时钟频率。  |
| DCGM_FI_DEV_MEM_CLOCK | Gauge    | MHz      | GPU 内存时钟频率。 |

### 5.4. 剖析
| 指标名称                           | 指标类型 | 指标单位 | 指标含义                                                                                                                    |
| ---------------------------------- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------- |
| DCGM_FI_PROF_GR_ENGINE_ACTIVE      | Gauge    | %        | 在一个时间间隔内，Graphics 或 Compute 引擎处于 Active 的时间占比。                                                          |
| DCGM_FI_PROF_PIPE_TENSOR_ACTIVE    | Gauge    | %        | 单位时间内 Tensor Pipes 平均处于 Active 状态的周期分数。                                                                    |
| DCGM_FI_PROF_DRAM_ACTIVE           | Gauge    | %        | 内存拷贝活跃周期分数（一个周期内有一次 DRAM 指令则该周期为 100%）。                                                         |
| DCGM_FI_PROF_PCIE_RX_BYTES         | Gauge    | B/s      | 通过 PCIe 总线接收的数据速率。                                                                                              |
| DCGM_FI_PROF_PCIE_TX_BYTES         | Gauge    | B/s      | 通过 PCIe 总线传输的数据速率。                                                                                              |
| DCGM_FI_DEV_PCIE_REPLAY_COUNTER    | Counter  | 次       | GPU PCIe 总线的重试次数。                                                                                                   |
| DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL | Counter  | -        | GPU 所有通道的 NVLink 带宽计数器总数。                                                                                      |

### 5.5. 温度和功率

| 指标名称                             | 指标类型 | 指标单位 | 指标含义             |
| ------------------------------------ | -------- | -------- | -------------------- |
| DCGM_FI_DEV_GPU_TEMP                 | Gauge    | ℃        | GPU 当前温度         |
| DCGM_FI_DEV_MEMORY_TEMP              | Gauge    | ℃        | GPU 显存当前温度     |
| DCGM_FI_DEV_POWER_USAGE              | Gauge    | W        | GPU 当前使用功率     |
| DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION | Counter  | mJ       | GPU 启动以来的总能耗 |

### 5.6. XID 错误

| 指标名称               | 指标类型 | 指标单位 | 指标含义           |
| ---------------------- | -------- | -------- | ------------------ |
| DCGM_FI_DEV_XID_ERRORS | Gauge    | -        | 最近发生的 XID 错误代码 |

### 5.7. 其他

| 指标名称                                | 指标类型 | 指标单位 | 指标含义                         |
| --------------------------------------- | -------- | -------- | -------------------------------- |
| DCGM_FI_DEV_VGPU_LICENSE_STATUS         | Gauge    | -        | vGPU 许可证状态                  |
| DCGM_FI_DEV_UNCORRECTABLE_REMAPPED_ROWS | Counter  | -        | 因无法纠正的错误而重新映射的行数 |
| DCGM_FI_DEV_CORRECTABLE_REMAPPED_ROWS   | Counter  | -        | 因可纠正的错误而重新映射的行数   |
| DCGM_FI_DEV_ROW_REMAP_FAILURE           | Gauge    | -        | 重新映射行是否失败               |
