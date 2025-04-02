# Ingress 支持

本文介绍如何在 UK8S 中安装和配置基于 nginx 的 Ingress Controller 。

不同版本的 Kubernetes 安装配置方法有所不同。

> 注意：Nginx Ingress较低版本存在一些安全漏洞，详见[Ingress-Nginx Controller漏洞公告](/uk8s/vulnerability/CVE-2025-1974.md), 如果您的 Kubernetes 版本在1.13 - 1.25并且需要安装Nginx Ingress，建议以最小权限管理Nginx Ingress。

如果您的 Kubernetes 版本为 1.26 及以上，请参考 [kubernetes Nginx Ingress 安装配置说明 (1.26 ~ latest)](/uk8s/service/ingress/nginx_1.26)。

如果您的 Kubernetes 版本为 1.19 ~ 1.25，请参考 [kubernetes Nginx Ingress 安装配置说明 (1.19 ~ 1.25)](/uk8s/service/ingress/nginx_1.19)。

如果您的 Kubernetes 版本为 1.13 ~ 1.18，请参考 [kubernetes Nginx Ingress 安装配置说明 (1.13 ~ 1.18)](/uk8s/service/ingress/nginx)。

如果您想了解 Ingress 的高级用法，请参考 [Ingress 高级用法](/uk8s/service/ingress/multiple_ingress)
