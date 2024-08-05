# 推理常用基础镜像

Uhub提供了一系列的推理相关基础容器镜像，用户可以基于这些基础镜像构建自定义镜像，用于部署推理服务。

### 镜像列表：


| 镜像名称       | tag信息    | 源仓库   |  
| :----------: | :----------: | :----------: | 
| pytorch/pytorch       | 2.4.0-cuda11.8-cudnn9-runtime <br/> 2.4.0-cuda11.8-cudnn9-runtime   | pytorch/pytorch | 
| nvida/pytorch      | 24.07-py3 <br/> 24.06-py3   | nvcr.io/nvidia/pytorch | 
| vllm/vllm-openai       | v0.5.3 <br/> v0.5.2   | vllm/vllm-openai | 
| jupyter/tensorflow-notebook  | x86_64-ubuntu-22.04 |    jupyter/tensorflow-notebook     | 
| nvidia/cuda  | 12.5.1-cudnn-runtime-ubuntu20.04 <br/> 12.5.1-cudnn-runtime-ubuntu22.04 |    nvcr.io/nvidia/cuda     | 

### 如何获取
上述列表中所有镜像已经同步仓库：ucloudai，镜像地址规则如下所示：
```
uhub.service.ucloud.cn/ucloudai/<镜像名称>:tag
```


例如：下载`vllm/vllm-openai`镜像的`v0.5.3`版本，可使用如下命令：
```sh
docker pull uhub.service.ucloud.cn/ucloudai/vllm/vllm-openai:v0.5.3
```
