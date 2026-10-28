# Halo 本地开发

当前本机使用 Java 21 + Halo 2.27.1 JAR 运行，数据保存在 `halo-data`，不会连接现有 MySQL。

## 当前启动方式

```powershell
Set-Location F:\acg-resource-site\halo
.\run-halo.ps1
```

打开 <http://127.0.0.1:8090/system/setup> 完成首次初始化；初始化完成后访问 <http://127.0.0.1:8090/console>。

## 启动

```powershell
docker compose up -d
```

Docker 方式作为备用方案。使用它之前需要停止 JAR 进程，否则端口 8090 会冲突。

## 停止

```powershell
docker compose stop
```

## 删除本地容器

```powershell
docker compose down
```

`halo-data` 保存本地数据库、配置和上传文件。主题源码在 `theme/`，构建结果在 `theme/dist/`，可以在 Halo 后台的主题管理中上传 ZIP 安装。
