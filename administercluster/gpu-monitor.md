# 集群GPU监控

## 1. 介绍
Uk8s 使用开源组件 [Dcgm-Exporter](https://github.com/NVIDIA/dcgm-exporter) 用于获取 GPU 相关监控指标，主要包含：
- GPU 卡利用率
- 容器 GPU 资源利用率

## 2. 部署

如果你的集群还没有在uk8s的监控中心开启了监控，那么只需开启监控即可在 Grafana 页面查看 Dashboard `容器 GPU 监控`、`NVIDIA DCGM Exporter Dashboard`。

>  ⚠️ 下面的部署内容适用于 `2024/05/17` 前已经在 Uk8s 的监控中心开启了监控，`2024/05/17`后开启的监控默认自带 Dcgm-exporter 服务和 Dashboard:

### 2.1. 部署 Dcgm-Exporter
```sh
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/gpu-share/dcgm-exporter.yaml
```

### 2.2. 部署 DCGM 官方 Dashboard
>  ⚠️ `12239` 为 [DCGM](https://grafana.com/grafana/dashboards/12239-nvidia-dcgm-exporter-dashboard/) 官方 Dashboard。

登陆Grafana后，`选择左侧导航栏 '+' 号` --> `Import` --> `第一个输入框输入 12239` --> `Load`

### 2.3. 部署 Uk8s Container GPU Dashboard

> ⚠️ 官方的图表没有容器相关信息，如果你需要查看容器的 GPU 相关信息，需要导入 Uk8s 自制的 Dashboard。

登陆Grafana后，你需要先 [下载 json 文件](https://docs.ucloud.cn/uk8s/json/grafana/gpu-uk8s-grafana.json) --> `选择左侧导航栏 '+' 号` --> `Import` --> `第二个输入框粘贴下载的 json 内容` --> `Load`

## 3. 测试

你可以通过下面命令快速启动一个 GPU Pod。该 Pod 会运行一段时间结束。随后你可以在 Grafana 的 `Container GPU` Dashboard 中查看该 Pod 的 GPU 使用情况。

```sh
cat << EOF | kubectl create -f -
 apiVersion: v1
 kind: Pod
 metadata:
   name: dcgmproftester
 spec:
   restartPolicy: OnFailure
   containers:
   - name: dcgmproftester11
     image: uhub.service.ucloud.cn/uk8s/dcgmproftester
     args: ["--no-dcgm-validation", "-t 1004", "-d 120"]
     resources:
       limits:
          nvidia.com/gpu: 1
     securityContext:
       capabilities:
          add: ["SYS_ADMIN"]

EOF
```

## 4. Dashboard 图表

| Dashboard                      | Grafana图表              | 作用                                          |
| ------------------------------ | ------------------------ | --------------------------------------------- |
| NVIDIA DCGM Exporter Dashboard | GPU Temperature          | GPU 卡温度                                    |
| NVIDIA DCGM Exporter Dashboard | GPU Power Usage          | GPU 功耗                                      |
| NVIDIA DCGM Exporter Dashboard | GPU SM Clocks            | GPU 时钟频率                                  |
| NVIDIA DCGM Exporter Dashboard | GPU Utilization          | GPU 利用率                                    |
| NVIDIA DCGM Exporter Dashboard | Tensor Core Utilization  | Tensor Pipes 平均处于 Active 状态的周期分数。 |
| NVIDIA DCGM Exporter Dashboard | GPU Framebuffer Mem Used | GPU 显存使用量。                              |
| Container GPU                  | GPU Utilization          | 容器 GPU 利用率                                    |
| Container GPU                  | GPU Framebuffer Mem      | 容器 GPU 显存使用量&剩余量                    |
| Container GPU                  | GPU Memory Usage         | 容器 GPU 显存使用率                                |

## 5. DCGM 常见指标

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
| DCGM_FI_DEV_FB_USED | Gauge    | MiB      | GPU 帧缓存剩余量。 |

### 5.3. 频率

| 指标名称              | 指标类型 | 指标单位 | 指标含义           |
| --------------------- | -------- | -------- | ------------------ |
| DCGM_FI_DEV_SM_CLOCK  | Gauge    | MHz      | GPU SM 时钟频率。  |
| DCGM_FI_DEV_MEM_CLOCK | Gauge    | MHz      | GPU 内存时钟频率。 |

### 5.4. 剖析
| 指标名称                           | 指标类型 | 指标单位 | 指标含义                                                                                                                    |
| ---------------------------------- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------- |
| DCGM_FI_PROF_GR_ENGINE_ACTIVE      | Gauge    | %        | 在一个时间间隔内，Graphics 或 Compute 引擎处于 Active 的时间占比。                                                          |
| DCGM_FI_PROF_SM_ACTIVE             | Gauge    | %        | 在一个时间间隔内，至少一个线程束在一个 SM（Streaming Multiprocessor）上处于 Active 的时间占比。该值统计的是所有 SM 的均值。 |
| DCGM_FI_PROF_SM_OCCUPANCY          | Gauge    | %        | 在一个时间间隔内，驻留在 SM 上的线程束与该 SM 最大可驻留线程束的比例。该值统计的是所有 SM 的均值。                          |
| DCGM_FI_PROF_PIPE_TENSOR_ACTIVE    | Gauge    | %        | 单位时间内 Tensor Pipes 平均处于 Active 状态的周期分数。                                                                    |
| DCGM_FI_PROF_DRAM_ACTIVE           | Gauge    | %        | 内存拷贝活跃周期分数（一个周期内有一次 DRAM 指令则该周期为 100%）。                                                         |
| DCGM_FI_PROF_PIPE_FP64_ACTIVE      | Gauge    | %        | 单位时间内 F64 Pipes 平均处于 Active 状态的周期分数。                                                                       |
| DCGM_FI_PROF_PIPE_FP32_ACTIVE      | Gauge    | %        | 单位时间内 F32 Pipes 平均处于 Active 状态的周期分数。                                                                       |
| DCGM_FI_PROF_PIPE_FP16_ACTIVE      | Gauge    | %        | 单位时间内 F16 Pipes 平均处于 Active 状态的周期分数。                                                                       |
| DCGM_FI_PROF_NVLINK_RX_BYTES       | Counter  | B/s      | 通过 NVLink 接收的数据流量。                                                                                                |
| DCGM_FI_PROF_NVLINK_TX_BYTES       | Counter  | B/s      | 通过 NVLink 传输的数据流量。                                                                                                |
| DCGM_FI_PROF_PCIE_RX_BYTES         | Counter  | B/s      | 通过 PCIe 总线接收字节数。                                                                                                  |
| DCGM_FI_PROF_PCIE_TX_BYTES         | Counter  | B/s      | 通过 PCIe 总线传输字节数。                                                                                                  |
| DCGM_FI_DEV_PCIE_REPLAY_COUNTER    | Counter  | 次       | GPU PCIe 总线的重试次数。                                                                                                   |
| DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL | Counter  | -        | GPU 所有通道的 NVLink 带宽计数器总数。                                                                                      |

### 5.5. 温度和功率

| 指标名称                             | 指标类型 | 指标单位 | 指标含义             |
| ------------------------------------ | -------- | -------- | -------------------- |
| DCGM_FI_DEV_GPU_TEMP                 | Gauge    | ℃        | GPU 当前温度         |
| DCGM_FI_DEV_MEMORY_TEMP              | Gauge    | ℃        | GPU 显存当前温度     |
| DCGM_FI_DEV_POWER_USAGE              | Gauge    | W        | GPU 当前使用功率     |
| DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION | Counter  | mJ       | GPU 启动以来的总能耗 |

### 5.6. XID 错误&违规

| 指标名称                             | 指标类型 | 指标单位 | 指标含义                                 |
| ------------------------------------ | -------- | -------- | ---------------------------------------- |
| DCGM_FI_DEV_XID_ERRORS               | Gauge    | -        | 最近发生的错误代码                       |
| DCGM_CUSTOM_XID_ERRORS_TOTAL_COUNTER | Counter  | -        | 发生错误代码总数                         |
| DCGM_FI_DEV_POWER_VIOLATION          | Counter  | μs       | 因功率上限而导致违规的累积持续时间       |
| DCGM_FI_DEV_THERMAL_VIOLATION        | Counter  | μs       | 因热限制导致违规的累积持续时间           |
| DCGM_FI_DEV_SYNC_BOOST_VIOLATION     | Counter  | μs       | 因同步提升限制而导致违规的累积持续时间   |
| DCGM_FI_DEV_BOARD_LIMIT_VIOLATION    | Counter  | μs       | 因电路板限制而导致违规的累积持续时间     |
| DCGM_FI_DEV_LOW_UTIL_VIOLATION       | Counter  | μs       | 因低利用率限制导致违规的累积持续时间     |
| DCGM_FI_DEV_RELIABILITY_VIOLATION    | Counter  | μs       | 因电路板可靠性限制导致违规的累积持续时间 |

### 5.7. 停用的内存页面

| 指标名称                | 指标类型 | 指标单位 | 指标含义                      |
| ----------------------- | -------- | -------- | ----------------------------- |
| DCGM_FI_DEV_RETIRED_SBE | Counter  | 个       | 因单 bit 错误而停用的内存页面 |
| DCGM_FI_DEV_RETIRED_DBE | Counter  | 个       | 因双 bit 错误而停用的内存页面 |

### 5.8. 其他

| 指标名称                                | 指标类型 | 指标单位 | 指标含义                         |
| --------------------------------------- | -------- | -------- | -------------------------------- |
| DCGM_FI_DEV_VGPU_LICENSE_STATUS         | Gauge    | -        | vGPU 许可证状态                  |
| DCGM_FI_DEV_UNCORRECTABLE_REMAPPED_ROWS | Counter  | -        | 因无法纠正的错误而重新映射的行数 |
| DCGM_FI_DEV_CORRECTABLE_REMAPPED_ROWS   | Counter  | -        | 因可纠正的错误而重新映射的行数   |
| DCGM_FI_DEV_ROW_REMAP_FAILURE           | Gauge    | -        | 重新映射行是否失败               |