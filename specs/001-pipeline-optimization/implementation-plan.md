# Implementation Plan: 管线优化与智能抽取

**Feature Branch**: `001-pipeline-optimization`  
**Created**: 2025-11-28  
**Status**: Planning Phase  

## Technical Context

### Current Architecture
- **前端**: Streamlit Web界面（保持不变）
- **管线引擎**: LangGraph functional API（已集成）
- **LLM集成**: DeepSeek客户端（OpenAI兼容）
- **卡片生成**: genanki包（保持不变）
- **文档处理**: PyMuPDF + python-docx（保持不变）

### Technology Constraints
- **语言**: Python为主，保持现有项目结构
- **LLM调用**: 沿用现有DeepSeekClient，无需改动
- **前端**: 保持Streamlit实现，不添加复杂功能
- **卡片导出**: 继续使用genanki，保持兼容性

### Core Optimization Goals
1. **LLM智慧归纳**: 发挥大模型对知识点的理解和丰富能力
2. **用户确认机制**: 导出前必须让用户确认最终卡片
3. **技术实现简化**: 避免过度工程化，保持代码可运行性

## Constitution Check

根据项目章程验证：

### ✓ 原文保真原则
- 规格明确要求"谨慎丰富，基本上要忠实原文"
- LLM归纳在保持原意基础上进行适当丰富

### ✓ 质量优先原则  
- 用户确认机制确保最终卡片质量
- LLM智慧归纳提升卡片学习效果

### ✓ 用户控制原则
- 导出前确认机制给用户完全控制权
- 简化其他环节，聚焦核心功能

### ✓ LangGraph架构原则
- 保持现有节点化设计
- 在现有架构基础上优化，不破坏兼容性

### ✓ 本地优先原则
- 所有处理在本地完成
- 仅LLM API调用需要网络

## Phase 0: Research & Technical Decisions

### Research Tasks

#### RT-001: LLM智慧归纳最佳实践
**研究内容**: 如何让LLM对法律知识点进行有效归纳总结
**关键问题**:
- 如何设计prompt让LLM理解归纳 vs 改写的区别
- 如何保持法律条文的准确性同时进行学习优化
- 如何控制"丰富"的程度避免过度解读

**决策**: 采用教育性归纳prompt策略
**实现**: 设计专门的归纳prompt模板，强调学习效果和准确性平衡

#### RT-002: 用户确认界面优化
**研究内容**: Streamlit中实现高效的用户确认流程
**关键问题**:
- 如何展示卡片预览让用户快速理解内容
- 如何支持批量选择和个别调整
- 如何在不破坏现有UI的情况下集成确认环节

**决策**: 在现有预览基础上增加确认环节
**实现**: 利用Streamlit的checkbox和expander组件

#### RT-003: 语义理解vs关键词匹配
**研究内容**: LLM提示词语义理解的具体实现
**关键问题**:
- 如何设计prompt识别语义相关的法律概念
- 如何处理同义词、近义词和相关概念
- 如何平衡召回率和准确性

**决策**: 采用教育导向的语义关联prompt
**实现**: 设计理解性prompt，让LLM从学习角度识别相关内容

## Phase 1: Data Model & Contracts

### Entity Updates

#### 知识点 (KnowledgePoint) 增强
```python
# 新增字段
induction_quality: float  # LLM归纳质量评分
induction_notes: str      # 归纳过程说明
semantic_matches: List[str]  # 语义匹配的关键词
```

#### 卡片 (Card) 增强  
```python
# 新增字段  
llm_induction: str        # LLM归纳过程描述
user_confirmed: bool      # 用户确认状态
confirmation_time: datetime  # 确认时间
```

### API Contracts

#### 归纳确认接口
```
POST /api/confirm-cards
Request: {
  card_ids: string[],
  confirmed: boolean
}
Response: {
  success: boolean,
  confirmed_count: number
}
```

#### 预览获取接口
```
GET /api/cards/preview
Response: {
  cards: Card[],
  total_count: number,
  unconfirmed_count: number
}
```

## Phase 2: Implementation Plan

### 节点优化顺序

#### 1. 优化 extract.py 节点
**目标**: 增强语义理解能力
**改动**:
- 更新prompt模板，增加语义关联指令
- 添加归纳质量评估逻辑
- 保持与现有接口兼容

#### 2. 优化 generate_cards.py 节点  
**目标**: 强化LLM智慧归纳
**改动**:
- 设计专门的归纳prompt
- 添加归纳过程记录
- 保持原文保真原则

#### 3. 增强 streamlit_app.py
**目标**: 添加用户确认环节
**改动**:
- 在预览界面增加确认checkbox
- 添加导出前确认提示
- 保持现有UI风格一致

#### 4. 优化 quality.py 节点
**目标**: 简化质量评估
**改动**:
- 保留基本质量分数
- 移除复杂的多层质量保障
- 重点保障LLM归纳质量

### 代码改动原则

1. **最小改动**: 仅修改必要节点，保持其他代码不变
2. **向后兼容**: 所有改动不破坏现有功能
3. **渐进优化**: 分步骤实施，确保每步可运行
4. **聚焦核心**: 重点强化LLM归纳和用户确认，其他保持简洁

### 测试策略

1. **单元测试**: 每个优化节点独立测试
2. **集成测试**: 完整流程端到端验证  
3. **用户测试**: 确认环节用户体验验证
4. **回归测试**: 确保现有功能不受影响

## 实施优先级

### P0 - 核心功能 (必须完成)
- [ ] LLM智慧归纳prompt设计和实现
- [ ] 用户导出前确认机制
- [ ] 语义理解关键词抽取

### P1 - 优化功能 (建议完成)  
- [ ] 全局抽取文档结构识别优化
- [ ] 确认界面用户体验优化
- [ ] 归纳质量评估简化

### P2 - 增强功能 (可选完成)
- [ ] 批量确认操作优化
- [ ] 卡片预览效果增强
- [ ] 错误处理完善

## 风险评估与缓解

### 风险1: LLM归纳可能偏离原意
**缓解**: 设计严格的prompt约束，添加原文引用检查
**监控**: 用户反馈和确认率统计

### 风险2: 用户确认流程增加操作复杂度  
**缓解**: 优化UI设计，提供批量操作，保持流程简洁
**验证**: 用户体验测试

### 风险3: 代码改动影响现有功能
**缓解**: 充分的回归测试，保持改动最小化
**保障**: 分步骤实施，每步验证可运行性

## 下一步行动

1. 开始Phase 0的具体研究任务
2. 设计LLM归纳prompt模板
3. 规划用户确认界面改动
4. 制定详细的代码修改计划

**建议**: 先实现核心功能（LLM归纳+用户确认），再逐步优化其他环节，确保项目始终保持可运行状态。