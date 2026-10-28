# Halo 服务器部署（MySQL）

当前本地 Halo 使用 H2：`halo/application.yaml` 中的 `r2dbc:h2:file`。服务器建议使用现有 MySQL，但为 Halo 单独创建数据库和用户。

## 1. 创建 MySQL 数据库

```sql
CREATE DATABASE halo_resource CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'halo_resource'@'127.0.0.1' IDENTIFIED BY '替换为强密码';
GRANT ALL PRIVILEGES ON halo_resource.* TO 'halo_resource'@'127.0.0.1';
FLUSH PRIVILEGES;
```

如果 Halo 和 MySQL 不在同一台机器，将用户主机部分按实际内网地址调整。

## 2. 服务器目录

```text
/opt/halo/
  halo-2.27.1.jar
  application.yaml
  halo-data/
    plugins/
    themes/
    attachments/
```

不要把本地 `halo-data/db` 的 H2 文件当作 MySQL 数据导入。

## 3. application.yaml

```yaml
server:
  port: 8090

spring:
  r2dbc:
    url: r2dbc:pool:mysql://127.0.0.1:3306/halo_resource
    username: halo_resource
    password: 修改为数据库密码
  sql:
    init:
      mode: always
      platform: mysql

halo:
  work-dir: /opt/halo/halo-data
  external-url: https://你的域名
```

## 4. 启动测试

```bash
cd /opt/halo
java -Dfile.encoding=UTF-8 -server -Xms256m -Xmx512m \
  -jar halo-2.27.1.jar \
  --spring.config.additional-location=optional:file:/opt/halo/
```

首次访问：`https://你的域名/system/setup`。

## 5. systemd 服务

```ini
[Unit]
Description=Halo
After=network.target mysql.service

[Service]
User=halo
WorkingDirectory=/opt/halo
ExecStart=/usr/bin/java -Dfile.encoding=UTF-8 -server -Xms256m -Xmx512m -jar /opt/halo/halo-2.27.1.jar --spring.config.additional-location=optional:file:/opt/halo/
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 6. 迁移本地项目

H2 到 MySQL 不能通过复制 `halo-data/db` 直接完成。推荐在本地 Halo 后台导出文章，再在服务器后台导入；插件 JAR、主题 ZIP 和 ImgBed Telegram 存储策略需要在服务器重新安装/配置。

如果只想完整复制当前本地站点，服务器可以继续使用 H2，直接复制整个 `halo-data`，但不适合后续多人编辑和长期生产使用。
