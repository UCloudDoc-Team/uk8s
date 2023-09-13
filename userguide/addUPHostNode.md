# 添加已有主机-裸金属

目前部分地域（如乌兰察布，上海）开放支持已有裸金属资源加入集群； 在集群详情页，节点列表页，点击`添加已有主机`，类型选择UPHost，即可添加已有裸金属资源。

具体支持情况如下：
> 若有需求可以先找产品确认适配情况
- 支持裸金属机型：
  1. CPU裸金属：公有云部分标准云盘裸金属、本地盘裸金属机型
  2. GPU裸金属：高性能计算显卡5(BM.3090.I8.M7)  
- 集群版本要求：1.20.6及以上   
- CSI版本要求：23.07.24及以上
- CNI版本要求：v1.2.0及以上   

## 操作指引

### 一、在集群列表页点击详情，进入集群详情页
<img width="1434" alt="image" src="https://github.com/UCloudDoc-Team/uk8s/assets/124045035/f569021d-d766-43de-a722-d7b7288661e4">

### 二、进入集群节点页
<img width="1432" alt="image" src="https://github.com/UCloudDoc-Team/uk8s/assets/124045035/9a22256c-6eee-4b15-917e-d7b5a555b541">

### 三、点击`添加已有主机`
选择UPHost，勾选目标裸金属资源，确认提交即可。    

<img width="572" alt="image" src="https://github.com/UCloudDoc-Team/uk8s/assets/124045035/6532840c-6e38-4d20-acad-0548f0d621ef">

