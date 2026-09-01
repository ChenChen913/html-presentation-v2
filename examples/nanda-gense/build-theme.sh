#!/usr/bin/env bash
# 合成 nanda 项目主题：v2 本体 + 项目 override（lessons A11：改源片段后必须重合成）
set -e
cd "$(dirname "$0")"
cat theme-v2-zitan.css theme-nanda-override.css > theme-v2-nanda.css
echo "[ok] theme-v2-nanda.css 已合成（本体 + override）"
