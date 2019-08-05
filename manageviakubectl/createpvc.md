{{indexmenu_n>3}}
## 创建PVC

当前存储卷支持SSD、SATA类型的UDisk以及UFS，详见：

* [在UK8S中使用UDisk](/compute/uk8s/volume/udisk)
* [在UK8S中使用UFS](/compute/uk8s/volume/ufs)


### 创建StorageClass

以下以UDisk为示例

```
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: cloud
provisioner: ucloud/udisk
parameters:
  type: ssd
```


### 创建一个存储卷声明并Mount到Pod

```
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test-pvc-claim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: cloud
  resources:
    requests:
      storage: 20Gi

---
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: test
      mountPath: /data
    ports:
    - containerPort: 80
  volumes:
  - name: test
    persistentVolumeClaim:
      claimName: test-pvc-claim
```

备注：受UDisk产品限制，PVC最小为20GB，步长为10GB。