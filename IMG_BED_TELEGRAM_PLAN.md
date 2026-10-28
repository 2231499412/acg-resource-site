# Halo 使用 ImgBed Telegram 渠道的实现方案

## 为什么官方 S3 插件不能直接使用

Halo 官方 S3 插件调用的是 S3 的 PutObject、Multipart Upload、HeadObject、DeleteObject 等接口，并按 S3 规则生成对象地址。Telegram 渠道没有这些接口：文件要先发到 ImgBed 的 `/upload`，再由 ImgBed 调用 Telegram Bot API 保存，最终通过 `/file/...` 代理读取。因此 `pages.dev/file/...` 只能读，不能当成 S3 Endpoint 写入。

## 可行方案

开发一个 Halo 存储策略插件 `imgbed-telegram`：

1. 实现 Halo `AttachmentHandler`。
2. 上传时调用：
   `POST /upload?uploadChannel=telegram&returnFormat=full`
3. 以 `multipart/form-data` 的 `file` 字段发送图片。
4. 使用 ImgBed API Token（至少 `upload` 权限）。
5. 解析返回的 `src` / `publicUrl`，写入 Halo 附件永久链接。
6. 删除时调用 `/api/manage/delete/{path}`，Token 需要 `delete` 权限。
7. 在 Halo 中把该策略设为文章附件默认策略。

建议插件设置字段：ImgBed 地址、API Token、上传目录、是否强制 Telegram、单文件大小上限（20MB）。图片上传采用流式或临时文件，避免 2G 服务器一次性占用过多内存。

## ImgBed API

官方上传文档：<https://cfbed.sanyue.de/api/upload.html>

普通上传示例：

```text
POST https://904764f8.cloudflare-imgbed-6ip.pages.dev/upload?uploadChannel=telegram&returnFormat=full
Authorization: Bearer <API_TOKEN>
Content-Type: multipart/form-data
file=<image>
```

## 限制

Telegram Bot 渠道单文件上限约 20MB；大文件需要 ImgBed 分块流程。文章封面和正文图片通常远小于此限制，适合直接上传。已有本地附件不会自动迁移，需要重新上传。
