import streamlit as st
import json
import datetime
from modules.ai_client import generate_novel_response
from modules.db_manager import init_db, save_message, get_history

# 1. 初始化頁面與資料庫
st.set_page_config(page_title="韓文網文 AI 小說家", page_icon="✍️", layout="centered")
init_db()

# 2. 側邊欄：設定與備份 (Streamlit 經典佈局)
with st.sidebar:
    st.title("⚙️ 設定")
    # API Key 輸入框
    api_key = st.text_input("Gemini API Key", type="password", placeholder="輸入你的 API Key")

    st.divider()
    st.subheader("💾 資料備份")

    # 直接從資料庫抓取歷史紀錄準備匯出
    history_data = get_history()
    json_string = json.dumps(history_data, ensure_ascii=False, indent=4)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 內建的下載按鈕，完美取代 Flet 的本地儲存
    st.download_button(
        label="📥 下載對話紀錄",
        data=json_string,
        file_name=f"novel_backup_{timestamp}.json",
        mime="application/json"
    )

# 3. 主畫面標題
st.title("✍️ 韓文網文 AI 小說家")
st.caption("輸入靈感或續寫要求，AI 將以韓國網文風格為您創作！")

# 4. 渲染歷史紀錄
# Streamlit 每次互動都會由上往下重新執行，因此這裡會自動把資料庫的對話印出來
for msg in get_history():
    # 將資料庫的 model 轉換為 streamlit 慣用的 assistant 角色圖示
    role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg["content"])

# 5. 聊天輸入框與傳送邏輯
if prompt := st.chat_input("輸入小說靈感或續寫要求..."):
    if not api_key:
        st.warning("⚠️ 請先在左側邊欄打開選單，輸入 Gemini API Key！")
        st.stop() # 終止往下執行

    # 顯示並儲存使用者的訊息
    with st.chat_message("user"):
        st.markdown(prompt)

    # 取得歷史紀錄當作上下文 (必須在存入新訊息前取得，符合 ai_client 參數預期)
    current_history = get_history()

    # 儲存剛輸入的訊息進資料庫
    save_message("user", prompt)

    # 顯示 AI 載入狀態並呼叫 API
    with st.chat_message("assistant"):
        with st.spinner("AI 小說家思考中..."):
            ai_response = generate_novel_response(
                api_key=api_key,
                history=current_history,
                new_message=prompt
            )
        # 載入完畢後顯示內容
        st.markdown(ai_response)

    # 儲存 AI 回覆進資料庫
    save_message("model", ai_response)