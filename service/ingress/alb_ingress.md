# ALB Ingress

> alb ingress 是使用 ucloud alb 实现 k8s ingress

## 部署

## 例子

## 注解参数说明

| 注解名称                                           | 说明                                                    | 默认值                      | 是否支持动态配置 |
|----------------------------------------------------|---------------------------------------------------------|-----------------------------|------------------|
| alb.ingress.kubernetes.io/load-balancer-id         | 绑定的LB的ID                                            | ""                          | 否               |
| alb.ingress.kubernetes.io/load-balancer-type       | LB 的类型 (outer/inner)                                 | outer                       | 是               |
| alb.ingress.kubernetes.io/http-listen-ports        | LB 监听端口，默认 HTTP 80 和 HTTPS 443 json数组格式     | [{"HTTP":80},{"HTTPS":443}] | 否               |
| alb.ingress.kubernetes.io/certificates             | 指定 ucloud ssl 证书 id，数组逗号隔开，第一个为默认证书 | ""                          | 是               |
| alb.ingress.kubernetes.io/subnet-id                | 子网 ID                                                 | 集群的子网                  | 否               |
| alb.ingress.kubernetes.io/load-balancer-chargetype | LB 付费模式 (month/year/dynamic)                        | "month"                     | 否               |
| alb.ingress.kubernetes.io/load-balancer-quantity   | LB 付费时长                                             | 1                           | 否               |
| alb.ingress.kubernetes.io/monitor-domain           | http 的方式做健康检查的域名                             | ""                          | 是               |
| alb.ingress.kubernetes.io/monitor-path             | http 的方式做健康检查的路径                             | ""                          | 是               |
| alb.ingress.kubernetes.io/security-groups          | 安全组配置，多个使用逗号隔开，优先级为顺序              | ""                          | 是               |
| alb.ingress.kubernetes.io/eip-paymode              | EIP 计费模式 (traffic/bandwidth/sharebandwidth)         | "bandwidth"                 | 否               |
| alb.ingress.kubernetes.io/eip-sharebandwidthid     | EIP 共享带宽 ID                                         | ""                          | 否               |
| alb.ingress.kubernetes.io/eip-bandwidth            | EIP 带宽，单位为 Mbps                                   | 2                           | 是               |
| alb.ingress.kubernetes.io/eip-chargetype           | EIP 付费模式 (month/year/dynamic)                       | "month"                     | 否               |
| alb.ingress.kubernetes.io/eip-quantity             | EIP 付费时长，chargetype 为 dynamic 时无需填写          | 1                           | 否               |
| alb.ingress.kubernetes.io/eip-operator-name        | EIP 弹性IP线路 (International/Bgp/BGPPro/Telecom)       | 根据地域                    | 否               |

* lb类型:
  * outer：外网
  * innger： 内网

* 付费模式:
  * month: 按月
  * year： 按年
  * dynamic: 按时

* EIP 计费模式：
  * traffic: 按流量
  * bandwidth: 按带宽
  * sharebandwidth: 共享带宽

* EIP 默认线路:
  * BGP: 华北一、上海、广州、华北二
  * International: 其他地域

* 动态配置是指创建完成之后仍然可以修改的配置
