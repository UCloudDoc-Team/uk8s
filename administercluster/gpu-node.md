# 使用gpu节点

uk8s提供的标准镜像中，已安装nvidia驱动，并在集群中预先安装nvidia-device-plugin，所以客户使用uk8s集群时可直接使用gpu节点。

## 注意事项
1. 默认情况下，容器之间不共享 GPU，每个容器可以请求一个或多个 GPU。无法请求 GPU 的一小部分。
2. 集群的 Master 节点暂不支持设置为 GPU 机型。
3. 使用高性价比显卡的云主机机型（如高性价比显卡3、高性价比显卡5、高性价比显卡6）作为节点时，需使用标准镜像`Ubuntu 20.04-高性价比`
    - 创建集群
      ![](/images/gpu/image-0.png)
      ![](/images/gpu/image-1.png)
    - 新增Node节点
      ![](/images/gpu/image-2.png)
    - 支持可用区
        - 华北二A
        - 上海二B
        - 北京二B