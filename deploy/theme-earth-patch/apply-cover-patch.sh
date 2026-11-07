#!/usr/bin/env bash
# 部署「封面 / 壁纸 外链优先 + 本地兜底」主题补丁（4 个模板文件）。
#
# 数据层（文章 spec.cover 改成 "外链#fb=本地"、主题背景图配置）已经通过 Halo Console API
# 改好；这个脚本只负责把 4 个模板文件放到服务器上并重启 Halo，让兜底逻辑真正生效。
#
# 用法：
#   sudo bash apply-cover-patch.sh
#   THEME_DIR=/opt/halo/data/themes/theme-earth sudo bash apply-cover-patch.sh   # 手动指定主题目录
#
# 没有仓库也能跑：脚本会从 GitHub raw 下载补丁文件，失败自动切 jsDelivr。
set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/2231499412/acg-resource-site/main"
JSDELIVR="https://cdn.jsdelivr.net/gh/2231499412/acg-resource-site@main"
PATCH_DIR="deploy/theme-earth-patch"
# 左：仓库内补丁文件路径；右：主题目录内的目标相对路径
RELS=(
  "$PATCH_DIR/post.html|templates/post.html"
  "$PATCH_DIR/modules/post-card.html|templates/modules/post-card.html"
  "$PATCH_DIR/modules/featured-post-card.html|templates/modules/featured-post-card.html"
  "$PATCH_DIR/modules/hero.html|templates/modules/hero.html"
)
SUN="sudo"
[ "$(id -u)" -eq 0 ] && SUN=""

echo "==> 1/5 定位 theme-earth 主题目录"
if [ -z "${THEME_DIR:-}" ]; then
  CAND=$($SUN find / -type f -path '*/theme-earth/templates/post.html' 2>/dev/null | head -n 1 || true)
  if [ -z "$CAND" ]; then
    echo "未找到 theme-earth/templates/post.html，请手动设置 THEME_DIR 后重跑。" >&2
    exit 1
  fi
  THEME_DIR=$(dirname "$(dirname "$CAND")")
fi
[ -d "$THEME_DIR/templates/modules" ] || { echo "目录无效：$THEME_DIR" >&2; exit 1; }
echo "    $THEME_DIR"

echo "==> 2/5 下载补丁文件"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
for PAIR in "${RELS[@]}"; do
  SRC_REL="${PAIR%%|*}"
  DEST="$TMP/$(basename "$SRC_REL")"
  if ! curl -fsSL --retry 2 --connect-timeout 10 "$REPO_RAW/$SRC_REL" -o "$DEST"; then
    echo "    raw 失败，切 jsDelivr：$SRC_REL"
    curl -fsSL --retry 2 --connect-timeout 10 "$JSDELIVR/$SRC_REL" -o "$DEST"
  fi
  echo "    OK $SRC_REL ($(wc -c < "$DEST") bytes)"
done

echo "==> 3/5 校验补丁内容"
grep -q "coverFallbackScript" "$TMP/post.html"                     || { echo "post.html 缺少 coverFallbackScript" >&2; exit 1; }
grep -q "cover-fallback-loader" "$TMP/hero.html"                   || { echo "hero.html 缺少兜底脚本" >&2; exit 1; }
grep -q "data-cover-remote" "$TMP/post-card.html"                  || { echo "post-card.html 缺少 data-cover-remote" >&2; exit 1; }
grep -q "data-cover-remote" "$TMP/featured-post-card.html"         || { echo "featured-post-card.html 缺少 data-cover-remote" >&2; exit 1; }
echo "    4/4 校验通过"

echo "==> 4/5 备份并覆盖"
STAMP=$(date +%Y%m%d%H%M%S)
for PAIR in "${RELS[@]}"; do
  SRC_REL="${PAIR%%|*}"
  DST_REL="${PAIR##*|}"
  TARGET="$THEME_DIR/$DST_REL"
  BAK="$TARGET.bak-cover-$STAMP"
  [ -f "$TARGET" ] && $SUN cp -p "$TARGET" "$BAK"
  $SUN cp "$TMP/$(basename "$SRC_REL")" "$TARGET"
  echo "    $DST_REL  (备份 ${BAK##*/})"
done

echo "==> 5/5 重启 Halo（Thymeleaf 模板有缓存）"
RESTARTED=0
if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files 2>/dev/null | grep -q '^halo.service'; then
  $SUN systemctl restart halo && RESTARTED=1 && echo "    systemctl restart halo 完成"
fi
if [ "$RESTARTED" -eq 0 ] && command -v docker >/dev/null 2>&1; then
  C=$($SUN docker ps --format '{{.Names}}' 2>/dev/null | grep -i halo | head -n 1 || true)
  if [ -n "$C" ]; then
    $SUN docker restart "$C" >/dev/null && RESTARTED=1 && echo "    docker restart $C 完成"
  fi
fi
if [ "$RESTARTED" -eq 0 ]; then
  echo "    未自动识别到 Halo 服务，请手动重启 Halo 进程后刷新页面。" >&2
fi

echo
echo "完成。验证：打开首页查看源代码应含 cover-fallback-loader；"
echo "打开任一文章页，封面 img 应含 data-cover-remote，背景 div 应含 data-bg-src。"
echo "回滚：把 .bak-cover-$STAMP 备份文件改回原名并重启 Halo 即可。"
