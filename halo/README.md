# Halo 本地实例

本目录运行 Halo 社区版 2.27.1，使用 Java 21 和本地 H2 数据库，避免修改现有 MySQL 数据。

启动：

```powershell
Set-Location F:\acg-resource-site\halo
.\run-halo.ps1
```

访问：<http://127.0.0.1:8090/system/setup> 完成首次初始化；初始化完成后进入 <http://127.0.0.1:8090/console>。

主题构建包在 `..\theme\dist\acg-resource-theme-0.1.0.zip`，完成初始化后可从 Halo 后台的主题管理上传。
