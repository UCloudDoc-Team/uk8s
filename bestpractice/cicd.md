
## 基于Jenkins的CI/CD实践

[TOC]

### 一、概要

提到K8S环境下的CI/CD，可以使用的工具有很多，比如Jenkins、Gitlab CI、新兴的drone等，考虑到大多公司在VM环境下都采用 Jenkins 集群来搭建符合需求的 CI/CD 流程，这里先给介绍大家下Kubernetes+Jenkins的CI/CD方案。

#### 1、Jenkins架构

![](/images/bestpractice/jenkins-arch.png)

Jenkins Master 和 Jenkins Slave 以 Pod 形式运行在 Kubernetes 集群的 Node 上，Master是常驻服务，所有的配置数据都存储在一个 Volume 中，Slave 不是一直处于运行状态，它会按照需求动态的创建并自动删除。

#### 2、工作原理

当 Jenkins Master 接受到 Build 请求时，会根据配置的 Label 动态创建一个运行在 Pod 中的 Jenkins Slave 并注册到 Master 上，当运行完 Job 后，这个 Slave 会被注销并且这个 Pod 也会自动删除，恢复到最初状态。

#### 3、优势
相对于部署在虚拟机环境下的Jenkins 一主多从架构，将Jenkins部署到K8S会带来以下好处：

* **服务高可用:**当 Jenkins Master 出现故障时，Kubernetes 会自动创建一个新的 Jenkins Master 容器，并且将 Volume 分配给新创建的容器，保证数据不丢失，从而达到集群服务高可用。

* **动态伸缩:** 合理使用资源，每次运行 Job 时，会自动创建一个 Jenkins Slave，Job 完成后，Slave 自动注销并删除容器，资源自动释放，而且 Kubernetes 会根据每个资源的使用情况，动态分配 Slave 到空闲的节点上创建，降低出现因某节点资源利用率高，还排队等待在该节点的情况。

* **扩展性好：** 当 Kubernetes 集群的资源严重不足而导致 Job 排队等待时，可以很容易的添加一个 Kubernetes Node 到集群中，从而实现扩展。

### 二、部署Jenkins

1、 为了管理方便，我们把需要创建的资源都部署在一个名为 jenkins 的 namespace 下面，所以我们需要添加创建一个 namespace：

```
kubectl create namespace jenkins 
```

2、 声明一个PVC对象，后面我们要将Jenkins容器的 /var/jenkins_home 目录挂载到了这个名为PVC对象上面。

* 如果您使用的k8s版本大于等于1.14，且没有使用快杰云主机，请部署。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/cicd/yaml_jenkins_jenkins-pvc.yaml
```

* 如果您使用的k8s版本大于等于1.14，且使用快杰云主机，请部署。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/cicd/yaml_jenkins_jenkins-pvc-rssd.yaml
```

* 如果您使用的k8s版本小于1.14，请部署。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/cicd/yaml_jenkins_jenkins-pvc-1.13.yaml
```

3、 以Deployment方式部署Jenkins master,为了演示方便，我们还使用LoadBalancer类型的service将其暴露到外网。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/cicd/yaml_jenkins_jenkins.yaml
```

4、 等到服务启动成功后，我们就可以根据LoadBalancer的IP（即EXTERNAL-IP），访问 jenkins 服务了，并根据提示信息进行安装配置。

```
bash-4.4# kubectl get svc -n jenkins
NAME      TYPE           CLUSTER-IP       EXTERNAL-IP    PORT                        AGE
jenkins   LoadBalancer   172.17.201.210   106.75.98.80   8080:33651/TCP,50000:43748/TCP   4d21h
```

5、 创建一个名为jenkins2的ServiceAccount，并且为其赋予特定的权限，后面配置Jenkins-Slave我们会用到。

```
kubectl apply -f https://gitee.com/uk8s/uk8s/raw/master/yaml/cicd/yaml_jenkins_jenkins-rbac.yaml
```

### 三、安装Kubernetes插件

1、 前面我们已经获取到Jenkins的外网IP地址，我们直接在浏览器输入EXTERNAL-IP:8080，即可打开Jenkins页面，提示需要输入初始化密码：

![](/images/bestpractice/unlock.png)

2、 我们通过kubectl log获取jenkins容器的日志来获取初始化密码

```
kubectl logs jenkins-deployment-66b865dbd-xvmdz -n jenkins
```

![](/images/bestpractice/passget.png)

3、 选择推荐安装，添加完管理员帐号admin，即可进入到 jenkins 主界面。

4、 接下来安装jenkins依赖插件清单——kubernets plugin，让他能够动态的生成 Slave 的 Pod。 点击 Manage Jenkins -> Manage Plugins -> Available -> Kubernetes plugin勾选安装即可。 

![](/images/bestpractice/installplugin.png)

安装插件相对较慢，请耐心等待，并且由于是在线安装，集群需要开通外网，请[开启natgw](https://console.ucloud.cn/vpc/natgw)来使node节点通外网

### 四、配置Jenkins

接下来将进入最重要的一个步骤，在Kubernetes插件安装完毕后，我们需要配置Jenkins和Kubernetes参数，使Jenkins连接到UK8S集群，并能调用Kubernetes API 动态创建Jenkins Slave，执行构建任务。

首先点击 Manage Jenkins —> Configure System，进入到系统设置页面。滚动到页面最下方，然后点击Add a new cloud —> 选择 Kubernetes，开始填写 Kubernetes 和 Jenkins 配置信息。

1、 输入UK8S Apiserver地址，以及服务证书key。

以上两个参数信息，可以在[UK8S集群详情页](https://console.ucloud.cn/uk8s/manage)的内网或外网集群凭证中获取。"服务证书key"为集群凭证中的certificate-authority-data字段内容，进行base64解码，将解码后的内容复制到输入框即可。

![](/images/bestpractice/certificate.png)

2、 填写集群Namespace、上传凭据、Jenkins地址

Namespace此处填写之前创建Namespace即可，此处为jenkins。凭证处，点击”Add“，凭证类型选择"Secret file"，将[UK8S集群详情页](https://console.ucloud.cn/uk8s/manage)全部内容复制下来，保存为kubeconfig上传。


![](/images/bestpractice/pinju.png)

![](/images/bestpractice/kubeconfig.jpeg)


3、 点击”连接测试“，如果出现 Connection test successful 的提示信息证明 Jenkins 已经可以和 Kubernetes 系统正常通信了

4、 接下来，我们点击”添加Pod模板“，这个Pod模板即Jenkins-slave pod的模板。

* namespace，我们这里填 ”jenkins“
* 标签列表，这里我们填 ”jnlp-slave“，这个标签我们在后面创建Jobs会用到，非常重要。
* 用法，选择 ”尽可能使用这个节点“
* Docker镜像，填写”uhub.service.ucloud.cn/library/jenkins:jnlp“，这个容器镜像是我们CI/CD的运行环境。
* 工作目录，填写”/home/jenkins“

![](/images/bestpractice/podtemplate.png)

选择添加卷，主机路径和挂载路径都填写为”/var/run/docker.sock“，使得jenkins-slave可以使用宿主机的Docker，让我们可以在容器中进行镜像Build等操作。


![](/images/bestpractice/pod2.png)

点击最下方的Advanced，Service Account 输入jenkins2，这是我们之前创建的SA。

![](/images/bestpractice/pod3.png)

其他几个参数由于只是演示，我们都使用默认值，在实际使用的时候，请自行选择合理的参数。到这里我们的 Kubernetes Plugin 插件就算配置完成了。


### 五、运行一个简单任务

Kubernetes 插件的配置工作完成了，接下来我们就来添加一个 Job 任务，看是否能够在 Slave Pod 中执行，任务执行完成后看 Pod 是否会被销毁。


1、 在 Jenkins 首页点击create new jobs，创建一个测试的任务，输入任务名称，然后我们选择 Freestyle project 类型的任务，点击OK。

![](/images/bestpractice/job1.png)

2、 在任务配置页，最下面的 Label Expression 这里要填入jnlp-slave，就是前面我们配置的 Slave Pod 中的 Label，这两个地方必须保持一致

![](/images/bestpractice/job2.png)

3、 在任务配置页的 Build 区域，选择Execute shell，输入一个简单的测试命令，并点击保存。

![](/images/bestpractice/job3.png)

4、 点击查看Console output，查看任务运行情况。

![](/images/bestpractice/job4.png)

到这里我们就完成了使用 Kubernetes 动态生成 Jenkins Slave 的方法。

### 六、运行一个pipeline任务

#### 1. pipeline介绍

Pipeline，简单来说，就是一套运行在 Jenkins 上的工作流（流水线）框架，将原来独立运行于单个或者多个节点的任务连接起来，实现单个任务难以完成的复杂流程编排和可视化的工作。Jenkins Pipeline 有几个核心概念：

* **Node：**节点，一个 Node 就是一个 Jenkins 节点，是执行 Step 的具体运行环境，比如我们之前动态运行的 Jenkins Slave 就是一个 Node 节点。

* **Stage：**阶段，一个 Pipeline 可以划分为若干个 Stage，每个 Stage 代表一组操作，比如：Build、Test、Deploy，Stage 是一个逻辑分组的概念，可以跨多个 Node。

* **Step：**步骤，Step 是最基本的操作单元，可以是打印一句话，也可以是构建一个 Docker 镜像，由各类 Jenkins 插件提供，比如命令：sh ‘make’，就相当于我们平时 shell 终端中执行 make 命令一样。

#### 2. 创建pipeline 任务

Pipeline 有两种创建方法，一是直接在 Jenkins 的 Web UI 界面中输入脚本，二是通过创建一个 Jenkinsfile 脚本文件放入项目源码库中，这里为了方便演示，我们使用在 Web UI 界面中输入脚本的方式来运行Pipeline。

1、 点击”new item“，输入Job名称，选择Pipeline，点击"OK"。

![](/images/bestpractice/pipeline1.png)

2、 在最下方的pipeline 脚本部分，输入以下脚本内容，并点击保存


```
node('jnlp-slave') {
    stage('Clone') {
      echo "1.Clone Stage"
    }
    stage('Test') {
      echo "2.Test Stage"
    }
    stage('Build') {
      echo "3.Build Stage"
    }
    stage('Deploy') {
      echo "4. Deploy Stage"
    }
}

```


> 上面的脚本内容中，我们给 node 添加了一个 jnlp-slave 标签，指定这个pipeline的4个stage，都运行在jenkins的slave节点中。


3、 任务创建好之后，点击”立即构建“，我们可以通过kubectl命令发现UK8S集群中正启动一个新的pod用于构建任务。

```
bash-4.4# kubectl get po -n jenkins
NAME                                  READY   STATUS              RESTARTS   AGE
jenkins-deployment-6f9d84f745-lcs67   1/1     Running             0          5d2h
jnlp-0qn7x                            0/1     ContainerCreating   0          1s

```

4、 回到 Jenkins 的 Web UI 界面中查看 本次构建历史的 Console Output，也可以类似如下的信息，表明构建成功

```
Console Output
Started by user kukkazhang
Running in Durability level: MAX_SURVIVABILITY
[Pipeline] Start of Pipeline
[Pipeline] node
Still waiting to schedule task
‘jnlp-7m9dl’ is offline
Agent jnlp-7m9dl is provisioned from template Kubernetes Pod Template
Agent specification [Kubernetes Pod Template] (jnlp-slave): 
* [jnlp] uhub.service.ucloud.cn/library/jenkins:jnlp

Running on jnlp-7m9dl in /home/jenkins/workspace/testhelloworld
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Clone)
[Pipeline] echo
1.Clone Stage
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Test)
[Pipeline] echo
....
....
6. Deploy Stage
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
Finished: SUCCESS
```

### 七、在UK8S中部署应用


上面我们已经知道了如何在 Jenkins Slave 中构建Pipeline任务，那么如何通过Jenkins来部署一个原生的 Kubernetes 应用呢？

一般而言，在Kubernetes中部署一个业务的流程大致如下：

* 1.编写代码
* 2.测试
* 3.编写 Dockerfile
* 4.构建 Docker 镜像
* 5.推送 Docker 镜像到仓库
* 6.编写 Kubernetes YAML 文件
* 7.更改 YAML 文件中的 Docker 镜像 TAG
* 8.利用 kubectl 工具部署应用

这是我们人肉部署应用的流程，现在我们要做的是把上面这些流程放入 Jenkins 中来自动帮我们完成，从测试到更新 YAML 文件属于 CI 流程，后面部署属于 CD 的范畴。下面我们现在要来编写一个 Pipeline 的脚本，帮我们自动完成以上工作。

**开始之前的准备工作**

为了演示方便，我们准备了一个简单的helloworld程序，并将业务代码、dockerfile、yaml 放置 [github代码仓库](https://github.com/ucloud/uk8s-demo.git),分支:jenkins-cicd,接下来我们来逐步编写Pipeline脚本。

1、clone代码，我们将git commit的记录作为后面构建的镜像 tag，让镜像tag和git commit记录对应起来，方便后续排查问题。

```
 stage('Clone') {
        echo "1.Clone Stage"
        git branch: 'jenkins-cicd', url: "https://github.com/ucloud/uk8s-demo.git"
        script {
            build_tag = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        }
}
```

2、编写测试用例，这里涉及到业务逻辑，我们选择略过。

```
stage('Test') {
    echo "2.Test Stage"
}

```

3、构建镜像，镜像tag便是我们之前在clone代码阶段定义的build_tag，注意将"jenkins_k8s_cicd"更换成您自己的uhub仓库名。

```
stage('Build') {
        echo "3.Build Docker Image Stage"
        sh "docker build -t uhub.service.ucloud.cn/jenkins_k8s_cicd/jenkins_k8s_cicd:${build_tag} ."
}

```

4、将镜像推送到镜像仓库。我们选择将镜像推送到Uhub的私人仓库中去，因此我们还需要登录到uhub，注意将"jenkins_k8s_cicd"更换成您自己的uhub仓库名。

```
  stage('Push') {
        echo "4.Push Docker Image Stage"
        withCredentials([usernamePassword(credentialsId: 'uhub', passwordVariable: 'uhubPassword', usernameVariable: 'uhubUser')]) {
            echo "${uhubPassword}"
            echo "${uhubUser}"
            sh "docker login -u ${uhubUser} -p ${uhubPassword} uhub.service.ucloud.cn"
            sh "docker push uhub.service.ucloud.cn/jenkins_k8s_cicd/jenkins_k8s_cicd:${build_tag}"
        }
}

```

为了保证账户安全，上面的脚本中，我们用了Jenkins的一个"凭据"功能。在首页点击 Credentials -> Stores scoped to Jenkins 下面的 Jenkins -> Global credentials (unrestricted) -> 左侧的 Add Credentials：添加一个 Username with password 类型的认证信息。

输入 uhub 的用户名和密码，ID 部分我们输入uhub，注意，这个值非常重要，需要与Pipeline 中的脚本保持一致。

![](/images/bestpractice/1.png)

5、更新yaml文件，这里我们只是将yaml中的镜像tag更换成最新构建出的镜像tag。

```
stage('YAML') {
    echo "5. Change YAML File Stage"
    sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s.yml"
}

```

6、应用发布。我们直接使用kubectl apply命令来更新应用，还记得我们之前创建的名为jenkins2的ServiceAccount吗？能成功发布应用，还有赖我们为jenkins2配置的权限呢。

```
stage('Deploy') {
    echo "6. Deploy Stage"
    sh "kubectl apply -f k8s.yml"
}

```

7、上面我们把pipeline中的每个Stage都讲述了一遍，下面我们把6个stage的脚本合并到一起，创建一个新的流水线任务，体验下完整的应用发布流程吧。

```
node('jnlp-slave') {
    stage('Clone') {
      echo "1.Clone Stage"
      git branch: 'jenkins-cicd', url: 'https://github.com/ucloud/uk8s-demo.git'
      script {
          build_tag = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
      }

    }
    stage('Test') {
      echo "2.Test Stage"
    }
    stage('Build') {
      echo "3.Build Docker Image Stage"
      sh "docker build -t uhub.service.ucloud.cn/jenkins_k8s_cicd/jenkins_k8s_cicd:${build_tag} ."

    }
    stage('Push') {
      echo "4.Push Docker Image Stage"
      withCredentials([usernamePassword(credentialsId: 'uhub', passwordVariable: 'uhubPassword', usernameVariable: 'uhubUser')]) {
            echo "${uhubPassword}"
            echo "${uhubUser}"
            sh "docker login -u ${uhubUser} -p ${uhubPassword} uhub.service.ucloud.cn"
            sh "docker push uhub.service.ucloud.cn/jenkins_k8s_cicd/jenkins_k8s_cicd:${build_tag}"
        }

    }
    stage('YAML') {
      echo "5. Change YAML File Stage"
      sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s.yml"
    }
    stage('Deploy') {
      echo "6. Deploy Stage"
      sh "kubectl apply -f k8s.yml"
    }
}
```

![](/images/bestpractice/2.png)



