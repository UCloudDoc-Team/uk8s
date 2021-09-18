# 镜像及镜像仓库常见问题

## 1. 如何在 UK8S 中 Build 镜像？

1. UK8S的1.12.7和1.13.5两个版本，目前Master节点没有安装Docker服务，不支持在Master节点Build镜像。
2. UK8S的Node节点有安装Docker服务，可以登陆到Node节点进行Build镜像，Node节点Build镜像时需要使用--network=host参数，例如：

```
docker build -f Dockerfile -t ucloud/tomcat:v1.0.0 . --network=host
```

> 还可以在 UHost 中安装docker服务进行Build镜像

## 2. 怎么在UK8S集群中拉取Uhub以外的镜像？

UK8S使用VPC网络实现内网互通，拉取Uhub镜像不受影响，拉取外网镜像时需要对VPC的子网配置网关，需要在UK8S所在的区域下进入VPC产品，对具体子网配置NAT网关，使集群节点可以通过NAT网关拉取外网镜像，具体操作详见[VPC创建NAT网关](vpc/briefguide/step4)
。

## 3. 为什么我的 UHub 登陆失败了?

1. 请确认是在公网还是 UCloud 内网进行登陆的（如果 ping uhub 的 ip 为 106.75.56.109 则表示是通过公网拉取）
2. 如果在公网登陆，请在 UHub 的 Console 页面确认外网访问选项打开
3. 确认是否使用独立密码登陆，UHub 独立密码是和用户绑定的，而不是和镜像库绑定的

## 4. UHub 下载失败（慢）

1. `ping uhub.service.ucloud.cn` （如果ip为106.75.56.109 则表示是通过公网拉取，有限速）
2. `curl https://uhub.service.ucloud.cn/v2/` 查看是否通，正常会返回 UNAUTHORIZED 或 301
3. `systemctl show --property=Environment docker` 查看是否配置了代理
4. 在拉镜像节点执行`iftop -i any -f 'host <uhub-ip>'`命令，同时尝试拉取 UHub 镜像，查看命令输出（uhub-ip替换为步骤1中得到的ip）
5. 对于公网拉镜像的用户，还需要在 Console 页面查看外网访问是否开启
