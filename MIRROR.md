# 镜像配置说明

## NPM 镜像配置

### 方式一：使用配置文件（推荐）
项目已包含 `.npmrc` 文件，自动使用淘宝镜像。

### 方式二：手动配置
```bash
# 设置淘宝镜像
npm config set registry https://registry.npmmirror.com/
npm config set electron_mirror https://npmmirror.com/mirrors/electron/

# 查看配置
npm config get registry

# 恢复官方源
npm config set registry https://registry.npmjs.org/
```

### 可选镜像源
- **淘宝镜像**（推荐）: https://registry.npmmirror.com/
- **腾讯云**: https://mirrors.cloud.tencent.com/npm/
- **华为云**: https://mirrors.huaweicloud.com/repository/npm/

## PIP 镜像配置

### 方式一：临时使用
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方式二：全局配置
```bash
# Windows
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Linux/Mac
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 可选镜像源
- **清华大学**（推荐）: https://pypi.tuna.tsinghua.edu.cn/simple
- **阿里云**: https://mirrors.aliyun.com/pypi/simple/
- **中科大**: https://pypi.mirrors.ustc.edu.cn/simple/
- **豆瓣**: https://pypi.douban.com/simple/

## 速度对比

| 源 | npm安装速度 | pip安装速度 |
|----|------------|------------|
| 官方源 | 慢 🐌 | 慢 🐌 |
| 中国镜像 | 快 🚀 | 快 🚀 |

使用中国镜像可将下载速度提升 **10-50倍**！

## 快速安装

### Electron应用
```bash
# Windows
安装Electron依赖.bat

# 命令行
npm install
```

### Python GUI
```bash
# Windows
安装依赖.bat

# 命令行
pip install -r requirements.txt
```

所有安装脚本已自动配置中国镜像，无需手动设置！
