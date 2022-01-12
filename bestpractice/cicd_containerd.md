## 基于Jenkins的CI/CD实践(containerd版本)

### 前言

在之前的方案中，我们介绍了Docker+Jenkins实现容器镜像构建、业务部署的方案，该方案需要直接挂载docker socket文件到Jenkins slave容器中。由于UK8S
1.20以后的版本将采用Containerd,因此该方案不再适用。

这篇文章中，我们介绍基于Kaniko+Jenkins的CICD方案，Kaniko是谷歌开源的一款用来构建容器镜像的工具。与docker不同，Kaniko 并不依赖于Docker
daemon进程，完全是在用户空间根据Dockerfile的内容逐行执行命令来构建镜像，这就使得在一些无法获取 docker daemon 进程的环境下也能够构建镜像，比如在标准的Kubernetes
Cluster上。[关于kaniko](https://github.com/GoogleContainerTools/kaniko)

### 一、部署Jenkins

1、 为了管理方便，我们把需要创建的资源都部署在一个名为 jenkins 的 namespace 下面，所以我们需要添加创建一个 namespace：

```
kubectl create namespace jenkins
```

2、 声明一个PVC对象，后面我们要将Jenkins容器的 /var/jenkins_home 目录挂载到了这个名为PVC对象上面。

- 如果您使用的k8s版本大于等于1.14，且没有使用快杰云主机，请部署。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/cicd/yaml_jenkins_jenkins-pvc.yaml
```

- 如果您使用的k8s版本大于等于1.14，且使用快杰云主机，请部署。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/cicd/yaml_jenkins_jenkins-pvc-rssd.yaml
```

- 如果您使用的k8s版本小于1.14，请部署。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/cicd/yaml_jenkins_jenkins-pvc-1.13.yaml
```

3、 以Deployment方式部署Jenkins master,为了演示方便，我们还使用LoadBalancer类型的service将其暴露到外网。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins-deployment
  namespace: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      securityContext:
        fsGroup: 1000
      containers:
      - name: jenkins
        image: uhub.service.ucloud.cn/uk8s/jenkins:2.295-centos
        resources:
          limits:
            memory: "8G"
          requests:
            memory: "4G"
        ports:
        - containerPort: 8080
          name: web
          protocol: TCP
        - containerPort: 50000
          name: agent
          protocol: TCP
        volumeMounts:
        - name: jenkins-strorage
          mountPath: /var/jenkins_home
      volumes:
      - name: jenkins-strorage
        persistentVolumeClaim:
          claimName: jenkins-pvc-claim
---
apiVersion: v1
kind: Service
metadata:
  name: jenkins
  namespace: jenkins
  labels:
    app: jenkins
spec:
  type: LoadBalancer
  ports:
    - name: web
      port: 8080
      targetPort: web
    - name: agent
      port: 50000
      targetPort: agent
  selector:
    app: jenkins
```

4、 等到服务启动成功后，我们就可以根据LoadBalancer的IP（即EXTERNAL-IP），访问 jenkins 服务了，并根据提示信息进行安装配置。

```
bash-4.4# kubectl get svc -n jenkins
NAME      TYPE           CLUSTER-IP       EXTERNAL-IP    PORT                        AGE
jenkins   LoadBalancer   172.17.201.210   106.75.98.80   8080:33651/TCP,50000:43748/TCP   4d21h
```

### 三、安装Kubernetes插件

1、 前面我们已经获取到Jenkins的外网IP地址，我们直接在浏览器输入EXTERNAL-IP:8080，即可打开Jenkins页面，提示需要输入初始化密码：

![](/images/bestpractice/unlock.png)

2、 我们通过kubectl log获取jenkins容器的日志来获取初始化密码

```bash
kubectl -n jenkins get pod 

kubectl -n jenkins logs jenkins-deployment-xxxxxxx
```

![](/images/bestpractice/passget.png)

3、 进入安装插件页面，在配置之前，先开启代理兼容，访问"http://exter-ip:8080/configureSecurity/"，勾选启用代理兼容。这一步可能会出现报错，多尝试几次即可。

![](/images/bestpractice/agent.png)

4、 选择推荐安装，安装完毕后，添加管理员帐号，即可进入到 jenkins 主界面。

5、 接下来安装jenkins依赖插件清单——kubernets plugin，让他能够动态的生成 Slave 的 Pod。 点击 Manage Jenkins -> Manage Plugins
-> Available -> Kubernetes plugin勾选安装即可。

![](/images/bestpractice/installplugin.png)

安装插件相对较慢，请耐心等待，并且由于是在线安装，集群需要开通外网，请[开启natgw](https://console.ucloud.cn/vpc/natgw)来使node节点通外网

### 四、配置Jenkins

接下来将进入最重要的一个步骤，在Kubernetes插件安装完毕后，我们需要配置Jenkins和Kubernetes参数，使Jenkins连接到UK8S集群，并能调用Kubernetes API
动态创建Jenkins Slave，执行构建任务。

首先点击 Manage Jenkins —> Configure System，进入到系统设置页面。滚动到页面最下方，然后点击Add a new cloud —> 选择 Kubernetes，开始填写
Kubernetes 和 Jenkins 配置信息。

1、 输入UK8S Apiserver地址，以及服务证书key。

以上两个参数信息，可以在[UK8S集群详情页](https://console.ucloud.cn/uk8s/manage)的内网或外网集群凭证中获取。"服务证书key"为集群凭证中的certificate-authority-data字段内容，进行base64解码，将解码后的内容复制到输入框即可。

![](/images/bestpractice/certificate.png)

2、 填写集群Namespace、上传凭据、Jenkins地址

Namespace此处填写之前创建Namespace即可，此处为jenkins。凭证处，点击”Add“，凭证类型选择"Secret
file"，将[UK8S集群详情页](https://console.ucloud.cn/uk8s/manage)全部内容复制下来，保存为kubeconfig上传。

![](/images/bestpractice/pinju.png)

![](/images/bestpractice/kubeconfig.jpeg)

3、 点击”连接测试“，如果出现 Connection test successful 的提示信息证明 Jenkins 已经可以和 Kubernetes 系统正常通信了

### 五、为kaniko配置凭证

创建一个配置kaniko推送到uhub镜像的凭证，找一台有安装docker的镜像，登录一次uhub：

```bash
docker login uhub.service.ucloud.cn -u user@ucloud.cn
```

登入成功之后，在Home目录会有一个 .docker/config.json，将文件内内容复制进uk8s集群中，创建一个secret供kaniko容器使用。

```bash
kubectl create secret generic regcred --from-file=/home/ubuntu/.docker/config.json -n jenkins
```

到此配置结束。

### 六、创建Job

Kubernetes 插件的配置工作完成了，接下来我们就来添加一个 Job 任务，看是否能够在 Slave Pod 中执行，任务执行完成后看 Pod 是否会被销毁。

为了方便使用，我们提供了一个golang项目的ci/cd demo(https://github.com/DragonTwoYang/kankio-test.git)，
里面包含了完整的编译，构建镜像，部署流程。原方案中关于Slave Pod以及CICD的配置信息都配置在.jenkinsfile中，你可以根据项目自身需求更改jenkinsfile文件。

1、 在 Jenkins 首页点击create new jobs，创建一个测试的任务，输入任务名称，然后我们选择“流水线”类型的任务，点击OK。

![](/images/bestpractice/job6281.png)

2、 在任务配置页，这里我们选择GitHub项目，输入kaniko的任务地址。

![](/images/bestpractice/job6282.png)

3、 在任务配置页的流水线区域，选择Pipeline script from SCM，并选择 Master 分支以及 Jenkinsfile的文件路径。。

![](/images/bestpractice/job6283.png)
