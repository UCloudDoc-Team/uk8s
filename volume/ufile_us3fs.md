# 使用 us3fs 挂载 US3

UK8S 支持在集群中使用 US3 对象存储作为持久化存储卷，默认使用 s3fs 进行挂载。本文档介绍如何使用**us3fs**（UCloud 自研 FUSE 实现）替代 s3fs 来挂载 US3 存储桶。

## 背景

us3fs 是 UCloud 自研的兼容 POSIX 语义的 FUSE 用户态文件系统，专为 US3 对象存储设计，避免了 s3fs 的一些已知问题:

1. 偶发的 segfault
2. [cache 写满问题](https://github.com/s3fs-fuse/s3fs-fuse/issues/2694)

同时 us3fs 也存在以下限制:

> ⚠️ 需要注意和 s3fs 不同， us3fs **不支持**追加写，在写入日志等需要追加写的场景下不建议使用 us3fs

您可以阅读 us3fs 介绍文档了解更多: https://docs.ucloud.cn/ufile/tools/us3fs/introduction

## 使用前提

- CSI 版本为 **26.05.20** 及以上

## 启用 us3fs

默认情况下 CSI 使用 s3fs 作为 mounter。要启用 us3fs，需要在 CSI Driver 容器启动参数中添加 `--mounter=us3fs`：

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: csi-ufile
  namespace: kube-system
spec:
  template:
    spec:
      containers:
      - name: ufile
        image: uhub.service.ucloud.cn/cncfdev/csi-uk8s:<csi-version>
        args:
        - "--drivername=ufile.csi.ucloud.cn"
        - "--endpoint=$(CSI_ENDPOINT)"
        - "--hostname=$(KUBE_NODE_NAME)"
        - "--mounter=us3fs"      # 关键：指定使用 us3fs
        # 可选：指定 us3fs 挂载选项
        # - "--us3-opt=--log_dir=/var/log/us3fs -o allow_other"
        env:
        - name: CSI_ENDPOINT
          value: unix://var/run/csi/csi.sock
        - name: KUBE_NODE_NAME
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: spec.nodeName
```

您也可以直接通过命令修改已有 DaemonSet：

```shell
kubectl -n kube-system patch daemonset csi-ufile --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/1/args/-", "value": "--mounter=us3fs"}]'
```

配置说明：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--mounter` | 指定 mounter 类型，可选 `s3fs` 或 `us3fs` | `s3fs` |
| `--us3-opt` | us3fs 挂载选项，为空时使用默认配置 | `-o allow_other` |

us3fs 默认挂载选项为 `-o allow_other`，日志目录默认为 `/var/log/us3fs`。可通过 `--us3-opt` 自定义，例如：

```
--us3-opt=--log_dir=/var/log/us3fs -o allow_other -o mp_umask=000
```

您可以通过[ us3fs 文档 ](https://docs.ucloud.cn/ufile/tools/us3fs/quickaccess?id=%e9%80%89%e9%a1%b9%e5%88%97%e8%a1%a8) 查看可用的选项列表。

## 创建 US3 授权 Secret

与 s3fs 挂载方式一致，在 US3 控制台创建对象存储目录并生成授权令牌（Token），然后在 Kubernetes 中创建 Secret：

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: us3-secret
  namespace: kube-system
stringData:
  accessKeyID: TOKEN_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx # US3令牌公钥
  secretAccessKey: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxx      # US3令牌私钥
  endpoint: http://internal-cn-wlcb.ufileos.com
```

字段说明：

- `accessKeyID`：US3 令牌公钥
- `secretAccessKey`：US3 令牌私钥
- `endpoint`：对应地域接入 US3 服务的域名，具体请查看[US3 接入域名](https://docs.ucloud.cn/ufile/introduction/region) 。请注意选择 US3 协议的访问域名，而非 AWS S3 协议的域名。

> 推荐使用内网地址以获得更好的性能和稳定性。

## 创建存储类 StorageClass

使用 us3fs 时，StorageClass 的定义与 s3fs 完全一致，无需额外参数：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-ufile-us3fs
provisioner: ufile.csi.ucloud.cn
parameters:
  bucket: csis3-bucketname       # 事先申请好的US3 Bucket
  path: /csis3-dirname/          # 挂载时相对Bucket根文件的目录结构，默认为/
  csi.storage.k8s.io/node-publish-secret-name: us3-secret
  csi.storage.k8s.io/node-publish-secret-namespace: kube-system

  # 跨项目挂载时额外提供以下参数
  csi.storage.k8s.io/provisioner-secret-name: us3-secret
  csi.storage.k8s.io/provisioner-secret-namespace: kube-system
```

## 创建 PVC

US3 单个 Bucket 的存储空间理论上是无上限的， PV 和 PVC 中的容量参数没有实际意义，不会真实生效。

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: us3fs-claim
spec:
  storageClassName: csi-ufile-us3fs
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
```

## 在 Pod 中使用 PVC

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-us3fs
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: test
      mountPath: /data
  volumes:
  - name: test
    persistentVolumeClaim:
      claimName: us3fs-claim
```

## 验证挂载

Pod 启动后，可通过以下方式确认挂载是否正常：

```shell
# 进入 Pod 查看挂载情况
kubectl exec -it nginx-us3fs -- df -h

# 在节点上查看 us3fs 进程
pgrep -x us3fs

# 查看节点上的挂载点
mount | grep us3fs
```

## 从 s3fs 挂载切换到 us3fs 挂载

> ⚠️ 您只能在集群中选择使用 s3fs 或 us3fs 其中一种挂载方式, 如果当前集群已经存在 s3fs 挂载的 PVC，我们不推荐您切换到 us3fs。

如果您希望换到 us3fs 挂载, 需要的步骤为:

1. 按以上文档完成 csi-ufile DaemonSet 部署调整和新的存储类(使用 us3 endpoint)创建
2. 将现有的使用了 s3fs 挂载的 Pod 数量缩容到 0
3. 删除所有使用旧的 ufile 存储类(使用 s3 endpoint)创建的 PVC, 并使用新的存储类(使用 us3 endpoint)重建同名 PVC
4. 恢复 Pod 副本数

