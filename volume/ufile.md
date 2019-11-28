## 在UK8S中使用UFile

UK8S支持在集群中使用UFile对象存储作为持久化存储卷

支持UK8S版本：1.15.5、1.14.6（2019年9月17日之后创建）

### UFile使用必读

UFile对象存储适合用户上传、下载静态数据文件，如视频，图片等文件。

如果您的业务对于读写性能有很高的需求，如实时快速写入日志，推荐使用UDisk或者UFS作为UK8S集群的持久化存储，UFile不能提供像本地文件系统一样的功能。

### 已支持UK8S挂载UFile的地域（持续更新）

| 地域 | 外网 | 内网 |
|:---|:---|:---|
| 北京二 | s3-cn-bj.ufileos.com | internal.s3-cn-bj.ufileos.com |
| 上海 | s3-cn-sh2.ufileos.com | internal.s3-cn-sh2.ufileos.com |
| 拉各斯 | s3-afr-nigeria.ufileos.com | internal.s3-afr-nigeria.ufileos.com |
| 胡志明市 | s3-vn-sng.ufileos.com | internal.s3-vn-sng.ufileos.com |



### 一、创建UFile授权Secret

由于UFile带有地域属性和操作权限控制，我们需要手动创建Secret和StorageCLass。

首先我们事先在UFile的控制台创建好对象存储目录，并为这个目录生成一个授权令牌（Token），如图：

![](/images/volume/ufile.png)

Token创建管理教程可以[参考文档](storage_cdn/ufile/guide/token)。

在Kubernetes中为此令牌创建Secret，如下所示：

```
apiVersion: v1
kind: Secret
metadata:
  name: ufile-secret
  namespace: kube-system
stringData:
  accessKeyID: TOKEN_9a6ec9fd-9cb7-4510-8ded-xxxxxxxx # 非账号公钥，为Ufile的令牌公钥。
  secretAccessKey: c429c8e5-e4e6-4366-bf93-xxxxxx # 非账号私钥，为Ufile的令牌私钥。
  endpoint: internal.s3-cn-bj.ufileos.com
```

字段说明：

accessKeyID: UFile公钥

secretAccessKey: UFile私钥

endpoint: 对应地域接入S3服务URL

> 对应地域服务URL参考已支持UK8S挂载UFile的地域（持续更新）章节，推荐使用内网地址。


### 二、创建存储类StorageClass

接下来进行创建StorageClass操作，如下可以看到我们在这个StorageClass定义了UFile的backet并关联使用了前一步创建的Secret。

```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-ufile
provisioner: ufile.csi.ucloud.cn
parameters:
  bucket: csis3-bucketname  # 事先申请好的UFile Bucket
  csi.storage.k8s.io/node-publish-secret-name: csi-s3-secret # 关联前一步创建的Secret
  csi.storage.k8s.io/node-publish-secret-namespace: kube-system
```

### 三、创建持久化存储卷声明（PVC）

UFile单个Bucket的存储空间理论上是无上限的，所以PV和PVC中的容量参数没有实际意义，这里的requests信息不会真实生效。

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: logs3-claim
spec:
  storageClassName: csi-ufile
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
```

### 四、在pod中使用PVC


```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx 
    ports:
    - containerPort: 80
    volumeMounts:
    - name: test
      mountPath: /data
  volumes:
  - name: test
    persistentVolumeClaim:
      claimName: logs3-claim
```
