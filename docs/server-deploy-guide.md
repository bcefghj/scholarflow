# ScholarFlow 服务器部署完整教程

从零开始，把 ScholarFlow 部署到云服务器，让别人通过浏览器直接访问使用。

**预计耗时**: 30-60 分钟（含服务器购买）

---

## 目录

1. [购买云服务器](#1-购买云服务器)
2. [连接服务器](#2-连接服务器)
3. [安装 Docker](#3-安装-docker)
4. [部署 ScholarFlow](#4-部署-scholarflow)
5. [配置 Nginx 反向代理](#5-配置-nginx-反向代理)
6. [配置安全组（开放端口）](#6-配置安全组开放端口)
7. [验证部署](#7-验证部署)
8. [日常维护](#8-日常维护)
9. [常见问题](#9-常见问题)

---

## 1. 购买云服务器

### 推荐配置

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 1 核 | 2 核 |
| 内存 | 2 GB | 4 GB |
| 硬盘 | 40 GB | 50 GB |
| 系统 | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| 带宽 | 1 Mbps | 3 Mbps |

> **注意**: 内存建议 >= 2GB。Docker 构建 LaTeX 环境需要约 1.5GB 临时空间。如果内存只有 1GB，建议先[配置 swap](#配置-swap可选)。

### 各云平台新用户优惠

- **阿里云**: [新人试用](https://free.aliyun.com/) — 免费 3 个月 ECS
- **腾讯云**: [新人专区](https://cloud.tencent.com/act/pro/free) — 免费 1 个月轻量应用
- **华为云**: [免费试用](https://activity.huaweicloud.com/free_test/) — 免费体验

### 购买步骤（以阿里云为例）

1. 注册/登录阿里云
2. 进入 ECS 控制台 → 创建实例
3. 选择地域（建议选离用户近的，如华东/华北）
4. 选择 **Ubuntu 22.04 64位**
5. 设置登录密码（记好，后面要用）
6. 确认购买

记下服务器的**公网 IP 地址**（如 `47.96.5.62`），后面要用。

---

## 2. 连接服务器

### macOS / Linux

打开终端：

```bash
ssh root@你的服务器IP
# 例如: ssh root@47.96.5.62
# 输入密码回车（密码不会显示，正常的）
```

### Windows

- **方式1**: 使用 PowerShell（Win10/11 自带）

```powershell
ssh root@你的服务器IP
```

- **方式2**: 下载 [MobaXterm](https://mobaxterm.mobatek.net/)（免费、好用）
  - 新建 Session → SSH → 输入 IP、用户名 root → 输入密码

### 连接成功标志

看到类似这样的提示就说明连上了：

```
Welcome to Ubuntu 22.04.x LTS
root@iZxxxxxx:~#
```

---

## 3. 安装 Docker

连上服务器后，依次执行以下命令：

```bash
# 更新系统
apt-get update && apt-get upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 验证 Docker 安装成功
docker --version
# 输出类似: Docker version 24.x.x

# 启动 Docker 并设为开机自启
systemctl start docker
systemctl enable docker
```

### 配置 Docker 镜像加速（中国服务器强烈推荐）

中国服务器拉取 Docker 镜像可能很慢，配置加速器：

```bash
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
EOF

systemctl daemon-reload
systemctl restart docker
```

### 配置 swap（可选，1GB 内存必做）

如果服务器内存只有 1GB，需要配置 swap 防止 Docker 构建时内存不足：

```bash
# 创建 2GB swap 文件
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 开机自动启用
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 验证
free -h
# 应该看到 Swap: 2.0G
```

---

## 4. 部署 ScholarFlow

### 4.1 下载代码

```bash
cd /root
git clone https://github.com/bcefghj/scholarflow.git
cd scholarflow
```

> 如果 `git clone` 很慢，可以用 GitHub 镜像：
> ```bash
> git clone https://ghproxy.com/https://github.com/bcefghj/scholarflow.git
> ```

### 4.2 配置 API Key

```bash
cp .env.example .env
nano .env
```

在 `.env` 文件中填入你的 LLM API Key：

```ini
# 选一个填就行
OPENAI_API_KEY=sk-xxx
# 或者 MiniMax（推荐，性价比高）
MINIMAX_API_KEY=eyJhbxxxxxxxxx

# 模型配置（可选，不填则使用默认模型）
# DEFAULT_MODEL=minimax/MiniMax-M2.7
```

按 `Ctrl+O` 保存，`Ctrl+X` 退出。

### 4.3 构建 Docker 镜像

```bash
docker build -t scholarflow -f docker/Dockerfile .
```

> **首次构建需要 5-10 分钟**（下载 Python 依赖 + LaTeX 环境）。
> 后续重新构建会利用缓存，只需 1-2 分钟。

构建成功会看到：

```
Successfully built xxxxxxxxx
Successfully tagged scholarflow:latest
```

### 4.4 启动服务

```bash
docker run -d \
  --name scholarflow \
  -p 8080:8080 \
  -v scholarflow-data:/app/output \
  --env-file .env \
  --restart unless-stopped \
  scholarflow
```

参数说明：
- `-d`: 后台运行
- `--name scholarflow`: 容器名称
- `-p 8080:8080`: 端口映射
- `-v scholarflow-data:/app/output`: 持久化输出文件
- `--env-file .env`: 加载环境变量
- `--restart unless-stopped`: 自动重启

### 4.5 验证容器运行

```bash
docker ps
```

应该看到 `scholarflow` 容器状态为 `Up`：

```
CONTAINER ID   IMAGE         STATUS         PORTS
xxxxxxxxx      scholarflow   Up 2 minutes   0.0.0.0:8080->8080/tcp
```

```bash
# 测试服务是否正常
curl http://localhost:8080/
# 应返回 HTML 页面内容
```

---

## 5. 配置 Nginx 反向代理

Nginx 用于将 80 端口（HTTP 默认端口）转发到 8080 端口，这样用户直接访问 `http://你的IP` 即可。

```bash
docker run -d \
  --name nginx-proxy \
  -p 80:80 \
  -v /root/scholarflow/docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  --link scholarflow:scholarflow \
  --restart unless-stopped \
  nginx:alpine
```

> **关于 SSE（流式输出）**: `nginx.conf` 已经预配置了 `/api/stream/` 路径的 SSE 支持（禁用缓冲），无需额外配置。

验证 Nginx 运行：

```bash
docker ps
# 应该看到 scholarflow 和 nginx-proxy 两个容器都在运行

curl http://localhost/
# 应返回页面内容
```

---

## 6. 配置安全组（开放端口）

云服务器默认不开放端口，需要在控制台配置安全组规则。

### 阿里云

1. 登录 [ECS 控制台](https://ecs.console.aliyun.com/)
2. 找到你的实例 → 点击 → 安全组 → 配置规则
3. 添加以下规则：

| 方向 | 协议 | 端口范围 | 授权对象 | 说明 |
|------|------|----------|----------|------|
| 入方向 | TCP | 80 | 0.0.0.0/0 | HTTP 访问 |
| 入方向 | TCP | 443 | 0.0.0.0/0 | HTTPS（可选） |

### 腾讯云

1. 登录 [轻量应用服务器控制台](https://console.cloud.tencent.com/lighthouse)
2. 找到实例 → 防火墙 → 添加规则
3. 添加 TCP 80 端口，来源 0.0.0.0/0

### 华为云

1. 登录 [ECS 控制台](https://console.huaweicloud.com/ecm/)
2. 安全组 → 添加入方向规则 → TCP 80 → 0.0.0.0/0

---

## 7. 验证部署

### 浏览器访问

打开浏览器，输入：

```
http://你的服务器公网IP
```

例如: `http://47.96.5.62`

应该看到 ScholarFlow 的 Web 界面。

### 功能测试

1. 上传一个 PDF 论文文件
2. 选择输出选项（建议先选 "简要介绍" 测试，最快）
3. 点击开始处理
4. 观察流式进度输出
5. 下载生成的文件

### 验证 LaTeX PDF 生成

```bash
# 进入容器验证 xelatex
docker exec scholarflow xelatex --version
# 应输出: XeTeX 3.141592653-2.6-0.999995 (TeX Live 2023/Debian)

# 验证中文字体
docker exec scholarflow fc-list :lang=zh
# 应包含: WenQuanYi Micro Hei
```

---

## 8. 日常维护

### 查看日志

```bash
# 实时查看 ScholarFlow 日志
docker logs -f scholarflow

# 查看最近 100 行
docker logs --tail 100 scholarflow

# 查看 Nginx 日志
docker logs -f nginx-proxy
```

### 重启服务

```bash
# 重启 ScholarFlow
docker restart scholarflow

# 重启 Nginx
docker restart nginx-proxy

# 重启全部
docker restart scholarflow nginx-proxy
```

### 更新到最新版本

```bash
cd /root/scholarflow

# 拉取最新代码
git pull origin main

# 停止旧容器
docker stop scholarflow nginx-proxy
docker rm scholarflow nginx-proxy

# 重新构建（利用缓存，通常 1-2 分钟）
docker build -t scholarflow -f docker/Dockerfile .

# 启动新容器
docker run -d \
  --name scholarflow \
  -p 8080:8080 \
  -v scholarflow-data:/app/output \
  --env-file .env \
  --restart unless-stopped \
  scholarflow

docker run -d \
  --name nginx-proxy \
  -p 80:80 \
  -v /root/scholarflow/docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  --link scholarflow:scholarflow \
  --restart unless-stopped \
  nginx:alpine
```

### 清理磁盘空间

```bash
# 查看磁盘使用
df -h

# 清理 Docker 无用镜像
docker system prune -a -f

# 清理旧的输出文件（保留最近 7 天）
docker exec scholarflow find /app/output -mtime +7 -delete
```

### 备份数据

```bash
# 备份输出文件
docker cp scholarflow:/app/output /root/scholarflow-backup-$(date +%Y%m%d)

# 备份配置
cp /root/scholarflow/.env /root/scholarflow-backup-env
```

---

## 9. 常见问题

### Q: Docker 构建时内存不足怎么办？

**症状**: 构建过程中被 Killed，或报 `Cannot allocate memory`

**解决**: 配置 swap（见[第3节](#配置-swap可选1gb-内存必做)）

### Q: 中国服务器 Docker 拉取很慢？

**解决**: 配置 Docker 镜像加速器（见[第3节](#配置-docker-镜像加速中国服务器强烈推荐)）

### Q: `git clone` 超时？

**解决**: 使用 GitHub 镜像：
```bash
git clone https://ghproxy.com/https://github.com/bcefghj/scholarflow.git
```

### Q: 访问 IP 显示无法连接？

**检查清单**:
1. 安全组是否开放了 80 端口？
2. 容器是否在运行？`docker ps`
3. Nginx 是否正常？`docker logs nginx-proxy`
4. 防火墙是否放行？`ufw status`（如果启用了 ufw）

### Q: 生成的 PDF 中文显示为方框？

**原因**: 缺少中文字体

**解决**: 重新构建镜像（最新 Dockerfile 已包含 `fonts-wqy-microhei`）
```bash
docker stop scholarflow && docker rm scholarflow
docker build --no-cache -t scholarflow -f docker/Dockerfile .
# 然后重新启动容器
```

### Q: 表格超出 PDF 页面右边界？

**原因**: 旧版本使用固定宽度 `tabular`

**解决**: 更新到最新版本，已改用 `tabularx` 自适应宽度

### Q: 怎么配置 HTTPS？

使用 Let's Encrypt 免费证书（需要一个域名）：

```bash
# 安装 certbot
apt-get install -y certbot

# 获取证书（需要先把域名解析到服务器IP）
certbot certonly --standalone -d yourdomain.com

# 然后修改 nginx.conf 配置 SSL
```

### Q: 怎么绑定域名？

1. 在域名服务商处添加 A 记录，指向服务器 IP
2. 等待 DNS 生效（通常 5-30 分钟）
3. 通过 `http://yourdomain.com` 访问

---

## 快速部署命令汇总

如果你是老手，以下是从零到部署完成的所有命令（一键复制）：

```bash
# === 安装 Docker ===
curl -fsSL https://get.docker.com | sh
systemctl start docker && systemctl enable docker

# === 镜像加速（中国服务器） ===
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": ["https://docker.1ms.run", "https://docker.xuanyuan.me"]
}
EOF
systemctl daemon-reload && systemctl restart docker

# === 部署 ScholarFlow ===
cd /root
git clone https://github.com/bcefghj/scholarflow.git
cd scholarflow
cp .env.example .env
nano .env  # 填入 API Key

# 构建并启动
docker build -t scholarflow -f docker/Dockerfile .
docker run -d --name scholarflow -p 8080:8080 \
  -v scholarflow-data:/app/output --env-file .env \
  --restart unless-stopped scholarflow
docker run -d --name nginx-proxy -p 80:80 \
  -v /root/scholarflow/docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  --link scholarflow:scholarflow --restart unless-stopped nginx:alpine

# === 验证 ===
docker ps
curl http://localhost/
echo "部署完成！访问 http://$(curl -s ifconfig.me)"
```

---

**GitHub**: [bcefghj/scholarflow](https://github.com/bcefghj/scholarflow)
**小红书**: bcefghj
