# Vertical Pod Autoscaler (VPA) 使用文档

## 1. 初识VPA

### 1.1. 什么是 VPA

VPA 是一个自动调整容器中垂直资源（CPU和内存）的工具。VPA 根据容器实际资源使用情况，自动调整Pod的资源请求，以确保Pod在运行时有足够的资源。

### 1.2. VPA 的优势

**优势**

- **资源优化:** VPA通过动态调整容器资源请求，提高资源利用率。
- **性能改进:** 通过确保Pod有足够的资源，VPA提高了应用程序的性能和稳定性。
- **自动化:** VPA能够在不需要人为干预的情况下自动调整资源。

#### 1.2.1. VPA 的限制

1. 由于VPA会自动调整Pod的资源请求，因此Pod可能会在后台重启，Pod可能会调度到其他的节点。

2. 避免`VPA`和`HPA`同时使用。

## 2. 安装

### 2.1. 先决条件
- Kubernetes 1.10+

### 2.2. 部署

#### 2.2.1. 部署 VPA 服务证书
```sh
curl -sfL https://docs.ucloud.cn/uk8s/yaml/vpa/gencerts.sh | sh -
```

### 2.3. 部署 VPA 服务

**1.22及版本以上**
```sh
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/vpa/vpa.yaml
```

**1.22以下**
```sh
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/vpa/vpa-less-1.22.yaml
```

### 2.4. 部署一个 VPA 对象

```sh
kubectl apply -f https://docs.ucloud.cn/uk8s/yaml/vpa/deployment.yaml
```

## 3. 查看 VPA 对象
```sh
kubectl describe vpa nginx-vpa
```

上述命令输出为 VPA 为 Deployment 推荐的值。

```sh
  Recommendation:
    Container Recommendations:
      Container Name:  nginx
      Lower Bound:
        Cpu:     25m
        Memory:  262144k
      Target:
        Cpu:     25m
        Memory:  262144k
      Uncapped Target:
        Cpu:     25m
        Memory:  262144k
      Upper Bound:
        Cpu:     50032m
        Memory:  107227776429
```

