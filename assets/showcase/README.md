# Showcase · 五主题成品预览

同一篇讲稿（*Everything is code*，方言 B）在五套主题下的构建产物。
每个 HTML 都是**单文件**（引擎 + 主题 + 讲稿内容全部内联），下载后双击即可放映，无需联网、无任何依赖。

| 文件 | 主题 | 风格一句话 | 预览图 |
|---|---|---|---|
| `showcase-v1-nju-replica.html` | v1 紫罗兰讲台 | jyy 原版 1:1 复刻，紫渐变标题栏（6 页初版） | [p1](preview/showcase-v1-nju-replica-p1.png) |
| `showcase-v2-zitan.html` | v2 紫檀 | 现代规范版，紫渐变色块 + 着重号 | [p1](preview/showcase-v2-zitan-p1.png) |
| `showcase-v3-paper-journal.html` | v3 纸墨学刊 | 衬线宋体、暖纸底、学刊双细线，红色学刊式题号 | [p1](preview/showcase-v3-paper-journal-p1.png) |
| `showcase-v4-chalkboard.html` | v4 墨板讲堂 | 深墨绿黑板 + 粉笔白/黄，楷体板书 | [p1](preview/showcase-v4-chalkboard-p1.png) |
| `showcase-v5-swiss-blueprint.html` | v5 瑞士图则 | 纯白 + 墨黑 + 克莱因蓝，全稿直角细线 | [p1](preview/showcase-v5-swiss-blueprint-p1.png) |

`preview/` 内是各版第 1 页（1280×720）截图，可在仓库 README 中直接引用。

## 放映键位

`←`/`→` 翻页 · `空格` 下一步（分步动画）· `O` 总览网格 · `F` 全屏 · 点击右半屏翻页 · 触屏滑动翻页

打印 / 导出 PDF：浏览器打印对话框，`@page` 已按 1280×720 预置分页。

## 这些产物是怎么来的

```
demo 讲稿（Markdown）+ references/themes/theme-vX.css
        │
        └─ python3 assets/engine/buildall 讲稿.md -o slides.html --theme 主题.css
```

想改内容 → 改讲稿重新构建；想换颜色 → 参考 `assets/palettes/`（五大高校色系覆盖片段）。
注意：v1 是"忠于原版"的历史快照（6 页），v2–v5 为 7 页且全变量化设计、换色零风险。
