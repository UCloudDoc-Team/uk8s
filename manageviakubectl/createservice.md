
## 创建Service

### 创建一个类型为LoadBalancer的Service，将MYSECRET换成自定义的SecretName即可。

```

apiVersion: v1
kind: Service
metadata: 
  name: ucloud-nginx
  labels:
    app: ucloud-nginx
spec: 
  type: LoadBalancer
  ports: 
    - protocol: TCP
      port: 80
  selector:
    app: ucloud-nginx
---
apiVersion: v1
kind: Pod
metadata:
  name: test-nginx
  labels:
    app: ucloud-nginx
spec:
  containers:
  - name: nginx
    image: uhub.service.ucloud.cn/ucloud/nginx:1.9.2
    ports:
    - containerPort: 80
  imagePullSecrets:
    - name: MYSECRET
```

系统会自动生成一个ULB，UK8S同时还支持配置ULB的各种参数，详见[service](../service/annotations)