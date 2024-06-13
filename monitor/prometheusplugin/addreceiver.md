# 添加接收人

监控中心支持添加接收人邮箱、企业微信及钉钉三种告警形式，请在 UK8S 控制台「监控中心」→「收发设置」进行配置。

## 1. 配置发件服务器

配置接收人前，需要先设置发件人邮箱信息。目前发送信息是通过邮箱发送。 

不同的邮件服务提供商对于发件服务器的配置都有较为详细的说明；这里强调两点：

1. 目前尚不支持TLS，因此请勿填写TLS端口；
2. 密码建议为客户端密码，填写邮箱登录密码可能无法发送邮件。

![](/images/monitor/prometheus/编辑发件服务器.png)

## 2. 配置邮件接收人

支持添加多个邮件接收人

![](/images/prometheus/addemial.jpg)

- 名称： 收件人名称
- 邮箱地址： 收件的邮箱地址

## 3. 配置企业微信接收人

> 注：企业微信机器人类型请参考 '配置webhook接收人(钉钉/企业微信机器人方式)' 方式

在使用微信接收人之前，我们必须在微信管理后台创建一个应用并获取应用ID、企业ID、应用秘钥、部门ID、企业微信用户ID等信息，需要咨询您的企业微信负责人或者管理员方可获取相关信息。详细alertmanager配置的官方文档请参考[这里](https://prometheus.io/docs/alerting/latest/configuration/#wechat_config)

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

> 企业微信如果收不到告警信息，还需要设置可信任IP，可参考企业微信[官方文档](https://developer.work.weixin.qq.com/devtool/query?e=60020)。管理员登录企业微信web页面，在“应用管理”中点击自建的应用进入详情页；找到“企业可信IP”进行配置。填写的IP为访问企业微信的IP（一般为集群关联的NAT网关的外网弹性IP）。


![](/images/prometheus/weixinerrcode.png)

## 4. 配置webhook接收人(钉钉/企业微信机器人方式)

#### 4.1 创建钉钉/企业微信机器人，获取 Webhook 地址

在使用webhook接收人(钉钉/企业微信机器人方式)之前，我们必须在钉钉/企业微信管理后台创建自定义机器人，并获取其 Webhook 地址，详情参考钉钉/企业微信相关文档。

#### 4.2 部署配置文件

AlertManager 不支持直接接入钉钉/企业微信告警，需要进行适配转换，以下是参考社区的示例部署 yaml 文件。

> 请根据yaml中的提示，结合自身场景来替换yaml中的webhook地址以及image

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
          # 替换image值:
          # 企业微信机器人: uhub.service.ucloud.cn/uk8s/prometheus-webhook-wechat:v2.0.0
          # 钉钉机器人: uhub.service.ucloud.cn/uk8s/prometheus-webhook-dingtalk:v2.0.0
          image: xxx:xxx
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

## 5. 配置webhook接收人(微信公众号方式)

#### 5.1 创建公众号以及模板，获取公众号的 appid、secret 以及模板的 templateid

该告警方式基于微信公众号的模板消息实现，使用时请遵守[模板消息运营规范](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Template_Message_Operation_Specifications.html)

模板消息内容可参考如下(模板名称随意)
```
告警状态: {{ status.DATA }}
告警类型: {{ alertname.DATA }}
告警级别: {{ severity.DATA }}
告警实例: {{ instance.DATA }}
告警内容: {{ message.DATA }}
告警时间: {{ startsat.DATA }}
```

#### 5.2 部署配置文件

AlertManager 同样不支持直接接入微信公众号告警，需要进行适配转换

> 请根据yaml中的提示，结合自身场景来替换yaml中的配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-webhook
  namespace: uk8s-monitor
data:
  config.yaml: |
    # 请替换为您的微信公众号的appid
    appid: "xxx"
    # 请替换为您的微信公众号的secret
    secret: "xxx"
    # 请替换为您的微信公众号模板的templateid
    templateid: "xxx"
    # 告警组 name为组名，chatids下为该告警组下的用户的openid
    chatgroups:
      - name: uk8s
        chatids:
          - "openid1"
      - name: all
        chatids:
          - "openid1"
          - "openid2"
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
  replicas: 1
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
          image: uhub.service.ucloud.cn/uk8s/prometheus-webhook-wechat-public:v2.0.0
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

#### 5.3 添加接收人

在控制台「收发设置」页面「接收人」版面点击「添加」，在 Webhook 地址栏中填写 

http://alertmanager-webhook.uk8s-monitor.svc/wechat/{groupname}/send  

其中{groupname}为config.yaml中对应的chatgroups.name的名称