{{indexmenu_n>3}}
## 创建PVC

当前存储卷的类型支持SSD、SATA UDISK，UFS即将支持，敬请期待。

### 创建StorageClass

```
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: cloud
provisioner: ucloud/udisk
parameters:
  diskCategory: cloud_efficiency
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