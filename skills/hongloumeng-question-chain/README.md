# 《红楼梦》整本书阅读问题链建构 Skill

面向高中语文教师与学生的开放技能：将阅读疑问、文本证据和阶段性反馈转化为可讨论、可追踪、可调整的问题链。适合课前备课、课堂讨论和阅读指导，也可用于审查已有问题链。

本项目是给支持 Agent Skills 的助手读取的**工作流程文件**。它不附带模型、原著全文、论文、学生数据、自动课堂记录系统，也不保证任何具体教学效果。使用时需有支持技能文件的AI环境，由使用者提供阅读材料并审核结果。

## 能做什么

| 定位 | 使用场景 | 结果 |
| --- | --- | --- |
| AI助教 | 汇总阅读疑问、选择主问题 | 疑问来源、归类及主问题候选 |
| 认知工具 | 组织跨章节材料与已有问题 | 题间联系、待核证据、修改建议 |
| 思想伙伴 | 备课设问或学生探究 | 逐步追问、阅读支架 |
| 决策伙伴 | 根据阶段性回答调整问题 | 反馈依据、修改备选和教师决定记录 |

四种定位是本项目依据教学任务作出的安排，名称不构成一套既有的、互斥的角色理论。处理过程中教师保留最终教学判断。

## 项目结构

- [SKILL.md](SKILL.md)：入口和通用规则。
- [references/](references/)：四种模式的详细操作、问题链记录表。
- [examples/](examples/)：明确标注为虚构的可复制输入示例。
- [scripts/epub_reader.py](scripts/epub_reader.py)：对受支持的用户自备 EPUB 执行本地目录检查与关键词定位。
- [assets/student-feedback-template.csv](assets/student-feedback-template.csv)：学生学习记录的空白模板。
- [tests/](tests/)：行为测试场景及运行记录说明。
- [设计依据与范围](DESIGN.md)：说明教学任务与资料来源。
- [LICENSE](LICENSE)：MIT许可。

## 在 Codex 中使用

在目标教学项目中，**将整个 `hongloumeng-question-chain` 文件夹**复制到项目目录下的 `.agents/skills/`，保留 `SKILL.md` 和 `references/` 的相对位置。例如，在项目根目录使用 PowerShell，下面的来源路径需替换为你实际保存项目的位置：

```powershell
$skillSource = 'D:/path/to/hongloumeng-question-chain'
$skillDestination = Join-Path (Get-Location) '.agents\skills'
New-Item -ItemType Directory -Force -Path $skillDestination | Out-Null
Copy-Item -LiteralPath $skillSource -Destination $skillDestination -Recurse
```

在新会话中输入：

```text
使用 $hongloumeng-question-chain，帮我检查这份《红楼梦》问题链中的题间联系。
阅读进度：……；版本：……；主问题：……；子问题：……
```

也可以将技能文件夹放在 Codex 用户技能目录下。对于从公开GitHub仓库安装，发布后可在 Codex 中使用内置的 `$skill-installer`，提供该仓库地址和技能目录路径；安装流程及发现范围以使用环境实际支持情况为准。本项目当前是独立技能目录，不自称已成为插件市场中的插件。

## 在 WorkBuddy 中使用

按 [WorkBuddy 官方技能使用说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)，打开“专家·技能·连接器”中的“技能”，点击“添加技能 → 上传技能”，选择项目发行时提供的 `hongloumeng-question-chain-workbuddy.zip`，导入后在已安装列表确认并启用。新对话中可以请求“请使用《红楼梦》问题链建构技能分析以下问题”。如当前版本没有上传入口，请核对本机版本与官方帮助。

WorkBuddy 上传版与标准版的教学规则和参考资料相同；上传版额外填写中英文展示名称、说明、版本及作者字段，以对照 [WorkBuddy 开放平台的技能字段说明](https://open.workbuddy.cn/docs/skill)。这不代表已提交至其技能市场或已经通过平台解析。另一条项目级路径是把标准技能目录放入 `.agents/skills/`；应以具体 WorkBuddy 版本的发现配置为准。Python 检索 EPUB 属于可选功能，必须具备对应的本地文件与脚本执行条件；环境不具备时改用已提供的文本片段。

从项目源文件重新生成 WorkBuddy 上传包：

```text
python scripts/build_workbuddy.py --output ../hongloumeng-question-chain-workbuddy.zip
```

本项目在 Codex 的隔离项目中测试了技能元数据发现，未在 WorkBuddy 客户端实际导入和对话，因此不能承诺所有版本均已实测兼容。

如另一工具支持 Agent Skills，请参照其文档导入这个文件夹；不同平台对技能发现、交互、文件和隐私的支持可能不同。不能将复制文本等同于该工具已完成技能安装。

## 四个使用示例

1. **整理学生疑问**：提供匿名批注与阅读范围，请它保留原话、归类，并给出主问题候选。
2. **检查问题链**：给出主问题、已设计的子问题及相关选段，请它说明前后联系、判断是否缺少整合。
3. **开展对话**：学生提出自己的判断，请它一次提出一个围绕证据或比较的追问。
4. **调整教学**：给出原题、某次匿名回答和阅读进度，请它提出可供教师取舍的补问、回读或支架。

完整的可复制输入见 [examples/虚构输入与使用方式.md](examples/虚构输入与使用方式.md)。

## 材料与核验

上传前请去除姓名、学号等识别信息，遵循所在学校的数据管理要求。至少注明年级、目标、阅读进度、使用的《红楼梦》版本和可讨论范围；有原著片段时请标明出处。不同版本、前八十回与续书，以及学生未读部分，都可能影响设问。

技能不会自动获得原著或学情，也不会自动记录课堂。生成结果应由教师或学生回到原著核对。参考资料不足时，输出应明确写明待核之处；文学解释可存在多种有依据的可能。

如果提供的是符合工具要求的 EPUB，可以使用本地检索器按回目范围定位正文或校注，具体条件及命令见 [原著证据说明](references/text-evidence.md)。检索只匹配关键词，不等于语义理解；请核对上下文、合并章节及可能使用图片显示的字形。本项目不分发原书，也不会自动从未提供的文件获得原著。

需要形成教学流程模型、整理论文研究材料或设计学生数据收集表时，可参照 [教学研究与数据说明](references/research-and-data.md)。技能可生成模板和标注清楚的模拟例子；真实教学数据须来自实际活动。技能本身不包含或训练大语言模型。

## 测试与贡献

在项目目录运行 `python tests/check_package.py` 检查结构、入口字段及本地链接；运行 `python tests/test_epub_reader.py` 检查检索器；运行 `python tests/test_workbuddy_package.py` 检查上传包的结构和指令一致性。这些检查不调用模型，也不能检验教学效果。行为场景与人工评价方式见 [tests/行为评估.md](tests/行为评估.md)。

欢迎使用者基于真实但已脱敏的课堂经验提出改进。提交示例前，确认有权分享材料，不上传受限的原著版本、论文全文、学生作业和个人信息。建议用完整输入、实际输出、预期与问题说明复现。

项目目前仅有设计者在对话环境中完成的[课堂材料手动模拟](tests/课堂材料评估摘要.md)，未完成独立教师评测、对照实验或真实课堂效果验证；请勿将输出直接表述为效果证据。

## 授权

本项目自编的技能说明、示例与测试文件按 [MIT License](LICENSE) 发布。使用者自行提供的作品版本、第三方文献、课例和学情数据不因本许可证而获得授权。建议公开发布者根据实际贡献者情况完善署名并核查上传资料的授权。
