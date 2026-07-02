# 使用 ULB 暴露服务

下面的例子创建一个 Service,通过 ULB 把流量从公网引入到集群内的 Nginx 服务。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
  annotations:
    # LB 类型,outer 公网,inner 内网,默认公网
    service.beta.kubernetes.io/ucloud-load-balancer-type: "outer"
    # LB 付费模式,支持 month(按月)、year(按年)、dynamic(按时)
    service.beta.kubernetes.io/ucloud-load-balancer-charge-type: "month"
    # 带宽,单位为 Mbps,默认2
    service.beta.kubernetes.io/ucloud-load-balancer-bandwidth: "2"
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
  selector:
    app: nginx
```

创建完成后,通过 `kubectl get svc nginx-svc` 查看分配到的 EIP 地址,然后就能从公网访问了。

> 提示:outer 表示公网,inner 表示内网,这两个值是固定的,请不要改成大写。
