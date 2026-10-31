# Earth 手机端导航

手机端（小于 640px）显示左侧菜单、居中站点 Logo/名称和右侧搜索。侧栏读取 Halo 主菜单和文章分类树，支持子分类展开、分类文章数量、当前页面标记、标签和显示模式切换。搜索使用已启用的 Halo 搜索组件。桌面顶部栏保持原样。

在服务器仓库目录运行（模板目录沿用现有 Halo 数据目录）：

```bash
git pull --ff-only origin main
sudo python3 scripts/patch-earth-mobile-navigation.py --halo-data-dir /opt/halo-data
sudo systemctl restart halo
```

脚本会安装 `deploy/theme-earth/` 中的模块和样式，并在使用 Earth 顶部栏的页面引入它们；可重复运行。首次修改每个模板前会保存 `.html.before-mobile-navigation.bak` 备份。已应用的文章图片边距规则不会被覆盖。

在 Halo 后台管理分类和主菜单；站点 Logo 有配置时使用 Logo，否则显示站点名称。新建分类后导航会自动读取。主题升级可能覆盖模板，升级后需重新运行脚本。

本地预览：

```bash
python scripts/patch-earth-mobile-navigation.py
```

随后重启本地 Halo 并以手机宽度访问页面。
