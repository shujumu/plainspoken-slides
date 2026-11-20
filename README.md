# 最直白的汇报PPT · Plainspoken Slides

[English](README.en.md) · [MIT](LICENSE)

一个把 Word、记录和数据做成可编辑 PowerPoint 的 Agent Skill。用真实图片交代现场，用一句话讲清一页，再用原生叠化连接关键场景。适合项目汇报、案例复盘、方案评审和课堂答辩。

## 安装

在项目目录运行下面的命令，安装到 Codex 的项目技能目录。此方式使用 [skills CLI](https://github.com/vercel-labs/skills)。

```sh
npx skills add shujumu/plainspoken-slides --skill plainspoken-slides -a codex
```

也可以下载本仓库，把整个文件夹命名为 `plainspoken-slides`，复制到项目的 `.agents/skills/`，或用户目录的 `~/.agents/skills/`。安装后在 Codex 新会话中调用 `$plainspoken-slides`。其它兼容 [Agent Skills](https://agentskills.io/specification) 的工具可以按自己的技能目录安装。

- 联网找图需要当前 Agent 能访问网页或图片搜索。你也可以直接提供图片。
- 生成 PPTX 需要本地或已连接的制作工具。推荐搭配 [PPT Master](https://github.com/hugohe3/ppt-master)，本文的原生图片叠化流程用 [v6.10.0](https://github.com/hugohe3/ppt-master/releases/tag/v6.10.0) 验证过。
- 附带的 PPTX 检查脚本只需要 Python 3.9 或更新版本。要确认实际动画，使用目标播放器放映或渲染样片。

## 使用示例

> 使用 $plainspoken-slides，读附件中的试点报告和实施方案，做一份供项目评审的 15 页可编辑 PPTX。重点说明原来的堵点、各方具体做法、已验证的结果和下一阶段目标。联网找真实的官方照片，逐页标注出处。给封面和章节页加照片背景，把「项目现场 → 上线活动」做成同页背景叠化。图片内嵌，放映时离线可见。附逐页讲稿，预算图表可编辑。

改稿时可以直接说明保留范围，例如「保持原稿事实和页序，重做第 1、5、12 页背景，并检查第 5 页的叠化播放」。

## 制作流程

| 步骤 | 产出与检查 |
| --- | --- |
| 1. 定受众和目标 | 核实文件、页数、称谓、时间及播放环境 |
| 2. 梳理叙事 | 每页一个结论，为关键事实标明出处，区分实测、估算和目标 |
| 3. 搜索真实素材 | 先核对原始页面、图片说明、作者和使用条件，再保存允许使用的素材 |
| 4. 设计与制作 | 封面和章节页用照片背景，正文用原生文字、形状和可编辑图表 |
| 5. 加入动效 | 两张图片在同一个画框里分层，上层图片淡入，固定渐变遮罩保证文字可读 |
| 6. 导出并验收 | 检查源文件与交付 PPTX，逐页看渲染，代表页抽看放映或视频样片的早、中、晚画面 |

在原生 PowerPoint 中，**页面淡化**发生在两页之间，**背景叠化**发生在同一页的两张图片之间。把照片做成可单独动效的幻灯片对象，文字放在独立图层，就可以直接在 PowerPoint 里调整构图、标题和动画时序。

详细方法见[资料研究和逐页规划](references/research-and-storyboard.md)与[照片动画和导出](references/photo-motion-and-export.md)。

## 检查导出文件

在仓库目录运行以下命令，将文件路径和目标页码换成你的成品。

```sh
python scripts/inspect_pptx.py "report.pptx" --expect-slides 15 --require-photo-fade 5
```

脚本报告页序、转场、讲稿备注、嵌入图片、图表、动画及目标。增加 `--json` 可输出 JSON。指定的页数或图片淡入缺失时，退出码会是非零。这个检查能确认原生动画及其目标对象已写入文件，实际叠化效果需要通过放映或样片确认。

## 许可与致谢

本仓库的 Skill、说明与脚本采用 [MIT 许可证](LICENSE)。项目中另行查找或提供的照片、数据与品牌素材适用其各自的许可和使用条件。PPT Master 由其上游项目独立维护。[PPT Master](https://github.com/hugohe3/ppt-master) · [Agent Skills 规范](https://agentskills.io/specification)
