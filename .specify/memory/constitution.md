<!-- 
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0 (Initial constitution)
- Added principles: Source Fidelity, Quality-First, User Control, LangGraph Architecture, Local-First
- Added sections: Technology Standards, Development Workflow
- Templates requiring updates: None (initial creation)
- Follow-up TODOs: None
-->

# Anki法律闪卡助手项目章程

## 核心原则

### I. 原文保真原则 (Source Fidelity)
所有知识抽取和卡片生成必须严格基于用户上传的原始文档内容，禁止添加外部知识或进行主观臆测。LLM仅用于结构化提取和重新组织现有信息，确保法律条文的准确性和权威性。

### II. 质量优先原则 (Quality-First)
建立多层质量保障机制：LLM生成质量评分、文本相似度去重、用户可配置的质量阈值过滤。每张卡片必须包含来源文档、具体位置和证据片段，确保可追溯性和可信度。

### III. 用户控制原则 (User Control)
用户必须能够完全控制整个制卡流程：自定义关键词、选择AI模型、调整质量参数、预览和手动选择最终导出的卡片。系统提供合理的默认值但允许深度定制。

### IV. LangGraph架构原则 (LangGraph Architecture)
使用LangGraph的functional API构建可扩展的节点化管线，支持检查点和断点续跑。每个处理节点职责单一、可独立测试，便于后续添加新功能或优化现有流程。

### V. 本地优先原则 (Local-First)
应用完全在本地运行，文档处理不依赖外部服务（除LLM API调用外）。用户数据保留在本地文件系统，确保法律文档的隐私性和安全性。

## 技术标准

### 技术栈规范
- 前端：Streamlit提供直观的Web界面
- LLM集成：OpenAI兼容API，优先支持DeepSeek系列模型
- 文档解析：PyMuPDF处理PDF，python-docx处理Word文档
- 卡片生成：genanki库生成标准Anki包格式
- 数据模型：Pydantic确保类型安全和数据验证
- 管线编排：LangGraph实现functional API和状态管理

### 质量控制标准
- 去重相似度阈值：默认0.88（用户可调整0.5-0.99）
- 最低质量分：默认0.30（用户可调整0.0-1.0）
- 每知识点最多卡片数：默认3张（用户可调整1-5张）
- 卡片必须包含：问题、答案、来源文档、具体位置、标签、难度、证据片段、质量分

## 开发流程

### 节点开发规范
每个管线节点必须：
1. 明确定义输入输出Schema（使用Pydantic模型）
2. 包含完整的错误处理和异常捕获
3. 提供详细的日志记录便于调试
4. 编写对应的单元测试
5. 支持独立运行和测试

### 代码审查要求
- 所有PR必须通过章程合规性检查
- 新功能必须包含相应的测试用例
- 文档必须同步更新（README、API文档等）
- 性能影响评估（特别是LLM调用成本）

### 版本管理策略
- 使用语义化版本控制（MAJOR.MINOR.PATCH）
- 破坏性变更必须升级主版本号
- 新功能添加升级次版本号
- 问题修复和优化升级修订号
- 每个版本必须更新变更日志

## 治理规则

本章程作为项目开发的最高指导原则，所有技术决策和代码实现必须符合上述原则。章程的修订需要：

1. 提出书面修改建议并说明理由
2. 评估修改对现有功能的影响
3. 获得项目维护者批准
4. 更新版本号和最后修改日期
5. 同步更新相关文档和模板

项目维护者负责定期审查章程的执行情况，确保开发活动与既定原则保持一致。对于复杂的技术决策，应优先参考章程中的相关原则。

**版本**: 1.0.0 | **批准**: 2025-11-28 | **最后修改**: 2025-11-28
