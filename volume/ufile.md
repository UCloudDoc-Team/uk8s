# 在UK8S中使用US3

UK8S支持在集群中使用US3对象存储作为持久化存储卷

支持UK8S版本：大于1.14.6（2019年9月17日之后创建）

## US3 使用必读

US3对象存储适合用户上传、下载静态数据文件，如视频，图片等文件。

如果您的业务对于读写性能有很高的需求，如实时快速写入日志，推荐使用UDisk或者UFS作为UK8S集群的持久化存储，US3不能提供像本地文件系统一样的功能。

> ⚠️ 21.09.1 版本之前的CSI UFile，当CSI Pod异常重启时，会造成所在节点上使用US3/UFile的pod挂载点失效，如果您的业务使用US3/UFile，请务必确认当前版本，并按照[CSI升级文档](uk8s/volume/CSI_update)尽快升级。如有疑问，请与我们技术支持联系。

### 手动部署CSI

> 对于没有预装US3 csi的集群，请执行以下命令来部署

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/volume/us3.21.11.2/csi-controller.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/volume/us3.21.11.2/csi-node.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/volume/us3.21.11.2/rbac-controller.yml
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/volume/us3.21.11.2/rbac-node.yml
```

## 已支持UK8S挂载US3的地域（持续更新）

UK8S已经支持挂载US3，具体支持地域请查看
[US3接入域名](https://docs.ucloud.cn/ufile/s3/s3_introduction?id=%E6%8E%A5%E5%85%A5%E5%9F%9F%E5%90%8D%EF%BC%88endpoint%EF%BC%89)

## 一、创建US3授权Secret

由于US3带有地域属性和操作权限控制，我们需要手动创建Secret和StorageCLass。

首先我们事先在US3的控制台创建好对象存储目录，并为这个目录生成一个授权令牌（Token），如图：

![](/images/volume/us3.png)

Token创建管理教程可以[参考文档](ufile/guide/token)。

在Kubernetes中为此令牌创建Secret，如下所示：

```
apiVersion: v1
kind: Secret
metadata:
  name: us3-secret
  namespace: kube-system
stringData:
  accessKeyID: TOKEN_9a6ec9fd-9cb7-4510-8ded-xxxxxxxx # 非账号公钥，为US3的令牌公钥。
  secretAccessKey: c429c8e5-e4e6-4366-bf93-xxxxxx # 非账号私钥，为US3的令牌私钥。
  endpoint: http://internal.s3-cn-bj.ufileos.com
```

字段说明：

accessKeyID: US3公钥

secretAccessKey: US3私钥

endpoint:
对应地域接入S3服务URL，具体请查看[US3接入域名](https://docs.ucloud.cn/ufile/s3/s3_introduction?id=%E6%8E%A5%E5%85%A5%E5%9F%9F%E5%90%8D%EF%BC%88endpoint%EF%BC%89)

> 对应地域服务URL参考已支持UK8S挂载US3的地域（持续更新）章节，推荐使用内网地址。

## 二、创建存储类StorageClass

接下来进行创建StorageClass操作，如下可以看到我们在这个StorageClass定义了US3的backet并关联使用了前一步创建的Secret。

```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-ufile
provisioner: ufile.csi.ucloud.cn
parameters:
  bucket: csis3-bucketname  # 事先申请好的US3 Bucket
  csi.storage.k8s.io/node-publish-secret-name: us3-secret # 关联前一步创建的Secret
  csi.storage.k8s.io/node-publish-secret-namespace: kube-system
```

## 三、创建持久化存储卷声明（PVC）

US3单个Bucket的存储空间理论上是无上限的，所以PV和PVC中的容量参数没有实际意义，这里的requests信息不会真实生效。

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

## 四、在pod中使用PVC

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
