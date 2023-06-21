# 制作自定义镜像

## 一、前言

为了满足用户对 UK8S 节点的个性化需求，除了标准镜像外，UK8S 的 Node 节点也支持自定义镜像。
但务必使用 UK8S 的标准镜像来制作自定义镜像，否则可能导致集群无法创建或节点无法添加。

下面介绍如何基于标准镜像制作自定义镜像，以及注意事项。
本文档介绍的自定义镜像制作过程是完全自动化的，制作过程中无需人工干预。用户需要具备简单的
shell 编程或 [Ansible][2] 使用经验。

由于香港可用区到国内和全球其它可用区的网速较快，进行镜像复制时可以减少耗时。
本文介绍的方法是在香港地域进行镜像构建，然后复制到其它可用区。
请保证在香港可用区有足够的云主机配额。

## 二、制作自定义镜像流程

1. 安装 Packer

安装 [Packer][1]
工具，使用该工具可以方便地创建并分发自定义镜像到你需要的可用区。下面介绍了MacOS 安装方式，其他环境请参考[Packer官方文档](https://developer.hashicorp.com/packer/downloads?product_intent=packer)

MacOS 用户可以通过以下命令安装 Packer：

```bash
brew install packer
```

Packer 只负责创建云主机，在云主机中安装配置软件需要使用命令行脚本或 Ansible。
本文档给的示例使用 Ansible，也可以转换成其它等价工具。下面介绍了Ansible 的MacOS 安装方式，其他环境请参考[Ansible 官方文档](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#managed-node-requirements)。

MacOS 用户可以通过以下命令安装 Ansible：

```bash
brew install ansible
```

2. 准备公钥、私钥及项目 ID

请在 UCloud 控制台的`账号管理 -> API 密钥`创建或使用现有的公钥及私钥。
请在 UCloud 控制台的`访问控制 -> 项目管理`中查找到存放即将创建的自定义镜像所属项目。
请将公钥、私钥和项目 ID 设置到环境变量中，命令示例如下：

    export UCLOUD_PUBLIC_KEY="公钥"
    export UCLOUD_PRIVATE_KEY="私钥"
    export UCLOUD_PROJECT_ID="项目 ID"

以上命令建议设置到 shell 的初始化文件中，如.zshrc 或.bashrc 等。

3. 编写 Packer 配置文件

假定该配置文件名称为 `custom.json`。

    {
      "variables": {
        "ucloud_public_key": "{{env `UCLOUD_PUBLIC_KEY`}}",
        "ucloud_private_key": "{{env `UCLOUD_PRIVATE_KEY`}}",
        "ucloud_project_id": "{{env `UCLOUD_PROJECT_ID`}}"
      },

      "builders": [{
        "type": "ucloud-uhost",
        "public_key": "{{user `ucloud_public_key`}}",
        "private_key": "{{user `ucloud_private_key`}}",
        "project_id": "{{user `ucloud_project_id`}}",
        "region": "hk",
        "availability_zone": "hk-02",
        "instance_type": "o-standard-2",
        "source_image_id": "<REPLACE_THE_UK8S_BASE_IMAGE_ID_HERE>",
        "ssh_username": "root",
        "image_name": "<YOUR_IMAGE_NAME_GOES_HERE>",
        "image_copy_to_mappings": [
          {
            "project_id": "{{user `ucloud_project_id`}}",
            "region": "<REPLACE_REGION_ID_WHERE_TO_COPY>"
          }
        ]
      }],

      "provisioners": [{
        "type": "ansible",
        "playbook_file": "./playbook.yml"
      }]

    }

请先将上述例子中尖括号中的内容替换成实际的值。
下表是香港可用区下 UK8S 支持的操作系统及版本对应的基础镜像 ID。
请按需要选择合适的镜像，并用镜像 ID 栏对应的值替代`<REPLACE_THE_UK8S_BASE_IMAGE_ID_HERE>`：

| 地域         | 可用区                 | 镜像 ID         | 操作系统      | 版本  | 支持 GPU  |
| ------------ | ---------------------- | --------------- | ------------- | ----- | --------- |
| hk           | hk-02(3002)            | uimage-puxm0l   | CentOS        | 7.6   | 是        |
| hk           | hk-02(3002)            | uimage-vareox   | Ubuntu        | 20.04 | 是        |
| hk           | hk-02(3002)            | uimage-yjoh5a   | Anolis        | 8.6   | 否        |


如果需要将制作完成的镜像拷贝到其它地域及可用区，可在上述文件的`image_copy_to_mappings`中设置目标[可用区](https://docs.ucloud.cn/api/summary/regionlist)，可以同时指定多个。
如果不需要复制的话，请将该属性删除即可。

接下来需要编写安装配置自定义镜像的脚本。本文档给了一个使用 Ansible 的示例供参考。Packer还有其他的类型的provisioners，请参考[Packer官方文档](https://developer.hashicorp.com/packer/docs/provisioners)。Ansible对应的 playbook.yml 如下：

    - hosts: all
      become: true

      pre_tasks:
        - name: Disable swap
          command: swapoff -a
          when: ansible_swaptotal_mb > 0

      roles:
        - role: custom-setup

上述例子中的 playbook 会关闭 swap，并执行命名`custom-setup`的 role 做进一步设置。
请注意这个仅仅是示例，关闭 swap 实际上已经在 UK8S 的基础镜像中完成，无需再做此操作。

4. 运行 Packer

首次运行 Pakcer 时请在包含上述 `custom.json` 文件的目录下运行：

    packer init .

如果上述命令运行有问题，请在运行路径下配置config.pkr.hcl文件，文件内容如下

    packer {
      required_plugins {
        ucloud = {
          version = ">= 1.0.8"
          source  = "github.com/ucloud/ucloud"
        }
      }
    }

然后再运行以下命令：

    packer build custom.json

创建镜像的过程比较耗时，中途请勿到云主机中进行任何操作，或者删除该主机，否则无法正常创建镜像。
创建完成后，packer 会显示镜像的 ID。示例如下：


    ==> ucloud-uhost: Stopping instance "uhost-88888888888"
        ucloud-uhost: Stopping instance "uhost-88888888888" complete
    ==> ucloud-uhost: Creating image xxxx-yyyyy-8.5...
        ucloud-uhost: Waiting for the created image "uimage-***********" to become available...
        ucloud-uhost: Creating image "uimage-***********" complete
    ==> ucloud-uhost: Copying images from "uimage-***********"...
        ucloud-uhost: Copying image from org-******:cn-bj2:uimage-*********** to org-******:cn-wlcb:uimage-***********
        ucloud-uhost: Copying image from org-******:cn-bj2:uimage-*********** to org-******:hk:uimage-***********
        ucloud-uhost: Copying image from org-******:cn-bj2:uimage-*********** to org-******:cn-gd:uimage-***********
        ucloud-uhost: Waiting for the copied images to become available...
        ucloud-uhost: Copying image complete
    ==> ucloud-uhost: Deleting instance...
        ucloud-uhost: Deleting instance "uhost-88888888888" complete
    Build 'ucloud-uhost' finished after 19 minutes 43 seconds.

自定义镜像制作完成后 Packer 会自动删除云主机，无需担心因忘记删除主机而产生不必要的费用。

## 三、注意事项

UK8S 基础镜像预先配置好了部署 Kubernetes 的依赖项，如软件、文件目录、内核参数等。
在基于 UK8S 基础镜像制作自定义镜像时，请谨慎修改相关配置，以免基于自定义镜像创建节点时失败。
下面简要说明制作自定义镜像过程中的注意事项。

### 3.1 系统相关

1. 默认禁用了 swap，**请勿开启**；
2. 配置了 journald 参数 Storage=persistent，**不建议修修改**；
3. 默认创建了以下目录，**请勿删除或修改**；

- /etc/kubernetes/ssl
- /etc/etcd/
- /etc/docker/
- /etc/kubelet.d/
- /var/lib/kubelet
- ~/.kube/
- /var/lib/etcd/
- /var/lib/etcd/default.etcd
- /usr/libexec/kubernetes/kubelet-plugins/volume/exec/ucloud~flexv/
- /etc/kubernetes/yaml

4. 加载了 ip_conntrack 模块，**请勿修改**；
5. 默认禁用了 IPV6，**请勿修改**
6. 对于龙蜥操作系统 8.x 版本，必须关闭 firewalld，**自定义镜像时请勿开启**

### 3.2 软件部分

UK8S 节点初始化依赖以下软件（部分），**请勿卸载**。
- iptables
- ipvsadm
- socat
- nfs-utils（用于挂载 ufs)
- conntrack
- earlyoom

UK8S 节点初始化时，会将预先生成的证书、配置文件、二进制文件（kube-proxy、kubelet、scheduler、docker、kubectl 等）
拷贝到节点，并依次启动。 因此在制作自定义镜像时，无需安装 K8S 相关组件。
即使安装也不会被使用到，但可能干扰 UK8S 管理程序而导致创建集群失败。

[1]: https://packer.io
[2]: https://www.ansible.com
