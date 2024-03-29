# CNI插件版本更新

## 20.11.1

### 变更记录

- 功能更新：
  - 支持Kubernetes中Pod暴露hostport端口。

### 要求

- Kubernetes版本：全部
- 地域：全部

## 20.10.1

### 变更记录

- 功能更新：
  - 删除Pod的时候，会显式尝试删除veth pair的host端；
  - 创建Pod的时候，会检查对应的veth名称设备是否残余存在，如果存在，先清理后创建。

### 要求

- Kubernetes版本：全部
- 地域：全部

## 20.09.1

### 变更记录

- 错误修复：删除嵌入的gops代理。
- 功能更新：
  - 快杰机型暂时不支持弹性网卡。
  - 优化了释放IP的流程。

### 要求

- Kubernetes版本：全部
- 地域：全部

## 20.07.1

### 变更记录

- Pod网络设置后，向全子网尝试发送GARP广播。

### 要求

- Kubernetes版本：全部
- 地域：全部

## 20.05.1

### 变更记录

- 修改UNI和EIP名称长度上限为64字节。
- cni增强自动识别节点主网卡，无需配置文件里配置。
- 识别UPHost物理机节点不运行UNI设备插件。

### 要求

- Kubernetes版本：全部
- 地域：全部

## 20.04.3

### 变更记录

- 功能更新：实现Pod绑定EIP的功能。

### 要求

- Kubernetes版本：全部
- 地域：全部

## 20.03.2

### 变更记录

- 功能更新：修复重复的API调用导致删除IP失败的更新。

### 要求

- Kubernetes版本：全部
- 地域：全部

## 20.03.1

### 变更记录

- 功能更新：升级CNI配置文件。

### 要求

- Kubernetes版本：全部
- 地域：全部

## 19.12.1

### 变更记录

- 功能更新：能够与Calico Felix和Typha结合，用来支持Kubernetes的网络策略，实现网络隔离功能。

### 要求

- Kubernetes版本：全部
- 地域：全部
