# Halo 接入 Cloudflare ImgBed / R2

当前图床地址：`https://904764f8.cloudflare-imgbed-6ip.pages.dev/`

## 先处理安全问题

之前截图暴露了 Telegram Bot Token。请在 Telegram 的 `@BotFather` 中撤销旧 Token 并重新生成；新 Token 只在 ImgBed 后台填写，不要发到聊天中。

## ImgBed 的 R2 配置

当前 `/api/channels` 显示 Telegram 1 个、Cloudflare R2 0 个。官方 ImgBed 的 R2 渠道通过 Cloudflare Pages binding 提供，不是普通的“添加渠道”表单。

官方说明：<https://cfbed.sanyue.de/deployment/configuration.html#配置-r2-渠道>

1. Cloudflare 控制台 → Pages → ImgBed 项目 → Settings → Bindings。
2. 添加 R2 bucket binding：变量名称必须是 `img_r2`，选择实际 R2 bucket。
3. 保存并重新部署 Pages 项目。
4. 登录 ImgBed 后台，打开：
   `https://904764f8.cloudflare-imgbed-6ip.pages.dev/systemConfig#upload`
5. 在 CloudFlare R2 分组编辑自动出现的渠道；如果界面要求公开地址，填：
   `https://904764f8.cloudflare-imgbed-6ip.pages.dev/file`
6. 上传一张小图片，确认 CloudFlare R2 分组显示为 1 个已启用渠道。

如果仍然是 0 个 R2 渠道，先检查 `img_r2` binding 和 Pages 重新部署日志。

## Halo 插件和存储策略

已下载官方 Halo S3 插件：

`F:\acg-resource-site\halo-data\plugins\plugin-s3-1.17.0.jar`

Halo 进程当前已在 `http://127.0.0.1:8090/` 运行。若后台插件列表没有“对象存储（Amazon S3 协议）”，进入 Halo 后台的“系统 → 插件 → 安装插件”，上传上面的 JAR。

安装后：

1. 进入“附件 → 存储策略 → 新建 → S3 对象存储”。
2. Bucket：ImgBed 绑定的 R2 bucket 名称。
3. Endpoint：`https://<ACCOUNT_ID>.r2.cloudflarestorage.com`。
4. Region：`auto`。
5. 先使用 Path Style。
6. Access Key ID 和 Secret：Cloudflare R2 API Token 的 Object Read & Write 凭据。
7. 绑定域名：`https://904764f8.cloudflare-imgbed-6ip.pages.dev/file`。
8. 保存后，把文章附件和默认附件存储策略切换到该 S3 策略。

Endpoint、Bucket、Access Key 和 Secret 不要发到聊天中，直接在 Cloudflare 和 Halo 页面填写。

## 验证

重新上传一张封面图和一张正文图，URL 应类似：

`https://904764f8.cloudflare-imgbed-6ip.pages.dev/file/<文件名>`

已有的 `/upload/...` 本地图片不会自动迁移，需要重新上传。
