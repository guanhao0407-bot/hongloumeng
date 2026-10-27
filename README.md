# 《红楼梦》整本书阅读问题链建构 Skill

面向高中语文整本书阅读，帮助教师和学生整理阅读疑问、关联文本与问题、展开递进追问，并依据学习反馈修订问题链。

## 下载与使用

- [下载 Codex／通用 Agent Skills 版](https://github.com/guanhao0407-bot/hongloumeng/raw/refs/heads/main/downloads/hongloumeng-question-chain-open-source.zip)
- [下载 WorkBuddy 上传版](https://github.com/guanhao0407-bot/hongloumeng/raw/refs/heads/main/downloads/hongloumeng-question-chain-workbuddy.zip)
- [阅读完整使用说明](skills/hongloumeng-question-chain/README.md)
- [查看技能说明和源文件](skills/hongloumeng-question-chain/SKILL.md)

Codex：解压通用版后，将整个 `hongloumeng-question-chain` 文件夹复制到项目的 `.agents/skills/`，在新会话中请求使用 `$hongloumeng-question-chain`。也可以在 Codex 中使用内置 `$skill-installer`，提供本仓库地址和目录 `skills/hongloumeng-question-chain`。具体步骤与限制见完整使用说明。

WorkBuddy：下载上传版 ZIP，在“专家·技能·连接器 → 技能 → 添加技能 → 上传技能”中选择该文件。上传版按照 WorkBuddy 开放平台文档补充了展示字段；尚未在 WorkBuddy 客户端完成实际导入与对话验证，界面及支持情况以使用者的版本为准。

## 四种教学定位

| 教学困难 | AI定位 | 主要任务 |
| --- | --- | --- |
| 教师预设偏重、学生发问不足 | AI助教 | 整理阅读疑问，提出主问题候选 |
| 章节联系松散、问题衔接不畅 | 认知工具 | 梳理章节证据与问题之间的联系 |
| 问题层次不清、理解深化不足 | 思想伙伴 | 面向教师设计递进追问，或引导学生说明依据 |
| 学情反馈滞后、问题调整不及时 | 决策伙伴 | 根据实际反馈提供补问、回读与支架备选 |

四种定位是针对本项目教学任务的应用划分。教师负责审核文本依据、选择设问并决定是否采纳调整；学生可以审查和修正AI输出。

## 原著、隐私与研究边界

本仓库不包含原著、第三方文献全文或学生资料。使用者可以自行提供有权使用的《红楼梦》文本或匿名阅读记录；EPUB本地检索工具支持部分目录格式，检索结果需回书核验。不同版本和阅读进度会影响可讨论内容。使用学生资料前，请按学校及研究机构的要求处理身份信息。

技能是工作流程文件，依托使用环境已有的AI模型；不会自动采集课堂数据，也不会自行训练模型。本项目已经进行软件检查与设计者手动模拟，尚无独立教师测评或真实课堂效果验证；详情见[测试说明](skills/hongloumeng-question-chain/tests/行为评估.md)。

## 许可

项目自编文件采用 [MIT License](LICENSE)。使用者自行提供的作品版本、论文、课例或数据的权利，仍以各自的授权为准。

