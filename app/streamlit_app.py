import os
import io
import json
#解析时间用于牌组的名称
from datetime import datetime
import streamlit as st
from streamlit_tags import st_tags
from dotenv import load_dotenv
from models.schemas import PipelineInput

# sys库用于与python解释器交互，提供了若干“系统级的方法接口”
# 这段代码的目的是要
import sys
#获取当前streamlit app的绝对路径，“..”代表上一级目录
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 将当前文件搜索路径设置为优先级最高
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.graph import run_pipeline
from anki.exporter import export_to_apkg

load_dotenv(override=True) #override参数决定是否覆盖同名变量


#=================================================================================================================================

# 1.页面元信息（必须在生成其他 Streamlit 元素之前调用），layout="wide" 让页面横向更宽
st.set_page_config(page_title="法律文档→Anki", layout="wide")

# 初始化session_state用于保存图运行结果和用户是否保留
if "pipeline_output" not in st.session_state:
    st.session_state.pipeline_output = None
if "cards_selected" not in st.session_state:
    st.session_state.cards_selected = {}

#=================================================================================================================================

# 2.标题文字与标题说明
st.title("法律文档制卡助手")
st.caption("上传法条/司法解释/案例原文，基于原文做结构化抽取与制卡，一键导出 .apkg")

#=================================================================================================================================

# 3.侧栏填写用于填写相关配置信息
with st.sidebar:
    # 分级标题
    st.header("模型与API配置")
    #文本输入，先从操作系统抓取环境变量，如果无返回空字符串（text_input接口要求）
    #用户也可以清空输入框自己输入
    base_url = st.text_input("Base URL", os.getenv("DEEPSEEK_BASE_URL", ""), placeholder="https://api.deepseek.com/v1")
    api_key = st.text_input("API Key", os.getenv("DEEPSEEK_API_KEY", ""), type="password")
    #单选框
    extract_model = st.selectbox("抽取模型", ["DeepSeek-V3", "DeepSeek-R1"], index=0)
    card_model = st.selectbox("制卡模型", ["DeepSeek-V3", "DeepSeek-R1"], index=0)
    #分割线    
    st.divider()
    #分级子标题
    st.subheader("质量与去重")
    #滑动条 
    dedup_threshold = st.slider("去重相似度阈值", 0.5, 0.99, 0.88, 0.01, help="相似度≥阈值判为重复")
    min_quality = st.slider("最低质量分", 0.0, 1.0, 0.30, 0.01, help="为了保证卡片质量，低于该分数的卡片会被过滤")
    #数字框
    max_cards_per_item = st.number_input("每个知识点最多卡片数", 1, 5, 3, 1)
#=================================================================================================================================
#主页面布置

st.subheader("Step 1 - 上传文档 & 关键词")
# 上传文件
uploaded_files = st.file_uploader("支持 docx/pdf/txt，多文件可选", type=["pdf", "docx", "txt"], accept_multiple_files=True)

# 标签交互式添加关键词，返回一个列表
keywords = st_tags(
    label='关键词',
    text='回车添加',
    value=['反不当竞争'],      # 默认值
    suggestions=['反垄断', '商业秘密']  # 智能补全
)

# 设置两列
col1, col2 = st.columns(2) 
# 上下文写法，按钮设置，每次点击按钮会触发重新运行脚本 
with col1:
    run_btn = st.button("运行抽取与制卡", type="primary")
with col2:
    reset_btn = st.button("重置")
#=================================================================================================================================
# 第一步运行管线时的判断逻辑与数据流

if reset_btn:
    st.session_state.pipeline_output = None
    st.session_state.cards_selected = {}
    st.rerun()

if run_btn:
    if not uploaded_files:
        st.warning("请至少上传一个文件")
    elif not api_key or not base_url:
        st.warning("请配置 Base URL 和 API Key")
    else:
        # 将上传的文件保存到 data/uploads
        os.makedirs("data/uploads", exist_ok=True)
        # 保存上传文件的绝对路径/相对路径，便于后续代码需要
        saved_paths = []
        # 将文件路径拼接后写入指定路径并保存（会覆盖同名文件）
        for uf in uploaded_files:
            save_path = os.path.join("data", "uploads", uf.name)
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())
            saved_paths.append(save_path)

        #信息反馈：配合with形成旋转加载效果
        with st.spinner("运行管线中，请稍候…"):
            try:
                input = PipelineInput(file_paths= saved_paths,
                                      keywords=keywords,
                                      api_base=base_url,
                                      api_key=api_key,
                                      extract_model=extract_model,
                                      card_model=card_model,
                                      dedup_threshold=dedup_threshold,
                                      min_quality=min_quality,
                                      max_cards_per_item=int(max_cards_per_item))
                
                thread_config = {
                    "configurable": {
                        "thread_id": "1001"
                }
}
                output = run_pipeline.invoke(input, config = thread_config)
            except Exception as e:
                output = {"documents": [], "extracted_items": [], "cards": [], "errors": [f"运行失败: {e}"]}
        st.session_state.pipeline_output = output

output = st.session_state.pipeline_output
#=================================================================================================================================
# 第二步运行判断逻辑

st.subheader("Step 2 - 抽取结果与卡片预览（可勾选导出）")
if not output:
    # 信息反馈：彩色提示框
    st.info("请先上传文档并点击运行")
else:
    docs = output.documents
    items = output.extracted_items
    cards = output.cards
    errors = output.errors

    if errors:
        for err in errors:
            st.error(err)
    
    # 可折叠/展开的容器组件
    with st.expander("抽取结果（结构化）", expanded=False):
        # 能先将python对象如list，dict等转为json格式，再用美化界面展示
        st.json({"documents": docs, "items": items[:50]})

    st.write(f"生成卡片数：{len(cards)}（根据阈值过滤后）")

    # 卡片列表渲染（复核并选择）- 增强版，支持LLM归纳展示和用户确认
    st.info("💡 新功能：系统现在使用LLM智慧归纳生成卡片，您可以查看归纳过程并确认最终内容")
    
    for idx, card in enumerate(cards): # 将序列类型打上“下标”
        card_id = f"card_{idx}"
        include_default = True
        quality = card.quality
        # 切分三列的比例 - 调整为更好的布局
        cols = st.columns([0.1, 0.5, 0.4])

        with cols[0]:
            # 展示界面为打勾框，并对streamlit_state的字典进行更新
            # checkbox的特性有返回值为bool型，状态持久（对key唯一标识进行赋值）、触发重跑
            st.session_state.cards_selected[card_id] = st.checkbox("选择", value=include_default, key=card_id)
            
        with cols[1]:
            # 展示markdown
            st.markdown(f"**Q**: {card.Question}")
            st.markdown(f"**A**: {card.Answer}")
            
            # 显示LLM归纳过程（如果有）
            if hasattr(card, 'llm_induction') and card.llm_induction:
                with st.expander("🧠 LLM归纳过程"):
                    st.write(card.llm_induction)
            
        with cols[2]:
            #小号文字，颜色更淡，用于写补充性的文字
            st.caption(f"来源：{card.SourceDoc}（{card.SourceLoc}）")
            st.caption(f"标签：{', '.join(card.Tags)}")
            st.caption(f"难度：{card.Difficulty}  质量分：{quality:.2f}")
            
            # 显示归纳提示版本（如果有）
            if hasattr(card, 'induction_prompt') and card.induction_prompt:
                st.caption(f"归纳方式: {card.induction_prompt}")
            
            with st.expander("证据片段"):
                st.write(card.Evidence)
        st.divider()

    exportable = [c for i, c in enumerate(cards) if st.session_state.cards_selected.get(f"card_{i}")]

    st.subheader("Step 3 - 导出 .apkg")
    deck_name = st.text_input("Deck 名称", value=f"Law-Notes-{datetime.now().strftime('%Y%m%d-%H%M')}")
    
    # 添加导出前确认机制
    if len(exportable) > 0:
        st.info(f"已选择 {len(exportable)} 张卡片准备导出")
        
        # 显示即将导出的卡片预览
        with st.expander("预览即将导出的卡片"):
            for card in exportable[:5]:  # 显示前5张
                st.markdown(f"**Q**: {card.Question}")
                st.markdown(f"**A**: {card.Answer}")
                st.markdown("---")
            if len(exportable) > 5:
                st.caption(f"... 还有 {len(exportable) - 5} 张卡片")
        
        # 确认复选框
        confirm_export = st.checkbox("我已确认上述卡片内容准确无误，准备导出", key="confirm_export")
        
        if st.button("导出 Anki 包", disabled=not confirm_export):
            if not confirm_export:
                st.warning("请先确认卡片内容无误")
            else:
                os.makedirs("exports", exist_ok=True)
                apkg_path = export_to_apkg(deck_name=deck_name, cards=exportable, output_dir="exports")
                with open(apkg_path, "rb") as f:
                    data = f.read()
                st.success(f"已导出：{apkg_path}")
                st.download_button("下载 .apkg", data=data, file_name=os.path.basename(apkg_path), mime="application/octet-stream")
    else:
        st.warning("请至少选择一张卡片")
