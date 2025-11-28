# Implementation Guide: 管线优化与智能抽取

**Feature**: 001-pipeline-optimization  
**Created**: 2025-11-28  
**Status**: Ready for Implementation  

## 🎯 实施目标

针对你的管线进行优化，核心是实现：
1. **LLM智慧归纳** - 发挥大模型对法律知识点的理解和丰富能力
2. **用户确认机制** - 导出前必须让用户确认最终卡片
3. **语义理解抽取** - 超越简单关键词匹配，理解法律概念关联

## 🔧 技术约束（严格遵守）

- **语言**: Python为主，保持现有项目结构
- **前端**: 保持Streamlit实现，不添加复杂功能  
- **制卡**: 继续使用genanki包，保持兼容性
- **LLM调用**: 沿用现有DeepSeekClient，无需改动底层调用
- **改动原则**: 最小改动，避免过度工程化，保持代码可运行性

## 📋 实施任务清单

基于详细任务规划，以下是具体的实施步骤：

### 阶段1: 项目初始化 (立即开始)

#### T001: 环境检查与备份
```bash
# 检查开发环境
cd c:\CODE\Python\anki_assist
.venv\Scripts\activate
python -c "import streamlit, langgraph, genanki; print('环境正常')"

# 备份关键文件
cp pipeline/nodes/generate_cards.py pipeline/nodes/generate_cards.py.backup
cp pipeline/nodes/extract.py pipeline/nodes/extract.py.backup  
cp app/streamlit_app.py app/streamlit_app.py.backup
```

#### T002: 创建优化模块结构
```python
# 创建新的优化模块
# pipeline/nodes/induction.py - LLM智慧归纳功能
# pipeline/nodes/confirmation.py - 用户确认管理
```

### 阶段2: 数据模型增强 (基础支撑)

#### T003: 更新模型定义
```python
# 在 models/schemas.py 中添加优化字段

class KnowledgePoint(BaseModel):
    # 现有字段保持不变...
    
    # 新增优化字段
    semantic_matches: List[str] = []  # 语义匹配的相关关键词
    induction_quality: float = 0.0    # LLM归纳质量评分
    induction_notes: str = ""         # 归纳过程说明

class Card(BaseModel):
    # 现有字段保持不变...
    
    # 新增优化字段  
    llm_induction: str = ""           # LLM归纳过程描述
    user_confirmed: bool = False      # 用户确认状态
    confirmation_time: Optional[datetime] = None  # 确认时间
```

### 阶段3: 核心功能实现 (重点突破)

#### T004: LLM智慧归纳功能
```python
# pipeline/nodes/induction.py

INDUCTION_PROMPT = """
基于以下法律知识点，生成高质量的学习卡片。要求：

1. 保持原文准确性，不进行主观臆测
2. 对学习内容进行适当归纳，提升记忆效果  
3. 问题要清晰明确，答案要准确完整
4. 可以适当丰富表达方式，但不得改变原意

知识点: {knowledge_content}
证据片段: {evidence}
来源: {source_doc} ({source_loc})

请生成问答卡片，展现你的理解智慧：
"""

def generate_cards_with_intelligence(items, client, model, max_cards_per_item=3):
    """LLM智慧归纳生成卡片"""
    cards = []
    for item in items:
        prompt = INDUCTION_PROMPT.format(
            knowledge_content=item.content,
            evidence=item.evidence,
            source_doc=item.source_doc,
            source_loc=item.source_loc
        )
        
        # 调用LLM进行智慧归纳
        response = client.generate(prompt, model=model)
        card_data = parse_llm_response(response)
        
        # 创建卡片并记录归纳过程
        card = Card(
            Question=card_data['question'],
            Answer=card_data['answer'],
            SourceDoc=item.source_doc,
            SourceLoc=item.source_loc,
            Tags=item.tags,
            Evidence=item.evidence,
            llm_induction=f"基于{item.title}进行归纳总结",
            user_confirmed=False  # 初始状态为未确认
        )
        cards.append(card)
    
    return cards
```

#### T005: 语义理解关键词抽取
```python
# pipeline/nodes/extract.py 增强

SEMANTIC_UNDERSTANDING_PROMPT = """
请分析以下法律文档内容，找出与关键词"{keywords}"相关的所有知识点。

要求：
1. 包括直接提及关键词的内容
2. 包括语义相关的内容（如同义词、相关概念）
3. 包括法律上相关的条文和解释
4. 保持原文准确性，不添加外部信息

文档内容: {document_content}
关键词: {keywords}

请返回相关的知识点列表。
"""

def extract_with_semantic_understanding(documents, keywords, client, model):
    """基于语义理解的关键词抽取"""
    doc_content = combine_documents_content(documents)
    prompt = SEMANTIC_UNDERSTANDING_PROMPT.format(
        document_content=doc_content,
        keywords=", ".join(keywords)
    )
    
    # 调用LLM进行语义理解
    response = client.generate(prompt, model=model)
    items = parse_semantic_response(response)
    
    # 记录语义匹配信息
    for item in items:
        item.semantic_matches = extract_related_concepts(item.content, keywords)
    
    return items
```

#### T006: 用户确认界面增强
```python
# app/streamlit_app.py 增强

def render_card_with_confirmation(card, index):
    """渲染带确认功能的卡片"""
    col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
    
    with col1:
        # 确认checkbox
        confirmed = st.checkbox(
            "确认", 
            value=card.user_confirmed,
            key=f"confirm_{index}"
        )
        card.user_confirmed = confirmed
        
    with col2:
        # 显示卡片内容
        st.markdown(f"**Q**: {card.Question}")
        st.markdown(f"**A**: {card.Answer}")
        
    with col3:
        # 显示LLM归纳信息
        if card.llm_induction:
            with st.expander("LLM归纳"):
                st.write(card.llm_induction)
        st.caption(f"质量: {card.quality:.2f}")

def validate_cards_before_export(cards):
    """导出前确认检查"""
    confirmed_cards = [c for c in cards if c.user_confirmed]
    if len(confirmed_cards) == 0:
        st.warning("请至少确认一张卡片")
        return None
    
    return confirmed_cards
```

#### T007: 管线集成优化
```python
# pipeline/graph.py 更新

@entrypoint(checkpointer=InMemorySaver())
def run_pipeline(input: PipelineInput) -> PipelineOutput:
    # 现有逻辑保持不变...
    
    # 优化后的抽取逻辑
    if input.keywords:
        # 使用语义理解的关键词抽取
        extracted_items = extract_with_semantic_understanding(
            documents, input.keywords, client, model=config.extract_model
        )
    else:
        # 保持现有的全局抽取逻辑
        extracted_items = chunk_documents_to_items(documents)
    
    # 使用LLM智慧归纳生成卡片
    cards = generate_cards_with_intelligence(
        extracted_items, client=client, model=config.card_model,
        max_cards_per_item=config.max_cards_per_item
    )
    
    # 质量控制（简化版）
    cards = quality_gate(cards, config.min_quality)
    cards = deduplicate_cards(cards, config.dedup_threshold)
    
    # 返回结果（保持现有格式）
    return PipelineOutput(
        documents=[d.model_dump() for d in documents],
        extracted_items=[i.model_dump() for i in extracted_items],
        cards=[c.model_dump() for c in cards],
        errors=errors
    )
```

## 🧪 测试验证

### 功能测试
```python
# 测试语义理解
def test_semantic_understanding():
    test_doc = "反不正当竞争法规定，经营者不得实施不正当竞争行为"
    keywords = ["不正当竞争"]
    items = extract_with_semantic_understanding([test_doc], keywords, client, "DeepSeek-V3")
    assert len(items) > 0
    assert any("不正当竞争" in item.content for item in items)

# 测试LLM归纳
def test_llm_induction():
    test_item = KnowledgePoint(
        title="测试法条",
        content="经营者不得实施不正当竞争行为",
        type="Statute"
    )
    cards = generate_cards_with_intelligence([test_item], client, "DeepSeek-V3")
    assert len(cards) > 0
    assert cards[0].llm_induction != ""
```

### 集成测试
```python
# 测试完整流程
def test_pipeline_optimization():
    input = PipelineInput(
        file_paths=["test_legal_doc.pdf"],
        keywords=["不正当竞争"],
        # 其他必要参数...
    )
    
    output = run_pipeline(input)
    assert len(output.cards) > 0
    assert all(card.user_confirmed == False for card in output.cards)  # 初始状态
```

## 🚀 部署与验证

### 启动测试
```bash
# 启动应用
.venv\Scripts\python -m streamlit run app/streamlit_app.py --server.port 8501

# 功能验证步骤：
# 1. 上传法律文档
# 2. 输入关键词测试语义理解
# 3. 查看生成的卡片是否有LLM归纳痕迹
# 4. 测试用户确认流程
# 5. 验证导出功能
```

## ⚠️ 注意事项

1. **保持简洁**: 避免添加不必要的复杂功能
2. **原文保真**: LLM归纳不能改变法律条文本意
3. **用户控制**: 确认机制必须清晰易用
4. **性能考虑**: LLM调用要合理控制，避免过度API调用
5. **错误处理**: 完善的异常处理，确保系统稳定性

## 📊 成功标准

- ✅ LLM能对法律知识点进行有效归纳总结
- ✅ 用户可以在导出前确认最终卡片内容
- ✅ 语义理解能发现关键词的相关概念
- ✅ 保持现有功能不受影响
- ✅ 代码始终保持可运行状态

现在你可以按照这个实施指南开始代码优化，重点先实现核心功能，确保每步都可运行！