# ImgBed Telegram 插件本地安装

已生成插件：`vendor/plugin-imgbed-telegram/build/libs/plugin-imgbed-telegram-1.0.0.jar`

## 安装

Halo 必须通过已登录的管理后台安装插件，单纯把 JAR 放进 `halo-data/plugins` 不会创建插件资源记录。打开 `http://127.0.0.1:8090/console`，进入“系统 -> 插件”，选择“安装插件”，上传该 JAR。

安装完成后，在“附件 -> 存储策略”新建 `ImgBed Telegram`，填写：

- ImgBed 地址：`https://904764f8.cloudflare-imgbed-6ip.pages.dev`
- API Token：在 ImgBed 后台创建，只在本机 Halo 表单填写
- 上传目录：例如 `halo`
- 最大文件大小：20 MB 或更小

将该策略设为默认附件存储策略后，文章封面图和正文编辑器图片会通过 ImgBed `/upload?uploadChannel=telegram&returnFormat=full` 上传，删除附件时调用 ImgBed 删除 API。

## 安全

不要把 API Token 或 Telegram Bot Token 发到聊天中。此前截图中暴露的 Bot Token 应在 `@BotFather` 立即撤销并重新生成。
