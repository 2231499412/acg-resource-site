# Halo 资源站版本管理

## GitHub 仓库只保存

- `vendor/plugin-imgbed-telegram/src` 和 Gradle 构建文件
- 主题源码、Showcase 源码（推荐用 Git 子模块或单独仓库）
- `scripts/`、部署脚本和文档
- `application-mysql.yaml.example`（只放变量名，不放密码）

## 不要提交

- `halo-data/`：数据库、插件运行状态、附件、日志
- `halo/halo-*.jar`：Halo 运行包可在服务器下载或单独保存
- API Token、数据库密码、Telegram Bot Token
- `node_modules/`、`.gradle/`、`build/`、`imports/`

## 服务器目录建议

```text
/opt/acg-resource-site/repo   # Git 工作区
/opt/halo/                    # Halo JAR 和不含密钥的配置
/opt/halo-data/               # 持久化数据，不受 git pull 影响
```

## 更新流程

```bash
cd /opt/acg-resource-site/repo
git pull --ff-only

cd vendor/plugin-imgbed-telegram
./gradlew clean build
cp build/libs/plugin-imgbed-telegram-1.0.0.jar \
  /opt/halo-data/plugins/PluginImgBedTelegram-1.0.0.jar

sudo systemctl restart halo
```

主题更新时先在仓库构建 ZIP，再通过 Halo 后台安装；不要用 `git pull` 覆盖 `/opt/halo-data`。

## 首次推送

在本地仓库创建 GitHub 私有仓库后：

```bash
git init
git add .
git commit -m "initial Halo resource site"
git branch -M main
git remote add origin <你的 GitHub 仓库地址>
git push -u origin main
```

服务器使用 Deploy Key 或 GitHub Fine-grained PAT，只授予该仓库读取权限。
