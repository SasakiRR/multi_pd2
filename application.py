import os
import time
import pytz
import json
import datetime
import numpy as np
from PIL import Image
import streamlit as st
from openai import OpenAI

# APIキーの設定
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# 定数定義
USER_NAME = "user"
ASSISTANT_NAME = "assistant"
ASSISTANT_NAME2 = "assistant2"
PERSUADER_PROMPTFILE = "prompts/persuaderprompt2.txt"
PERSUADEE_PROMPTFILE0 = "prompts/persuadeeprompt0.txt"
PERSUADEE_PROMPTFILE1 = "prompts/persuadeeprompt1.txt"
PERSUADEE_PROMPTFILE2 = "prompts/persuadeeprompt2.txt"
i_turn = 5
p_turn = 5

# 画像読み込み
user_icon = np.array(Image.open("icons/user.png"))
assistant_icon = np.array(Image.open("icons/persuader_bot.png"))
assistant2_icon = np.array(Image.open("icons/persuadee_bot.png"))

# ページ遷移のフラグの初期化
if "page_control" not in st.session_state:
    st.session_state.page_control = 0

# トピックの初期化
if "topic" not in st.session_state:
    st.session_state.topic = ""

# 事前アンケートの初期化
if "gender" not in st.session_state:
    st.session_state.gender = ""
if "age" not in st.session_state:
    st.session_state.age = ""
if "name" not in st.session_state:
    st.session_state.name = ""
if "meal1" not in st.session_state:
    st.session_state.meal1 = ""
if "meal2" not in st.session_state:
    st.session_state.meal2 = ""

# 表示用チャットログの初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# 説得者プロンプトの初期化
if "persuaderprompt" not in st.session_state:
    with open(PERSUADER_PROMPTFILE, "r") as f:
        st.session_state.persuaderprompt = f.read()

# 被説得者プロンプトの初期化
if "persuadeeprompt0" not in st.session_state:
    with open(PERSUADEE_PROMPTFILE0, "r") as f:
        st.session_state.persuadeeprompt0 = f.read()
if "persuadeeprompt1" not in st.session_state:
    with open(PERSUADEE_PROMPTFILE1, "r") as f:
        st.session_state.persuadeeprompt1 = f.read()
if "persuadeeprompt2" not in st.session_state:
    with open(PERSUADEE_PROMPTFILE2, "r") as f:
        st.session_state.persuadeeprompt2 = f.read()

# プロンプト用チャットログの初期化
if "prompt_chat_log" not in st.session_state:
    st.session_state.prompt_chat_log = "対話エージェント："

# ターン数の初期化
if "turn" not in st.session_state:
    st.session_state.turn = 1

# チャット入力無効化の初期化
if "is_chat_input_disabled" not in st.session_state:
    st.session_state.is_chat_input_disabled = True

# チャット入力欄の初期化
if "input_message" not in st.session_state:
    st.session_state.input_message = "ここにメッセージを入力"

# 被説得者が発話するかどうかのフラグの初期化
if "is_persuadee_speak" not in st.session_state:
    st.session_state.is_persuadee_speak = True

# 日時の初期化
if "dt_now" not in st.session_state:
    st.session_state.dt_now = ""

# ChatGPTによるレスポンス取得の関数
def response_chatgpt(prompt: str):
    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}],
        model="gpt-4.1",
        stream=True,
    )
    return response

# 事前アンケートの関数
def pre_survey():
    st.title("生活習慣に関するアンケート")
    st.write(
        "以下の生活習慣に関するアンケート全てに答えてください。"
    )
    st.session_state.gender = st.radio(
        label="あなたの性別を教えてください", 
        options=["男性", "女性", "その他"], 
        index=0
        )
    st.session_state.age = int(st.number_input("あなたの年齢を教えてください", step=1))
    st.session_state.name = st.text_input("対話内で使用する名前を入力してください")
    st.session_state.meal1 = st.radio(
        label="普段どれくらいの頻度で1日に3食食べていますか？", 
        options=["5：毎日", "4：週に3〜4回程度", "3：週に1〜2回程度", "2：月に1〜2回程度", "1：ほとんどの日に3食食べない"], 
        index=2
        )
    st.session_state.meal2 = st.radio(
        label="食事を取る際、栄養バランスを考えていますか？", 
        options=["5：考えている", "4：少し考えている", "3：どちらとも言えない", "2：あまり考えていない", "1：考えていない"], 
        index=2
        )
    # 提出ボタン
    if st.button("提出"):
        st.session_state.page_control = 1
        st.rerun()

# トピック表示の関数
def to_pd():
    st.session_state.topic = ""
    if int(st.session_state.meal1[0]) <= 3 and int(st.session_state.meal2[0]) <= 3:
        st.session_state.topic = "規則的で栄養バランスの取れた食事"
    elif int(st.session_state.meal1[0]) <= 3:
        st.session_state.topic = "規則的な食事"
    elif int(st.session_state.meal2[0]) <= 3:
        st.session_state.topic = "栄養バランスの取れた食事"
    if st.session_state.topic == "":
        st.write("今回は説得対話を行えるトピックがありません。")
        st.stop()
    else :
        st.write(
            f"あなたが説得を受けるトピックは{st.session_state.topic}です。"
        )
        st.write(
            "まずは、対話エージェントとの雑談を行います。"
        )
        st.write(
            "ボタンをクリックして対話エージェントとの対話を始めてください。"
        )
        st.write(
            "この対話では途中から説得エージェントが合流し、あなたと対話エージェントに対して説得を行います。"
        )   
        st.session_state.persuadeeprompt0 = st.session_state.persuadeeprompt0.replace("{user}", st.session_state.name)
        st.session_state.persuadeeprompt1 = st.session_state.persuadeeprompt1.replace("{topic}", st.session_state.topic).replace("{user}", st.session_state.name)
        st.session_state.persuadeeprompt2 = st.session_state.persuadeeprompt2.replace("{topic}", st.session_state.topic).replace("{user}", st.session_state.name)
        st.session_state.persuaderprompt = st.session_state.persuaderprompt.replace("{topic}", st.session_state.topic).replace("{user}", st.session_state.name)
        if st.button("対話エージェントとの対話を始める"):
            st.session_state.page_control = 2
            st.rerun()

# チャット画面の関数
def chat_system():
    # 被説得者のアイコンは右寄せにする
    st.markdown("""
        <style>
        [class*="st-key-user"] .stChatMessage {
            flex-direction: row-reverse;
            text-align: left;
        }
        [class*="st-key-assistant2"] .stChatMessage {
            flex-direction: row-reverse;
            text-align: left;
        }
        </style>
        """, unsafe_allow_html=True)
    st.title("説得対話用のチャットシステム")

    #対話エージェントとユーザのi_turnのアイスブレイク雑談対話
    if st.session_state.turn <= i_turn:
        # 以前のチャットログを表示
        for idx, chat in enumerate(st.session_state.chat_log):
            with st.container(key = f"{chat["name"]}_{idx}"):
                with st.chat_message(chat["name"], avatar=chat["avatar"]):
                    st.write(chat["msg"])
        # 対話エージェントの発話
        if st.session_state.chat_log == []:
            assistant2_msg = f"こんにちは！私は対話エージェントです。説得対話が始まる前に私と少し雑談をしましょう!"
            with st.container(key = f"{ASSISTANT_NAME2}_49"):
                with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
                    st.write(assistant2_msg)
            st.session_state.chat_log.append({"name": ASSISTANT_NAME2, "msg": assistant2_msg, "avatar": assistant2_icon})
            st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant2_msg + "\n" + "対話エージェント："
        if st.session_state.is_chat_input_disabled:
            # 対話エージェントが雑談する発話を生成
            response = response_chatgpt(st.session_state.persuadeeprompt0 + st.session_state.prompt_chat_log)
            # 対話エージェントのメッセージをストリーミング表示
            with st.container(key = f"{ASSISTANT_NAME2}_50"):
                with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
                    assistant2_msg = ""
                    assistant2_response_area = st.empty()
                    for chunk in response:
                        if chunk.choices[0].finish_reason is not None:
                            break
                        assistant2_msg += chunk.choices[0].delta.content
                        assistant2_response_area.write(assistant2_msg)
            st.session_state.chat_log.append({"name": ASSISTANT_NAME2, "msg": assistant2_msg, "avatar": assistant2_icon})
            st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant2_msg + "\n" + f"{st.session_state.name}："
            st.session_state.is_chat_input_disabled = False
            st.rerun()
        #ユーザの入力
        if user_msg := st.chat_input(st.session_state.input_message, disabled=st.session_state.is_chat_input_disabled) or st.session_state.is_chat_input_disabled:
            if not st.session_state.is_chat_input_disabled:
                # ユーザの発話を表示
                with st.container(key = f"{USER_NAME}_50"):
                    with st.chat_message(USER_NAME, avatar=user_icon):
                        st.write(user_msg)
                st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg, "avatar": user_icon})
                st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + user_msg + "\n" + "対話エージェント："
                st.session_state.is_chat_input_disabled = True
                st.session_state.turn += 1
                st.rerun()
    else:
        # 以前のチャットログを表示
        for idx, chat in enumerate(st.session_state.chat_log):
            with st.container(key = f"{chat["name"]}_{idx}"):
                with st.chat_message(chat["name"], avatar=chat["avatar"]):
                    st.write(chat["msg"])
        # 最初の説得エージェントの発話
        if len(st.session_state.chat_log) == 11:
            response = response_chatgpt(st.session_state.persuadeeprompt0 + st.session_state.prompt_chat_log)
            # 対話エージェントの雑談終了の発話をストリーミング表示
            with st.container(key = f"{ASSISTANT_NAME2}_50"):
                with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
                    assistant2_msg = ""
                    assistant2_response_area = st.empty()
                    for chunk in response:
                        if chunk.choices[0].finish_reason is not None:
                            break
                        assistant2_msg += chunk.choices[0].delta.content
                        assistant2_response_area.write(assistant2_msg)
            st.session_state.chat_log.append({"name": ASSISTANT_NAME2, "msg": assistant2_msg, "avatar": assistant2_icon})
            st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant2_msg + "\n" + f"説得エージェント："
            # 最初の挨拶
            assistant_msg = f"こんにちは！お話の途中にすみませんが、今から{st.session_state.topic}の重要性についてお話をさせてもらおうと思います。"
            with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
                st.write(assistant_msg)
            st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg, "avatar": assistant_icon})
            st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant_msg + "\n" + "説得エージェント："
            # 最初の説得
            response = response_chatgpt(st.session_state.persuaderprompt + st.session_state.prompt_chat_log)
            with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
                assistant_msg = ""
                assistant_response_area = st.empty()
                for chunk in response:
                    if chunk.choices[0].finish_reason is not None:
                        break
                    assistant_msg += chunk.choices[0].delta.content
                    assistant_response_area.write(assistant_msg)
            st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg, "avatar": assistant_icon})
            st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant_msg + "\n" + "対話エージェント："
            st.chat_input("説得文を読んでください", disabled=True)
            st.session_state.is_chat_input_disabled = False
            time.sleep(len(assistant_msg) * 0.1 + 5)
            st.rerun()

        # 対話エージェントの発話
        if not st.session_state.is_chat_input_disabled and st.session_state.is_persuadee_speak:
            if st.session_state.turn <= i_turn + 2:
                # 対話エージェントが反論する発話を生成
                response = response_chatgpt(st.session_state.persuadeeprompt1 + st.session_state.prompt_chat_log)
            else:
                # 対話エージェントが説得される発話を生成
                response = response_chatgpt(st.session_state.persuadeeprompt2 + st.session_state.prompt_chat_log)
            # 対話エージェントのメッセージを表示
            with st.container(key = f"{ASSISTANT_NAME2}_50"):
                with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
                    assistant2_msg = ""
                    assistant2_response_area = st.empty()
                    for chunk in response:
                        if chunk.choices[0].finish_reason is not None:
                            break
                        assistant2_msg += chunk.choices[0].delta.content
                        assistant2_response_area.write(assistant2_msg)
            st.session_state.chat_log.append({"name": ASSISTANT_NAME2, "msg": assistant2_msg, "avatar": assistant2_icon})
            st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant2_msg + "\n" + f"{st.session_state.name}："
            st.session_state.is_persuadee_speak = False
            st.rerun()

        #ユーザの入力
        if user_msg := st.chat_input(st.session_state.input_message, disabled=st.session_state.is_chat_input_disabled) or st.session_state.is_chat_input_disabled:
            if not st.session_state.is_chat_input_disabled:
                # ユーザの発話を表示
                with st.container(key = f"{USER_NAME}_50"):
                    with st.chat_message(USER_NAME, avatar=user_icon):
                        st.write(user_msg)
                st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg, "avatar": user_icon})
                st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + user_msg + "\n" + "説得エージェント："
                st.session_state.is_chat_input_disabled = True
                st.session_state.input_message = "説得文を読んでください"
                st.session_state.is_persuadee_speak = True
                st.rerun()
            else:
                # 説得エージェントの発話を表示
                if st.session_state.turn >= i_turn+p_turn:
                    assistant_msg = f"今日の話が皆さんの日々の食生活改善に少しでも役立てば幸いです。今日はお話しできて本当に良かったです。ありがとうございました！"
                    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
                        st.write(assistant_msg)
                    st.write("規定のターンが経過したので、説得対話は終了しました。")
                    st.write("下のボタンをクリックして、発話評価に進んでください。")
                    if st.button("評価を開始"):
                        st.session_state.page_control = 3
                        st.rerun()
                else:
                    response = response_chatgpt(st.session_state.persuaderprompt + st.session_state.prompt_chat_log)
                    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
                        assistant_msg = ""
                        assistant_response_area = st.empty()
                        for chunk in response:
                            if chunk.choices[0].finish_reason is not None:
                                break
                            assistant_msg += chunk.choices[0].delta.content
                            assistant_response_area.write(assistant_msg)
                    st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg, "avatar": assistant_icon})
                    st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant_msg + "\n" + "対話エージェント："
                    st.session_state.turn += 1
                    st.session_state.is_chat_input_disabled = False
                    st.session_state.input_message = "ここにメッセージを入力"
                    time.sleep(len(assistant_msg) * 0.1 + 5)
                    st.rerun()

# 発話評価の関数
def utterance_eval():
    st.title("発話ごとの評価")
    st.write(
        "説得エージェントと対話エージェントとあなたのそれぞれの発話について、次の質問に答えてください。"
    )
    for chat in st.session_state.chat_log[1:13]:
        chat["persuasive"] = "0"
        if chat["name"] != USER_NAME:
            chat["natural"] = "0"
    for i, chat in enumerate(st.session_state.chat_log[13:], 1):
        if chat["name"] == ASSISTANT_NAME:
            st.write(f"説得エージェントの発話{i}")
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"説得エージェントの発話{i}は説得力がある", ["5：同意できる（説得力がある）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（説得力がない）"], index=2)
            chat["natural"] = st.radio(f"説得エージェントの発話{i}は応答として自然である", ["5：同意できる（自然である）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（不自然である）"], index=2)
        elif chat["name"] == ASSISTANT_NAME2:
            st.write(f"対話エージェントの発話{i}")
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"あなたから見て、対話エージェントは発話{i}を行った時点で説得を受け入れていた", ["5：同意できる（その時点で説得を受け入れ、生活習慣を改善しようと考えている）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（その時点では説得を受け入れておらず、生活習慣を改善しようとは考えていない）"], index=2)
            chat["natural"] = st.radio(f"対話エージェントの発話{i}は応答として自然である", ["5：同意できる（自然である）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（不自然である）"], index=2)
        else:
            st.write(f"あなたの発話{i}")
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"あなたは発話{i}を行った時点で説得を受け入れていた", ["5：同意できる（その時点で説得を受け入れ、生活習慣を改善しようと考えている）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（その時点では説得を受け入れておらず、生活習慣を改善しようとは考えていない）"], index=2)
    #最終確認
    st.markdown("""
    ## :red[上にスクロールして、全てのアンケートに答えているかを確認してからボタンを押してください]
    """)
    if st.button("対話全体の評価に進む"):
        st.session_state.page_control = 4
        st.rerun()

# 対話全体の評価
def dialogue_eval():
    st.title("対話全体の評価")
    st.write(
        "今回の対話全体を考慮して説得エージェントについて、次の質問に答えてください。"
    )
    # 説得力
    persuasive = st.radio("この説得エージェントは説得力がある", ["5：同意できる（説得力がある）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（説得力がない）"], index=2)
    # 自然さ
    natural = st.radio("この説得エージェントの応答は自然である", ["5：同意できる（自然である）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（不自然である）"], index=2)
    # 具体的な説得力の評価
    meal1_eval = st.radio(
        label="今後どれくらいの頻度で1日に3食食べたいたいと思いますか？", 
        options=["5：毎日", "4：週に3〜4回程度", "3：週に1〜2回程度", "2：月に1〜2回程度", "1：ほとんどの日に3食食べない"], 
        index=2
        )
    meal2_eval = st.radio(
        label="今後食事を取る際、栄養バランスを考えたいと思いますか？", 
        options=["5：思う", "4：少し思う", "3：どちらとも言えない", "2：あまり思わない", "1：思わない"], 
        index=2
        )
    txt = st.text_area(
        label="エージェントと対話をして気づいたことや感想を自由に記述してください。", height=150, max_chars=200
    )
    #最終確認
    st.markdown("""
    ## :red[上にスクロールして、全てのアンケートに答えているかを確認してからボタンを押してください]
    """)
    # 終了ボタン
    if st.button("評価を終了"):
        st.session_state.dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).isoformat()
        data = {
            "date": st.session_state.dt_now,
            "gender": st.session_state.gender,
            "age": st.session_state.age,
            "topic": st.session_state.topic,
            "pre_survey": {
                "frequency": int(st.session_state.meal1[0]),
                "balance": int(st.session_state.meal2[0]),
            },
            "post_survey": {
                "frequency": int(meal1_eval[0]),
                "balance": int(meal2_eval[0]),
            },
            "all_persuasive": int(persuasive[0]),
            "all_natural": int(natural[0]),
            "free_writing": txt
        }
        dialogue = []
        for chat in st.session_state.chat_log[1:]:
            chat_entry = {
                "speaker": chat["name"],
                "message": chat["msg"],
                "persuasive": int(chat["persuasive"][0])
            }
            if chat["name"] != USER_NAME:
                chat_entry["natural"] = int(chat["natural"][0])
            dialogue.append(chat_entry)
        data["dialogue"] = dialogue
        # 保存
        with open(f"data/{st.session_state.dt_now}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.session_state.page_control = 5
        st.rerun()

def finish():
    st.title("評価が完了しました。")
    st.write("ありがとうございました。")
    with open(f"data/{st.session_state.dt_now}.json", "rb") as file:
        st.download_button(
            label="出力ファイルのダウンロード", 
            data=file,
            file_name=f"{st.session_state.dt_now}.json",
        )

#ページの管理
if st.session_state.page_control == 0:
    pre_survey()
elif st.session_state.page_control == 1:
    to_pd()
elif st.session_state.page_control == 2:
    chat_system()
elif st.session_state.page_control == 3:
    utterance_eval()
elif st.session_state.page_control == 4:
    dialogue_eval()
elif st.session_state.page_control == 5:
    finish()