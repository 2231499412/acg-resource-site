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

sudo install -m 0644 deploy/plugins/PluginImgBedTelegram-1.0.0.jar \
  /opt/halo-data/plugins/PluginImgBedTelegram-1.0.0.jar
sudo systemctl restart halo
```

复制 JAR 并重启只会把文件放到 Halo 数据目录，不会在 Halo 中注册插件。首次安装时，还要登录服务器的 Halo Console，进入“系统 -> 插件 -> 安装插件”，上传仓库中的 `deploy/plugins/PluginImgBedTelegram-1.0.0.jar`。插件安装并启用后，进入“附件 -> 存储策略”新建 ImgBed Telegram 策略，并在服务器上单独填写 ImgBed 地址、API Token、上传目录和文件大小限制，再将策略设为默认。

本地和服务器是不同的 Halo 实例，插件安装状态及存储策略配置保存在各自的数据目录/数据库中，不会随 Git 推送同步。升级已有插件时也应在 Console 确认插件版本并按 Halo 插件管理流程更新；不要只依赖复制 JAR 覆盖文件。

主题更新时先在仓库构建 ZIP，再通过 Halo 后台安装；不要用 `git pull` 覆盖 `/opt/halo-data`。

### Earth 主题补丁（单文件精确覆盖）

图片懒加载、多源兜底等小改动放在 `deploy/theme-earth-patch/`，只覆盖单个模板文件，不走整体 ZIP 重装：

```bash
cd /opt/acg-resource-site/repo
git pull --ff-only

sudo cp /opt/halo-data/themes/theme-earth/templates/post.html \
        /opt/halo-data/themes/theme-earth/templates/post.html.bak
sudo cp deploy/theme-earth-patch/post.html \
        /opt/halo-data/themes/theme-earth/templates/post.html
sudo systemctl restart halo
```

详见 `deploy/theme-earth-patch/README.md`。

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
