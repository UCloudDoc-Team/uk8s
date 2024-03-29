## 集群更新凭证

UK8S 支持用户通过 kubectl 工具连接 kubernetes 集群，详见[使用 kubectl 操作集群](/uk8s/manageviakubectl/intro_of_kubectl)

### 更新新 Token 访问集群

集群凭证现在展示的为 Token 访问方式（非原证书访问方式），按照上面的文档链接操作，我们已经复制信息至`~/.kube/config`文件中，集群已经可以正常连接访问。

![](/images/manageviakubectl/cluster-info.png)

如您将您的凭证有对外展示过并且您认为目前凭证存在泄漏的风险，可以通过点击更新凭证将集群凭证进行刷新，刷新后，老的集群凭证将无法继续使用，需要从 UK8S 页面重新获取复制。

![](/images/manageviakubectl/reset-token.png)

### 妥善保管好您的证书访问集群

UK8S 的 master 节点默认安装了 kubectl 工具，配置的为内网证书访问凭证，证书访问凭证将不会被刷新，请您妥善保管好您的证书安全
