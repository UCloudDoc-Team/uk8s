# 集群 IP 网段容量规划与扩容

UK8S 的 Pod IP 使用 VPC 子网中的 IP。创建集群或规划扩容前，除了业务 Pod，还需要考虑节点、IPAMD 空闲缓存和其他云资源的地址占用，并按每个子网分别估算规划规模下的峰值需求。

## 确认 Pod IP 来源

### Pod 使用节点子网

默认情况下，Pod IP 基于 Node 所在子网分配。每个节点都有一个主网卡与 VPC 子网关联，调度到该节点的 Pod 也从同一子网获得 VPC IP。同一 VPC
内不同子网之间一般可以互通，实际通信仍取决于路由、安全组和网络 ACL 等配置；各子网的 IP 容量需要分别核算。

在此模式下，现有节点只能继续使用其所在子网的地址。需要在新子网中增加节点，并让新增 Pod 调度到这些节点，才能使用新子网中的 IP。

### Pod 使用独立子网

启用 Pod 独立子网后，Node IP 来自节点子网，Pod IP 来自 `PodNetworking` 配置的 Pod 子网，两类子网需要分别核算。Pod 子网容量不足时，可以直接增加 Pod
Subnet，具体操作参见 [Pod 使用独立子网](/uk8s/network/podnetwork)。

## 估算规划所需 IP 容量

下面的公式用于估算创建集群或扩容到目标规模后，一个子网需要承载的预期 IP 总量：

```text
子网预期 IP 占用 =
  规划中 Node IP 数量
  + 规划中非 hostNetwork Pod IP 数量
  + 规划中 IPAMD 可能保留的空闲 IP 数量
  + 规划中其他共享该子网的云资源 IP 数量
  + 预留的扩容余量
```

- **IPAMD 可能保留的空闲 IP 数量**：已经从 VPC 子网分配给节点、当前没有被 Pod 使用的 IP。Pod 删除并完成冷却后，IP
  会进入空闲池；不超过高水位的缓存不会按空闲时间自动释放。高水位按节点和子网分别生效，规划时应结合实际参数、节点数量以及每个节点可能使用的子网数量估算。
- **其他共享该子网的云资源 IP**：同一子网内的云主机、虚拟网卡、负载均衡实例、数据库、缓存和其他占用私网地址的资源。

## 查看现有子网剩余 IP

在 [VPC 控制台](https://console.ucloud.cn/vpc/subnet)查看子网的实际剩余 IP 数量。该数值表示子网当前还可以继续分配的地址，已经扣除了现有资源的占用。

## 扩展集群可用 IP 容量

- **Pod 使用节点子网**：在同一 VPC 中创建新子网并在新子网中增加节点。新增 Pod 调度到这些节点后，才会从新子网分配 IP。扩容后仍需分别检查各子网的节点和 Pod
  分布，避免旧子网继续承担全部增长。
- **Pod 使用独立子网**：直接为集群增加 Pod Subnet。新增子网会成为新 Pod 的候选子网，具体操作和分配方式参见
  [Pod 使用独立子网](/uk8s/network/podnetwork)。

## 查看当前 IP 使用情况

查看 Pod IP、所在节点以及是否使用 `hostNetwork`：

```bash
kubectl get pods -A \
  -o custom-columns='NAMESPACE:.metadata.namespace,NAME:.metadata.name,HOST_NETWORK:.spec.hostNetwork,POD_IP:.status.podIP,NODE:.spec.nodeName'
```

未显式设置 `hostNetwork` 时，`HOST_NETWORK` 可能显示为 `<none>`，其含义与 `false` 相同。尚未分配地址或未完成调度的 Pod，其 `POD_IP` 或
`NODE` 也可能显示为 `<none>`，不要将这类空值计入当前 IP 占用。基础组件的数量会随集群版本和启用功能变化，应以计划扩容的集群实际配置为准，不使用固定的系统 Pod 数量。

查看每个节点、每个子网的 IPAMD 空闲缓存和高水位：

```bash
kubectl -n kube-system get ipamds \
  -o custom-columns='NODE:.spec.node,SUBNET:.spec.subnet,IDLE_IP:.status.current,HIGH:.status.high'
```

`IDLE_IP` 是已经结束冷却、位于 IPAMD 空闲池中的缓存 IP 数量，不包含正在被 Pod 使用或仍在冷却中的 IP，因此不代表 IPAMD 占用的全部子网地址。`HIGH`
是该节点在该子网中的空闲缓存高水位，不是启动时主动申请的目标数量。低水位不会主动预热 IP。IPAMD 的完整行为和参数说明请参见 [IPAMD](/uk8s/network/ipamd)。

节点以及其他云资源 IP 占用可在 VPC 界面查看。
