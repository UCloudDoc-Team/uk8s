# 集群内访问 Service

当我们在 UK8S 集群内部署好服务，配置了 svc 之后，如果访问服务的应用也在 k8s 集群内，则可以通过域名的方式访问服务

## 一、获取服务地址
![](/images/service/cluster_svc.png)

当我们服务访问的发起端(我们称为 client，这里以 api-pod-3 为例) 和 服务的接收端 (这里我们称为 server，这里以 access 为例) 同时运行在 UK8S 中时，一般使用 k8s 域名访问 server 服务，k8s 会自动将流量转发到对应的 pod 中。

访问的地址如下：

```
[servicename].[namespace].[resourcetype].[clusterdomain]
```

- servicename： 服务的名字，比如上面的 access
- namespace：服务所在的命名空间，上面对应 access 的命名空间 prj-foo
- resourcetype: 资源类型，访问类型为 service 时值统一为 svc
- clusterdomain： 集群域名，在控制台，具体某一个 k8s 实例的详情中获取，`概览`->`基本信息`中的`集群本地域名`可以获取具体的值，一般为 `cluster.local`

## 二、服务访问示例

#### 1. HTTP 服务访问

如果服务是 HTTP 服务，则我们可以通过 HTTP client 访问，对应的端口是 svc 配置的端口

```shell
curl http://access.prj-foo.svc.cluster.local:8080/
```

#### 2. tcp 服务访问

同理，在 tcp 服务中，我们使用服务地址作为我们访问时的 host，服务的端口作为访问时的 port。

比如说 access 是一个 grpc server

```go
func main() {
    conn, err := grpc.Dial("access.prj-foo.svc.cluster.local:8080", grpc.WithInsecure())
    ...
    defer conn.Close()

    client := pb.NewSearchServiceClient(conn)
    resp, err := client.Search(context.Background(), &pb.SearchRequest{
        Request: "gRPC",
    })
    ...
}
```
