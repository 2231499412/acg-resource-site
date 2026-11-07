# 图片懒加载 + 多源兜底补丁部署说明

## 背景

COS 图包文章单篇图片数量极大（最多 150 张），正文图片默认一次性全部加载，页面很慢。Halo 会给**本地 `/upload/` 图片**自动注入 `srcset`/`sizes` 响应式属性（外链图片则原样输出、不重写），但没有懒加载。

另外，游戏搬运文章的部分配图下载超时后会被脚本直接丢弃，造成缺图。为此补丁同时支持**外链优先 + 本地兜底**的多源加载。

> 实测补充：外链图片的 `data-sources`、`#fb=`、`loading="lazy"` 等自定义属性在前台会**完整保留**；只有本地图会被 Halo 追加 `srcset`/`sizes`。所以兜底链对搬运文章可靠，但仍需要本补丁的 JS 来真正执行「失败切下一个源」。

本补丁在 Earth 主题的 `post.html` 中注入一段前端脚本，做两件事：

**懒加载**
- 用 `IntersectionObserver` 拦截正文图片，把 `src`/`srcset` 暂存为 `data-*`
- 图片滚动到可视区域附近（提前 600px）才真正加载
- 首屏前 2 张图保持立即加载（避免首屏空白）
- 不支持的旧浏览器自动降级（不拦截加载，但仍有多源兜底）

**多源兜底**
- 每张图可带一组候选地址：`data-sources="外链|本地路径|备用源"`（按优先级）
- 因为 Halo 渲染时可能重写 img 标签并丢掉自定义属性，兜底地址**另外编码在 `src` 的 `#fb=` 片段里**；URL 片段不会发给服务器，不影响 CDN 缓存和防盗链
- 加载失败（`error` 事件，捕获阶段监听）自动切下一个源
- 主源 **3.5 秒**还没加载出来也会主动切换，避免访客干等外链超时
- 切源时清除 `srcset`/`sizes`，防止浏览器仍按旧候选取图
- 所有源都失败时保留灰底占位，不显示破图文字

搬运脚本 `acg_migrate.py` 输出的图片顺序是**外链优先、本地兜底**；`data-sources` 里的源数量不限，所以多个图床也能依次回退。

## 部署步骤

在服务器上执行：

```bash
# 1. 拉取最新代码（拿到补丁文件）
cd /opt/acg-resource-site/repo
git pull --ff-only

# 2. 备份服务器当前主题模板
sudo cp /opt/halo-data/themes/theme-earth/templates/post.html \
        /opt/halo-data/themes/theme-earth/templates/post.html.bak-lazyload

# 3. 用补丁覆盖
sudo cp deploy/theme-earth-patch/post.html \
        /opt/halo-data/themes/theme-earth/templates/post.html

# 4. 重启 Halo（使主题模板重新加载）
sudo systemctl restart halo
```

> 注意：路径需按你服务器实际目录调整（`/opt/halo-data` 是文档示例，也可能是其他挂载路径）。

## 重要：通过 API 修改文章正文后必须重新发布

Halo 把文章内容分成「头版本」(`spec.headSnapshot`) 和「已发布版本」(`spec.releaseSnapshot`)，前台渲染的是**后者**。

`PUT /apis/api.console.halo.run/v1alpha1/posts/{name}/content` 只更新头版本。如果改完不发布，用 API 读 `head-content` 看是新内容，但访客看到的仍是旧正文（响应头是 `no-store`，不是缓存问题，加随机参数也没用）。

改完正文后补一次发布：

```bash
PUT /apis/api.console.halo.run/v1alpha1/posts/{name}/publish
Body: {"publish": true}
```

发布后用文章列表接口确认 `headSnapshot == releaseSnapshot` 即生效。新建文章时 `create_post()` 已经带这一步，只有「更新已有文章」容易漏。

## 验证

部署后打开任意一篇 COS 图包文章（如「水淼 回复术士 芙蕾雅」），按 F12 打开开发者工具 → Network 面板：

1. **首次打开**只应看到少量图片请求（前 2 张 + 首屏可见的）
2. 向下滚动时，图片才陆续发起请求
3. 图片 `<img>` 标签上应有 `data-src` 属性（未加载时）或已加载

验证多源兜底：打开一篇搬运的游戏文章，在 F12 → Network 里把某个图片域名设为 Block（或断网模拟），应能看到该图在约 3.5 秒后自动改用 `/upload/` 的本地地址重新请求并显示。

## 回滚

如果出现问题，恢复备份即可：

```bash
sudo cp /opt/halo-data/themes/theme-earth/templates/post.html.bak-lazyload \
        /opt/halo-data/themes/theme-earth/templates/post.html
sudo systemctl restart halo
```

## 调优参数

补丁脚本中有两个可调参数（在 `post.html` 里搜索 `lazy-image-loader`）：

- `EAGER_COUNT = 2`：首屏立即加载的图片数，可调大（如 5）让首屏多预载几张
- `ROOT_MARGIN = "600px 0px"`：提前加载的距离，调大（如 1000px）会滚动更顺滑但提前加载更多
- `FALLBACK_TIMEOUT = 3500`：主源超时切下一个源的毫秒数。外链优先时可适当调小（如 2000）让切换更快；调太大访客会盯着空白等

> 图片源的优先顺序由搬运脚本 `acg_migrate.py` 写入正文时决定，主题脚本只按 `data-sources` 的顺序依次尝试。
