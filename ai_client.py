# modules/ai_client.py
from google import genai
from google.genai import types

# 韓國網文 AI 小說家 System Prompt
SYSTEM_PROMPT = """
你是一位精通韓國網路小說（如 Naver Series, KakaoPage, Novelpia）風格的資深專業小說家與編輯。
你的任務是協助使用者創作小說，請遵循以下原則：
1. 熟悉韓文網文常見題材（如：迴歸、附身、轉生、獵人、財閥、惡役千金、狀態窗系統等）。
2. 文風需具備韓國網文特色：段落簡短俐落、節奏明快、著重角色心理描寫與戲劇性衝突，並擅長製造「斷章（懸念）」。
3. 當使用者提出要求時，你不僅要幫忙「撰寫/續寫」，還要以專業編輯的角度提出「靈感建議」。
4. 適時分析使用者劇情的「優點與缺點」，並提供 2~3 個後續發展的選項供討論。
5. 請全部使用繁體中文回覆，但可帶有濃厚的韓式網文翻譯風格（如使用特定敬語感、歐巴/哥等稱呼的在地化感受）。
"""

def generate_novel_response(api_key: str, history: list, new_message: str) -> str:
    """
    呼叫最新的 Gemini API (google-genai)
    history 格式預期為: [{"role": "user"/"model", "content": "..."}]
    """
    if not api_key:
        return "⚠️ 請先在設定中輸入 Gemini API Key。"

    try:
        # 1. 初始化最新版 Client
        client = genai.Client(api_key=api_key)

        # 2. 設定 System Instruction 與生成參數
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7, # 適合創作的溫度
        )

        # 3. 轉換歷史紀錄符合最新 API 的 types.Content 格式
        # 舊版 api 使用 'model'，新版保持一致但需注意物件封裝
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
            )

        # 加入最新的一筆使用者訊息
        contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=new_message)])
        )

        # 4. 呼叫 API (建議使用 gemini-2.5-flash 速度快且聰明)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=config
        )

        return response.text

    except Exception as e:
        return f"⚠️ API 呼叫發生錯誤：{str(e)}"