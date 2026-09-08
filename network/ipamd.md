# IPAMD IP 缓存机制与参数

IPAMD 会复用已经回收的 Pod IP，减少重复申请 VPC IP 带来的等待。每个节点、每个子网分别维护一个空闲 IP 池，水位参数用于控制这些空闲 IP 的保留数量。

当前版本不会主动预热 IP。空闲池没有可用地址时，IPAMD 会按需申请新的 VPC IP；Pod 删除后，原 IP 完成冷却才会进入空闲池，供后续 Pod 使用。

## 水位参数的作用

| 参数                              | 作用                                                                   |
| ------------------------------- | -------------------------------------------------------------------- |
| `--availablePodIPHighWatermark` | 空闲 IP 池的高水位。每个节点、每个子网分别生效；空闲数量超过高水位后，IPAMD 会释放超出的部分。高水位不是需要主动填满的目标值。 |
| `--availablePodIPLowWatermark`  | 已不实际生效，仅作为兼容项。                                                       |

高水位以下的空闲 IP 不会按闲置时间自动释放。因此，高水位越高，一个节点可能长期保留的空闲 IP 越多；高水位越低，缩容后释放回 VPC 的空闲 IP 越多。

## 什么时候调整高水位

- **调低高水位**：子网剩余 IP 紧张，或者工作负载缩容后，IPAMD 长期保留了较多空闲 IP。
- **调高高水位**：Pod 经常删除和重建，且子网地址充足，希望保留更多回收 IP 供后续 Pod 复用。

调高高水位不会立即申请或预热 IP，只会允许后续回收的 IP 保留得更多。调低高水位也只会释放空闲池中超出的部分，不会释放正在被 Pod 使用的 IP。

## 查看当前水位和空闲 IP

查看目标集群中 IPAMD 实际使用的启动参数：

```bash
kubectl -n kube-system get daemonset cni-vpc-ipamd \
  -o jsonpath='{range .spec.template.spec.containers[?(@.name=="cni-vpc-ipamd")].args[*]}{@}{"\n"}{end}'
```

查看每个节点、每个子网当前的空闲 IP 数量和高水位：

```bash
kubectl -n kube-system get ipamds \
  -o custom-columns='NODE:.spec.node,SUBNET:.spec.subnet,IDLE_IP:.status.current,HIGH:.status.high'
```

- `IDLE_IP` 是已经完成冷却、当前可以复用的空闲 IP 数量，不包含运行中 Pod 使用的 IP，也不包含仍在冷却的 IP。
- `HIGH` 是该空闲池当前上报的高水位。

Ipamd CR 用于观察 IPAMD 空闲缓存，不代表 VPC 子网实际剩余 IP。判断是否需要调低高水位时，请以
[VPC 控制台](https://console.ucloud.cn/vpc/subnet)中的子网剩余 IP 为准，并结合各节点的 `IDLE_IP` 变化判断 IPAMD
是否长期保留了较多空闲地址。

## 调整高水位

修改前请记录当前的 `--availablePodIPHighWatermark`。然后编辑 IPAMD DaemonSet：

```bash
kubectl -n kube-system edit daemonset cni-vpc-ipamd
```

在 `cni-vpc-ipamd` 容器的 `args` 中修改高水位：

```yaml
args:
  - --availablePodIPHighWatermark=<HIGH_WATERMARK>
```

保存后，Kubernetes 会滚动更新 IPAMD Pod。观察更新是否完成：

```bash
kubectl -n kube-system rollout status daemonset/cni-vpc-ipamd
```
