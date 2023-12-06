# 添加接收人

监控中心支持添加接收人邮箱、企业微信及钉钉三种告警形式，请在 UK8S 控制台「监控中心」→「收发设置」进行配置。

## 1. 配置发件服务器

配置接收人前，需要先设置发件人邮箱信息。目前发送信息是通过邮箱发送。 

不同的邮件服务提供商对于发件服务器的配置都有较为详细的说明；这里强调两点：

1. 目前尚不支持TLS，因此请勿填写TLS端口；
2. 密码建议为客户端密码，填写邮箱登录密码可能无法发送邮件。

![](/images/prometheus/fajianren.jpg)

## 2. 配置邮件接收人

支持添加多个邮件接收人

![](/images/prometheus/addemial.jpg)

- 名称： 收件人名称
- 邮箱地址： 收件的邮箱地址

## 3. 配置企业微信接收人

> 注：企业微信机器人类型请参考 '配置webhook接收人(钉钉/企业微信机器人方式)' 方式

在使用微信接收人之前，我们必须在微信管理后台创建一个应用并获取应用ID、企业ID、应用秘钥、部门ID、企业微信用户ID等信息，需要咨询您的企业微信负责人或者管理员方可获取相关信息。

![](images/prometheus/addwechat.jpg)

- 名称：为接收人定义的名称，用于alertmanager的配置
- 企业ID：企业微信唯一ID；管理员登录企业微信web页面，在我的企业->企业信息中查询；（企业微信只有一人时无法查询）
- 应用ID：管理员登录企业微信web页面，在应用管理查看自建应用详情，应用的AgentId就是此应用的ID； 如果没有自建应用，可以先新建一个应用；
- 应用密钥：这里同应用ID的查询一致，在应用详情页面有secret选项，就是应用的密钥；
- 接收人：
  - 接收人标签：为接收人创建标签
  - 接收人部门：接收人所在企业部门ID， 管理员进入通讯录，在通讯找到接收人所在部门，点击部门旁边三个点，然后查看部门ID
  - 接收用户：接收人用户邮箱；

![](images/prometheus/weixinsetting.jpg)

由于监控中心配置了一条watchdog告警规则，只要企业微信的信息填写正确，一般10分钟以内均可从企业微信中获取到告警信息。

## 4. 配置webhook接收人(钉钉/企业微信机器人方式)

#### 4.1 创建钉钉/企业微信机器人，获取 Webhook 地址

在使用webhook接收人(钉钉/企业微信机器人方式)之前，我们必须在钉钉/企业微信管理后台创建自定义机器人，并获取其 Webhook 地址，详情参考钉钉/企业微信相关文档。

#### 4.2 部署配置文件

AlertManager 不支持直接接入钉钉/企业微信告警，需要进行适配转换，以下是参考社区的示例部署 yaml 文件。

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-webhook
  namespace: uk8s-monitor
data:
  config.yaml: |-
     targets:
      webhook1:  
        # 请替换为您的钉钉/企业微信机器人 Webhook 地址
        url: https://oapi.dingtalk.com/robot/send?access_token=xxxxxx
---
apiVersion: v1
kind: Service
metadata:
  name: alertmanager-webhook
  namespace: uk8s-monitor
spec:
  selector:
    k8s-app: webhook
  ports:
    - name: http
      port: 80
      targetPort: 8060
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alertmanager-webhook
  namespace: uk8s-monitor
spec:
  replicas: 2
  selector:
    matchLabels:
      k8s-app: webhook
  template:
    metadata:
      labels:
        k8s-app: webhook
    spec:
      volumes:
        - name: config
          configMap:
            name: alertmanager-webhook
      containers:
        - name: alertmanager-webhook
          # 企业微信机器人的情况需将如下的image值改为uhub.service.ucloud.cn/uk8s/prometheus-webhook-wechat:v2.0.0
          image: uhub.service.ucloud.cn/uk8s/prometheus-webhook-dingtalk:v2.0.0
          args:
            - --web.listen-address=:8060
            - --config.file=/config/config.yaml
          volumeMounts:
            - name: config
              mountPath: /config
          resources:
            limits:
              cpu: 100m
              memory: 100Mi
          ports:
            - name: http
              containerPort: 8060
```

#### 4.3 添加接收人

在控制台「收发设置」页面「接收人」版面点击「添加」，根据类型在 Webhook 地址栏中填写

钉钉机器人: http://alertmanager-webhook.uk8s-monitor.svc/dingtalk/webhook1/send

企业微信机器人: http://alertmanager-webhook.uk8s-monitor.svc/wechat/webhook/send
