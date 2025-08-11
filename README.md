## 法律文档 → Anki 闪卡助手（Streamlit + DeepSeek + genanki）

一个本地运行的小工具：上传法律相关文档（docx/pdf/txt）与关键词 → 基于原文做结构化抽取与制卡 → 一键导出 `.apkg` 直接导入官方 Anki。

- 只做“基于原文的排版组织”，不补充外部知识/不臆测
- OpenAI 兼容调用，支持 `DeepSeek-V3`、`DeepSeek-R1`
- 前端使用 Streamlit，内置人工复核界面与质量阈值/去重阈值
- 导出使用 `genanki`，模板简洁好看，含来源与证据片段

### 功能清单（P0）
- 多文件上传：`pdf`、`docx`、`txt`（默认不启用 OCR）
- LLM 抽取：法条/司法解释/案例要点/关键词命中（严格依据原文）
- 生成卡片：Q/A 与 Cloze 两类模板，附来源与证据片段
- 质量控制：质量分过滤 + 文本相似度去重
- 人工复核：可视化预览、勾选导出
- 一键导出 `.apkg` 文件

### 技术栈
- 前端：`streamlit`
- LLM：OpenAI 兼容 API（`DeepSeek-V3`、`DeepSeek-R1`）
- 编排：当前为简化顺序管线（后续计划迁移至 LangGraph 正式编排）
- 解析：`PyMuPDF`（pdf）、`python-docx`（docx）
- 制卡与导出：`genanki`
- 数据模型：`pydantic`

## 快速开始（Windows / uv）

你已安装 `uv`。以下步骤全部使用 uv 完成虚拟环境与依赖管理。

### 1) 进入项目目录
```powershell
cd C:\CODE\python\anki_assis
```

### 2) 创建虚拟环境
```powershell
uv venv .venv
```

### 3) 安装依赖
```powershell
uv pip install -r requirements.txt -p .venv
```

### 4) 配置 API（两种方式）
- 方式 A：直接在应用左侧边栏输入 `Base URL` 与 `API Key`
- 方式 B：使用 `.env` 文件（应用会自动读取）

`.env` 示例（放在项目根目录）
```ini
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_API_KEY=替换为你的Key
```

### 5) 启动应用
```powershell
uv run -p .venv streamlit run app/streamlit_app.py --server.port 8501
```
- 打开浏览器访问：`http://localhost:8501`
- 注意：Windows 不要在命令后面追加 `| cat`（该命令在 Windows 上不可用）

## 使用说明

### Step 1 - 上传与关键词
- 上传 `pdf/docx/txt` 多个文件
- 输入关键词（换行或逗号分隔），例如：`反不当竞争`
- 侧边栏选择模型：
  - 抽取模型：默认 `DeepSeek-V3`
  - 制卡模型：可选 `DeepSeek-V3` 或 `DeepSeek-R1`
- 可调参数：
  - 去重相似度阈值（默认 0.88）
  - 最低质量分（默认 0.65）
  - 每个知识点最多卡片数（默认 3）

点击“运行抽取与制卡”。

### Step 2 - 预览与复核
- 抽取结果（结构化 JSON 片段）可展开查看
- 卡片预览：显示问/答、来源与证据、标签、质量分
- 勾选准备导出的卡片。可通过阈值滑杆快速过滤质量较低或重复内容

### Step 3 - 导出 `.apkg`
- 设置 Deck 名称（默认：`Law-Notes-YYYYMMDD-HHMM`）
- 点击“导出 Anki 包”，下载 `.apkg` 文件
- 打开官方 Anki，直接导入该 `.apkg`

## 目录结构
```
anki_assis/
├─ app/
│  └─ streamlit_app.py         # 前端 UI
├─ pipeline/
│  ├─ graph.py                 # 管线入口（P0 顺序执行，后续迁移 LangGraph）
│  └─ nodes/
│     ├─ ingest.py             # 读取 pdf/docx/txt
│     ├─ normalize.py          # 清洗与简单分句（预留）
│     ├─ extract.py            # LLM 结构化抽取（严格 JSON）
│     ├─ generate_cards.py     # LLM 生成卡片（Q/A / Cloze）
│     └─ quality.py            # 去重与质量门控
├─ llm/
│  └─ client.py                # OpenAI 兼容客户端封装（DeepSeek）
├─ anki/
│  ├─ templates.py             # genanki 模板与样式
│  └─ exporter.py              # 组装 deck 并导出 .apkg
├─ models/
│  └─ schemas.py               # Pydantic 数据模型
├─ data/
│  └─ uploads/                 # 运行时保存上传文件
├─ exports/                    # 导出 .apkg 目录
└─ requirements.txt
```

## 模型与 API 配置
- 使用 OpenAI 兼容接口，模型名建议：`DeepSeek-V3`（信息抽取/制卡）、`DeepSeek-R1`（可选用于更复杂推理）
- 在 UI 或 `.env` 中设置：
  - `DEEPSEEK_BASE_URL`，例如 `https://api.deepseek.com/v1`
  - `DEEPSEEK_API_KEY`

## 默认策略与数据结构

- 质量控制（默认值，可在侧栏调整）：
  - 去重相似度阈值：`0.88`
  - 最低质量分：`0.65`
  - 每知识点最多卡片数：`3`
- 抽取结果包含：
  - 类型（`Statute`/`JudicialInterpretation`/`Case`/`KeywordHit`）
  - 原文证据片段、来源文档名与定位（尽量保留文章层级如“第X条”）
- 卡片字段（用于 genanki）：
  - `Question`, `Answer`, `SourceDoc`, `SourceLoc`, `Tags`, `Difficulty`, `Evidence`, `quality`

## 常见问题（FAQ）
- Q: 运行时提示 `'cat' 不是内部或外部命令`？
  - A: Windows 无需使用 `| cat`，直接运行启动命令即可。
- Q: PDF 是扫描件，抽不出文字？
  - A: 当前 P0 未启用 OCR。可在后续版本集成 `RapidOCR`/`PaddleOCR`，或请提供含文本层的 PDF。
- Q: 文档很长会超出模型上下文？
  - A: 当前对超长文本做了截断（约 4 万字符）。路线图将增加分块/并发与严格 JSON 合并。
- Q: 模型输出不是严格 JSON？
  - A: 已做稳健解析，但仍建议在模型温度较低、提示词明确时运行。后续将增加函数调用/工具型约束。
- Q: 代理/网络问题？
  - A: 按需配置系统代理；如需在 `Base URL` 使用内网网关，请确认证书与路由可达。
- Q: 端口被占用？
  - A: 启动命令中修改端口，例如 `--server.port 8502`。

## 路线图（Roadmap）
- LangGraph 正式编排：分节点可视化、并发执行、检查点与断点续跑
- 文档分块/并发抽取与 JSON 合并；引入更强的 JSON 模式约束
- OCR 支持（可选开关）
- 模板可视化编辑器（前端直接编辑卡片模板与样式）
- RAG 校验（对外部法规库进行引用校验与补全，但仍保持“不新增原文之外内容”的严格模式）

## 示例（本仓库）
- 你可以直接在应用中上传本目录下的示例：
  - `中华人民共和国反不正当竞争法(2025修订)(FBM-CLI.1.5299169).pdf`
- 关键词示例：`反不当竞争`

---
如你需要调整默认阈值、卡片样式、Deck 命名规则或增加 OCR，请在 Issue/对话中说明，我会快速更新实现。
