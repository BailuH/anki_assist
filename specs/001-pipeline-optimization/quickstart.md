# Quick Start Guide: 管线优化与智能抽取

**Feature**: 001-pipeline-optimization  
**Created**: 2025-11-28  
**Status**: Ready for Implementation  

## 概述

本指南帮助开发者快速理解和实现管线优化功能，重点聚焦LLM智慧归纳和用户确认机制。

## 核心改动点

### 1. LLM智慧归纳增强

**文件**: `pipeline/nodes/generate_cards.py`

**关键改动**:
```python
# 新增LLM归纳prompt模板
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

def generate_cards_with_indelligence(items, client, model, max_cards_per_item=3):
    # 为每个知识点调用LLM进行智慧归纳
    for item in items:
        prompt = INDUCTION_PROMPT.format(
            knowledge_content=item.content,
            evidence=item.evidence, 
            source_doc=item.source_doc,
            source_loc=item.source_loc
        )
        
        # 调用LLM生成卡片
        response = client.generate(prompt, model=model)
        cards = parse_llm_response(response)
        
        # 记录归纳过程
        for card in cards:
            card.llm_induction = f"基于{item.title}进行归纳总结"
            card.induction_prompt = "v1.0_induction"
            
        yield cards
```

### 2. 用户确认界面增强

**文件**: `app/streamlit_app.py`

**关键改动**:
```python
# 在预览界面添加确认功能
def render_card_with_confirmation(card, index):
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
        # 显示归纳信息
        if card.llm_induction:
            with st.expander("LLM归纳"):
                st.write(card.llm_induction)
        st.caption(f"质量: {card.quality:.2f}")

# 导出前确认检查
def validate_cards_before_export(cards):
    confirmed_cards = [c for c in cards if c.user_confirmed]
    if len(confirmed_cards) == 0:
        st.warning("请至少确认一张卡片")
        return False
    
    if len(confirmed_cards) < len(cards):
        st.info(f"将导出 {len(confirmed_cards)} 张已确认的卡片")
    
    return confirmed_cards
```

### 3. 语义理解关键词抽取

**文件**: `pipeline/nodes/extract.py`

**关键改动**:
```python
# 新增语义理解prompt
SEMANTIC_UNDERSTANDING_PROMPT = """
请分析以下法律文档内容，找出与关键词"{keywords}"相关的所有知识点。

要求：
1. 包括直接提及关键词的内容
2. 包括语义相关的内容（如同义词、相关概念）
3. 包括法律上相关的条文和解释
4. 保持原文准确性，不添加外部信息

文档内容: {document_content}
关键词: {keywords}

请返回相关的知识点列表，每个知识点包含：
- 类型（法条/案例/解释）
- 标题
- 内容摘要
- 原文证据
- 相关程度（1-10）

返回格式为JSON数组。
"""

def extract_with_semantic_understanding(documents, keywords, client, model):
    # 构建语义理解prompt
    doc_content = combine_documents(documents)
    prompt = SEMANTIC_UNDERSTANDING_PROMPT.format(
        document_content=doc_content,
        keywords=", ".join(keywords)
    )
    
    # 调用LLM进行语义理解
    response = client.generate(prompt, model=model)
    items = parse_semantic_response(response)
    
    # 记录语义匹配信息
    for item in items:
        item.semantic_matches = extract_matched_keywords(item.content, keywords)
        
    return items
```

## 实施步骤

### 步骤1: 环境准备
```bash
# 确保项目环境正常
cd c:\CODE\Python\anki_assist
.venv\Scripts\activate
python -c "import streamlit, langgraph, genanki; print('环境正常')"
```

### 步骤2: 备份现有代码
```bash
# 备份关键文件
cp pipeline/nodes/generate_cards.py pipeline/nodes/generate_cards.py.backup
cp pipeline/nodes/extract.py pipeline/nodes/extract.py.backup  
cp app/streamlit_app.py app/streamlit_app.py.backup
```

### 步骤3: 实现LLM智慧归纳
1. 修改 `generate_cards.py`，添加归纳prompt模板
2. 实现智慧归纳函数
3. 记录归纳过程信息

### 步骤4: 实现用户确认功能
1. 修改 `streamlit_app.py`，添加确认checkbox
2. 实现导出前确认检查
3. 优化确认界面交互

### 步骤5: 实现语义理解抽取
1. 修改 `extract.py`，添加语义理解prompt
2. 实现语义匹配逻辑
3. 记录语义关联信息

### 步骤6: 测试验证
```bash
# 运行测试
python -m pytest tests/ -v
# 启动应用测试
.venv\Scripts\python -m streamlit run app/streamlit_app.py --server.port 8501
```

## 关键测试点

### 功能测试
1. **LLM归纳测试**: 上传法律文档，检查卡片是否展现理解智慧
2. **用户确认测试**: 验证确认流程是否顺畅，导出是否受控
3. **语义理解测试**: 输入关键词，检查是否能发现语义相关内容

### 兼容性测试
1. **现有功能**: 确保原有功能不受影响
2. **数据格式**: 验证Anki包生成正常
3. **界面一致性**: 保持Streamlit界面风格统一

## 常见问题解决

### Q1: LLM归纳偏离原意
**解决**: 调整prompt模板，增加约束条件，添加原文引用检查

### Q2: 用户确认流程卡顿
**解决**: 优化界面布局，提供批量操作，减少不必要的重渲染

### Q3: 语义理解不准确
**解决**: 细化prompt指令，提供法律术语词典，调整相似度阈值

## 性能优化建议

### 1. 异步处理
```python
# 对LLM归纳进行异步处理
import asyncio

async def async_generate_cards(items, client, model):
    tasks = [generate_card_async(item, client, model) for item in items]
    return await asyncio.gather(*tasks)
```

### 2. 缓存机制
```python
# 缓存LLM响应
@lru_cache(maxsize=100)
def cached_llm_induction(item_content, model):
    return generate_card_with_indelligence(item_content, model)
```

### 3. 分批处理
```python
# 分批处理大量卡片
def batch_process_cards(cards, batch_size=10):
    for i in range(0, len(cards), batch_size):
        batch = cards[i:i+batch_size]
        process_batch(batch)
```

## 下一步计划

1. 完成核心功能实现
2. 进行充分测试验证
3. 优化用户体验
4. 准备部署上线

**重点提醒**: 保持代码简洁，避免过度工程化，聚焦LLM智慧归纳和用户确认这两个核心价值点。