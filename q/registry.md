
## 镜像库常见问题

### 如何在UK8S中Build镜像？

1. UK8S的1.12.7和1.13.5两个版本，目前Master节点没有安装Docker服务，不支持在Master节点Build镜像。
2. UK8S的Node节点有安装Docker服务，可以登陆到Node节点进行Build镜像，Node节点Build镜像时需要使用--network=host参数，例如：

```
docker build -f Dockerfile -t ucloud/tomcat:v1.0.0 . --network=host
```

> 还可以在UHost中安装docker服务进行Build镜像