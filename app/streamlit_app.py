import os
import io
import json
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Ensure project root on sys.path
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.graph import run_pipeline
from anki.exporter import export_to_apkg

load_dotenv(override=True)

st.set_page_config(page_title="法律文档→Anki", layout="wide")

if "pipeline_output" not in st.session_state:
    st.session_state.pipeline_output = None
if "cards_selected" not in st.session_state:
    st.session_state.cards_selected = {}

st.title("法律文档制卡助手")
st.caption("上传法条/司法解释/案例原文，基于原文做结构化抽取与制卡，一键导出 .apkg")

with st.sidebar:
    st.header("模型与API配置")
    base_url = st.text_input("Base URL", os.getenv("DEEPSEEK_BASE_URL", ""), placeholder="https://api.deepseek.com/v1")
    api_key = st.text_input("API Key", os.getenv("DEEPSEEK_API_KEY", ""), type="password")
    extract_model = st.selectbox("抽取模型", ["DeepSeek-V3", "DeepSeek-R1"], index=0)
    card_model = st.selectbox("制卡模型", ["DeepSeek-V3", "DeepSeek-R1"], index=0)
    st.divider()
    st.subheader("质量与去重")
    dedup_threshold = st.slider("去重相似度阈值", 0.5, 0.99, 0.88, 0.01, help="相似度≥阈值判为重复")
    min_quality = st.slider("最低质量分", 0.0, 1.0, 0.30, 0.01, help="低于该分数的卡片会被过滤；可先降到0.3再观察")
    max_cards_per_item = st.number_input("每个知识点最多卡片数", 1, 5, 3, 1)

st.subheader("Step 1 - 上传文档 & 关键词")
uploaded_files = st.file_uploader("支持 docx/pdf/txt，多文件可选", type=["pdf", "docx", "txt"], accept_multiple_files=True)
keywords_input = st.text_area("关键词（换行/逗号分隔）", value="反不当竞争")
keywords = [k.strip() for part in keywords_input.split("\n") for k in part.split(",") if k.strip()]

col1, col2 = st.columns(2)
with col1:
    run_btn = st.button("运行抽取与制卡", type="primary")
with col2:
    reset_btn = st.button("重置")

if reset_btn:
    st.session_state.pipeline_output = None
    st.session_state.cards_selected = {}
    st.experimental_rerun()

if run_btn:
    if not uploaded_files:
        st.warning("请至少上传一个文件")
    elif not api_key or not base_url:
        st.warning("请配置 Base URL 和 API Key")
    else:
        # 将上传的文件保存到 data/uploads
        os.makedirs("data/uploads", exist_ok=True)
        saved_paths = []
        for uf in uploaded_files:
            save_path = os.path.join("data", "uploads", uf.name)
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())
            saved_paths.append(save_path)
        with st.spinner("运行管线中，请稍候…"):
            try:
                output = run_pipeline(
                    file_paths=saved_paths,
                    keywords=keywords,
                    api_base=base_url,
                    api_key=api_key,
                    extract_model=extract_model,
                    card_model=card_model,
                    dedup_threshold=dedup_threshold,
                    min_quality=min_quality,
                    max_cards_per_item=int(max_cards_per_item),
                )
            except Exception as e:
                output = {"documents": [], "extracted_items": [], "cards": [], "errors": [f"运行失败: {e}"]}
        st.session_state.pipeline_output = output

output = st.session_state.pipeline_output

st.subheader("Step 2 - 抽取结果与卡片预览（可勾选导出）")
if not output:
    st.info("请先上传文档并点击运行")
else:
    docs = output.get("documents", [])
    items = output.get("extracted_items", [])
    cards = output.get("cards", [])
    errors = output.get("errors", [])

    if errors:
        for err in errors:
            st.error(err)

    with st.expander("抽取结果（结构化）", expanded=False):
        st.json({"documents": docs, "items": items[:50]})

    st.write(f"生成卡片数：{len(cards)}（根据阈值过滤后）")

    # 复核与选择
    for idx, card in enumerate(cards):
        card_id = f"card_{idx}"
        include_default = True
        quality = card.get("quality", 0)
        cols = st.columns([0.08, 0.57, 0.35])
        with cols[0]:
            st.session_state.cards_selected[card_id] = st.checkbox("选择", value=include_default, key=card_id)
        with cols[1]:
            st.markdown(f"**Q**: {card.get('Question','')}")
            st.markdown(f"**A**: {card.get('Answer','')}")
        with cols[2]:
            st.caption(f"来源：{card.get('SourceDoc','')}（{card.get('SourceLoc','')}）")
            st.caption(f"标签：{', '.join(card.get('Tags', []))}")
            st.caption(f"难度：{card.get('Difficulty', 'N/A')}  质量分：{quality:.2f}")
            with st.expander("证据片段"):
                st.write(card.get("Evidence", ""))
        st.divider()

    exportable = [c for i, c in enumerate(cards) if st.session_state.cards_selected.get(f"card_{i}")]

    st.subheader("Step 3 - 导出 .apkg")
    deck_name = st.text_input("Deck 名称", value=f"Law-Notes-{datetime.now().strftime('%Y%m%d-%H%M')}")
    if st.button("导出 Anki 包"):
        if not exportable:
            st.warning("请至少选择一张卡片")
        else:
            os.makedirs("exports", exist_ok=True)
            apkg_path = export_to_apkg(deck_name=deck_name, cards=exportable, output_dir="exports")
            with open(apkg_path, "rb") as f:
                data = f.read()
            st.success(f"已导出：{apkg_path}")
            st.download_button("下载 .apkg", data=data, file_name=os.path.basename(apkg_path), mime="application/octet-stream")
