{{indexmenu_n>40}}
======管理应用======


### 更新应用

按照前文已完成了应用的安装，当有新的版本发布的时候或者用户想要更新以发布的应用，用户可以通过 **helm upgrade** 命令对已发布应用进行更新升级。


#### 方法一，获取values.yaml执行文件更新

通过 **helm fetch** 命令获取到安装包
```
helm fetch stable/tomcat --untar
```
获取到tomcat的安装包(chart)，我们可以看到这个安装包内的结构
```
tomcat
├── Chart.yaml
├── README.md
├── templates
│   ├── appsrv-svc.yaml
│   ├── appsrv.yaml
│   ├── _helpers.tpl
│   └── NOTES.txt
└── values.yaml
```
其中values.yaml会记录整个安装包的变量信息，方便用户进行修改查看，用户可以通过修改values.yaml后，执行 **helm upgrade** 进行更新操作
```
helm upgrade -f values.yaml giggly-leopard stable/tomcat
```


#### 方法二，使用命令进行更新

通过 **helm inspect** 命令查看可以配置的选项
```
helm inspect values stable/tomcat
```
通过上一条命令获取到可修改的选项后，通过 **helm upgrade** 进行更新操作
```
helm upgrade --set service.externalPort=8080 giggly-leopard stable/tomcat
```

#### 方法三，升级新的版本

获取新的版本号需要通过 **helm repo update** 更新本地查询文件信息。
==通过 --version 命令可以指定更新到的版本，如果没有指定，则默认使用最新的版本。==

```
helm upgrade --version 0.2.0 giggly-leopard stable/tomcat
```
**注：通过Helm更新应用如果更新失败，会自动回滚**

### 回滚应用

Helm会将应用发布的信息记录在ConfigMap中，可以执行 **helm history** 命令查询历史版本信息

```
helm history giggly-leopard
```
通过 **helm rollback** 进行回滚。
```
helm rollback giggly-leopard 1
```

### 删除应用

通过 **helm delete** 进行应用删除。
```
helm delete --purge giggly-leopard
```
==helm的删除操作会将资源释放，但保留应用信息，并标记为 DELETE 状态，可通过 --deleted 查看已经删除的Release， DELETE 状态的应用历史纪录是会继续保存的，切命名不可再次使用。==
```
helm list --deleted
```
==上面的删除命令中加入中 --purge，这个参数将会永久删除这个应用的所有信息，重新建立的时候还可以使用该命名。==