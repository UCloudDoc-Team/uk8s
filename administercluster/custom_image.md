# 制作自定义镜像

## 一、前言

为了满足用户对 UK8S 节点的个性化需求，除了标准镜像外，UK8S 的 Node 节点也支持自定义镜像。
但务必使用 UK8S 的标准镜像来制作自定义镜像，否则可能导致集群无法创建或节点无法添加。

下面介绍如何基于标准镜像制作自定义镜像，以及注意事项。
本文档介绍的自定义镜像制作过程是完全自动化的，制作过程中无需人工干预。用户需要具备简单的
shell 编程或 [Ansible][2] 使用经验。

## 二、制作自定义镜像流程

1. 安装 Packer

安装 [Packer][1]
工具，使用该工具可以方便地创建并分发自定义镜像到你需要的可用区。

MacOS 用户可以通过以下命令安装 Packer：

```bash
brew install packer
```

Packer 只负责创建云主机，在云主机中安装配置软件需要使用命令行脚本或 Ansible。
本文档给的示例使用 Ansile，你也可以转换成其它等价工具。所以建议安装以下 Ansible。

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
下表是 UK8S 基础镜像 ID。请按可用区和操作系统从下表中选择你需要的镜像，
用镜像 ID 栏对应的值替代`<REPLACE_THE_UK8S_BASE_IMAGE_ID_HERE>`：

| 地域         | 可用区                 | 镜像 ID         | 操作系统      | 版本  | 支持 GPU  |
| ------------ | ---------------------- | --------------- | ------------- | ----- | --------- |
| afr-nigeria  | afr-nigeria-01(10017)  | uimage-ewug3a   | CentOS        | 7.6   | 是        |
| afr-nigeria  | afr-nigeria-01(10017)  | uimage-141kkh   | Ubuntu        | 20.04 | 是        |
| afr-nigeria  | afr-nigeria-01(10017)  | uimage-qsynla   | Anolis        | 8.6   | 否        |
| bra-saopaulo | bra-saopaulo-01(10015) | uimage-s5btgp   | CentOS        | 7.6   | 是        |
| bra-saopaulo | bra-saopaulo-01(10015) | uimage-d2gokx   | UBuntu        | 20.04 | 是        |
| bra-saopaulo | bra-saopaulo-01(10015) | uimage-jubeg3   | Anolis        | 8.6   | 否        |
| cn-bj2       | cn-bj2-02(4001)        | uimage-yqqphs   | CentOS        | 7.6   | 是        |
| cn-bj2       | cn-bj2-03(5001)        | uimage-tf3j3n   | CentOS        | 7.6   | 是        |
| cn-bj2       | cn-bj2-04(9001)        | uimage-5lu3ey   | CentOS        | 7.6   | 是        |
| cn-bj2       | cn-bj2-05(9002)        | uimage-qbchje   | CentOS        | 7.6   | 是        |
| cn-bj2       | cn-bj2-02(4001)        | uimage-felrep   | Ubuntu        | 20.04 | 是        |
| cn-bj2       | cn-bj2-03(5001)        | uimage-ciyiod   | Ubuntu        | 20.04 | 是        |
| cn-bj2       | cn-bj2-04(9001)        | uimage-b3gp4h   | Ubuntu        | 20.04 | 是        |
| cn-bj2       | cn-bj2-05(9002)        | uimage-v41va0   | Ubuntu        | 20.04 | 是        |
| cn-bj2       | cn-bj2-02(4001)        | uimage-ph5dcj   | Anolis        | 8.6   | 否        |
| cn-bj2       | cn-bj2-03(5001)        | uimage-pai3mb   | Anolis        | 8.6   | 否        |
| cn-bj2       | cn-bj2-04(9001)        | uimage-zlhdif   | Anolis        | 8.6   | 否        |
| cn-bj2       | cn-bj2-05(9002)        | uimage-jknwls   | Anolis        | 8.6   | 否        |
| cn-gd        | cn-gd-02(7001)         | uimage-jg0p2k   | CentOS        | 7.6   | 是        |
| cn-gd        | cn-gd-02(7001)         | uimage-b00t2y   | Ubuntu        | 20.04 | 是        |
| cn-gd        | cn-gd-02(7001)         | uimage-qpd30r   | Anolis        | 8.6   | 否        |
| cn-sh2       | cn-sh2-01(8100)        | uimage-cp5qk0   | CentOS        | 7.6   | 是        |
| cn-sh2       | cn-sh2-02(8200)        | uimage-iahdzb   | CentOS        | 7.6   | 是        |
| cn-sh2       | cn-sh2-03(8300)        | uimage-1hrt4v   | CentOS        | 7.6   | 是        |
| cn-sh2       | cn-sh2-01(8100)        | uimage-matqvp   | Ubuntu        | 20.04 | 是        |
| cn-sh2       | cn-sh2-02(8200)        | uimage-mawf3z   | Ubuntu        | 20.04 | 是        |
| cn-sh2       | cn-sh2-03(8300)        | uimage-fownjq   | Ubuntu        | 20.04 | 是        |
| cn-sh2       | cn-sh2-01(8100)        | uimage-cnlirb   | Anolis        | 8.6   | 否        |
| cn-sh2       | cn-sh2-02(8200)        | uimage-1cmk0m   | Anolis        | 8.6   | 否        |
| cn-sh2       | cn-sh2-03(8300)        | uimage-cl1vbw   | Anolis        | 8.6   | 否        |
| cn-wlcb      | cn-wlcb-01(10027)      | uimage-f4pwzt   | CentOS        | 7.6   | 是        |
| cn-wlcb      | cn-wlcb-01(10027)      | uimage-xhsmqh   | Ubuntu        | 20.04 | 是        |
| cn-wlcb      | cn-wlcb-01(10027)      | uimage-4lpvif   | Anolis        | 8.6   | 否        |
| hk           | hk-02(3002)            | uimage-puxm0l   | CentOS        | 7.6   | 是        |
| hk           | hk-02(3002)            | uimage-vareox   | Ubuntu        | 20.04 | 是        |
| hk           | hk-02(3002)            | uimage-yjoh5a   | Anolis        | 8.6   | 否        |
| idn-jakarta  | idn-jakarta-01(10011)  | uimage-3lqsv3   | CentOS        | 7.6   | 是        |
| idn-jakarta  | idn-jakarta-01(10011)  | uimage-dkbfby   | Ubuntu        | 20.04 | 是        |
| idn-jakarta  | idn-jakarta-01(10011)  | uimage-ckahxh   | Anolis        | 8.6   | 否        |
| jpn-tky      | jpn-tky-01(10008)      | uimage-3hypbh   | CentOS        | 7.6   | 是        |
| jpn-tky      | jpn-tky-01(10008)      | uimage-1yfi1v   | Ubuntu        | 20.04 | 是        |
| jpn-tky      | jpn-tky-01(10008)      | uimage-hbydhw   | Anolis        | 8.6   | 否        |
| kr-seoul     | kr-seoul-01(10004)     | uimage-lytemg   | CentOS        | 7.6   | 是        |
| kr-seoul     | kr-seoul-01(10004)     | uimage-ji1vyq   | Ubuntu        | 20.04 | 是        |
| kr-seoul     | kr-seoul-01(10004)     | uimage-vmoozr   | Anolis        | 8.6   | 否        |
| ph-mnl       | ph-mnl-01(10025)       | uimage-nv52nm   | CentOS        | 7.6   | 是        |
| ph-mnl       | ph-mnl-01(10025)       | uimage-g1qpsk   | Ubuntu        | 20.04 | 是        |
| ph-mnl       | ph-mnl-01(10025)       | uimage-0lfzew   | Anolis        | 8.6   | 否        |
| rus-mosc     | rus-mosc-01(10007)     | uimage-wg10ic   | CentOS        | 7.6   | 是        |
| rus-mosc     | rus-mosc-01(10007)     | uimage-0t4vk0   | Ubuntu        | 20.04 | 是        |
| rus-mosc     | rus-mosc-01(10007)     | uimage-dhakbf   | Anolis        | 8.6   | 否        |
| sg           | sg-01(10005)           | uimage-2qkirw   | CentOS        | 7.6   | 是        |
| sg           | sg-01(10005)           | uimage-r52fqi   | Ubuntu        | 20.04 | 是        |
| sg           | sg-01(10005)           | uimage-ph2jyx   | Anolis        | 8.6   | 否        |
| sg           | sg-02(10028)           | uimage-2qkirw   | CentOS        | 7.6   | 是        |
| sg           | sg-02(10028)           | uimage-r52fqi   | Ubuntu        | 20.04 | 是        |
| sg           | sg-02(10028)           | uimage-5yeoyz   | Anolis        | 8.6   | 否        |
| th-bkk       | th-bkk-01(10003)       | uimage-s2w523   | CentOS        | 7.6   | 是        |
| th-bkk       | th-bkk-01(10003)       | uimage-qdhhdc   | Ubuntu        | 20.04 | 是        |
| tw-tp        | tw-tp-01(10009)        | uimage-jswkmh   | CentOS        | 7.6   | 是        |
| tw-tp        | tw-tp-01(10009)        | uimage-v2a10d   | Ubuntu        | 20.04 | 是        |
| tw-tp        | tw-tp-01(10009)        | uimage-o41ux4   | Anolis        | 8.6   | 否        |
| us-ca        | us-ca-01(6001)         | uimage-uimk0f   | CentOS        | 7.6   | 是        |
| us-ca        | us-ca-01(6001)         | uimage-fikjpt   | Ubuntu        | 20.04 | 是        |
| us-ca        | us-ca-01(6001)         | uimage-ycujk2   | Anolis        | 8.6   | 否        |
| us-ws        | us-ws-01(10001)        | uimage-uujixy   | CentOS        | 7.6   | 是        |
| us-ws        | us-ws-01(10001)        | uimage-2ipl43   | Ubuntu        | 20.04 | 是        |
| us-ws        | us-ws-01(10001)        | uimage-pv4vpi   | Anolis        | 8.6   | 否        |
| vn-sng       | vn-sng-01(10018)       | uimage-zvzwyr   | CentOS        | 7.6   | 是        |
| vn-sng       | vn-sng-01(10018)       | uimage-qq4oc1   | Ubuntu        | 20.04 | 是        |
| vn-sng       | vn-sng-01(10018)       | uimage-g0yjby   | Anolis        | 8.6   | 否        |


如果你需要将制作完成的镜像拷贝到其它地域及可用区，可在上述文件的`image_copy_to_mappings`中设置目标可用区，可以同时指定多个。
如果不需要复制的话，请将该属性删除即可。

接下来你需要编写安装配置自定义镜像的脚本。本文档给了一个使用 Ansible 的示例供参考。对应的 playbook.yml 如下：

    - hosts: all
      become: true

      pre_tasks:
        - name: Disable swap
          command: swapoff -a
          when: ansible_swaptotal_mb > 0

      roles:
        - role: custom-setup

上述例子中的 playbook 会关闭 swap，并执行命名`custom-setup`的 role 做进一步设置。
请注意这个仅仅是示例，关闭 swap 实际上已经在 UK8S 的基础镜像中完成，你无需再做此操作。

4. 运行 Packer

首次运行 Pakcer 时请在包含上述 `custom.json` 文件的目录下运行：

    packer init .

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
