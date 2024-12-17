import os
import time
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
PERSUADEE_PROMPTFILE1 = "prompts/persuadeeprompt1.txt"
PERSUADEE_PROMPTFILE2 = "prompts/persuadeeprompt2.txt"
p_turn = 5
wait_time = 15
dt_now = datetime.datetime.now()

# ページ遷移のフラグの初期化
if "page_control" not in st.session_state:
    st.session_state.page_control = 0

# トピックの初期化
if "topic" not in st.session_state:
    st.session_state.topic = ""

# 事前アンケートの初期化
if "exercise" not in st.session_state:
    st.session_state.exercise = 0
if "cleaning" not in st.session_state:
    st.session_state.cleaning = 0
if "meal" not in st.session_state:
    st.session_state.meal = 0
if "sleep" not in st.session_state:
    st.session_state.sleep = 0

# 対話全体の評価値の初期化
if "persuasive" not in st.session_state:
    st.session_state.persuasive = 0
if "natural" not in st.session_state:
    st.session_state.natural = 0

# 表示用チャットログの初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# 説得者プロンプトの初期化
if "persuaderprompt" not in st.session_state:
    with open(PERSUADER_PROMPTFILE, "r") as f:
        st.session_state.persuaderprompt = f.read()

# 被説得者プロンプトの初期化
if "persuadeeprompt1" not in st.session_state:
    with open(PERSUADEE_PROMPTFILE1, "r") as f:
        st.session_state.persuadeeprompt1 = f.read()
if "persuadeeprompt2" not in st.session_state:
    with open(PERSUADEE_PROMPTFILE2, "r") as f:
        st.session_state.persuadeeprompt2 = f.read()

# プロンプト用チャットログの初期化
if "prompt_chat_log" not in st.session_state:
    st.session_state.prompt_chat_log = "説得者："

# ターン数の初期化
if "turn" not in st.session_state:
    st.session_state.turn = 1

# ChatGPTによるレスポンス取得の関数
def response_chatgpt(prompt: str):
    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}],
        model="gpt-4o-mini",
        stream=True,
    )
    return response

# 事前アンケートの関数
def pre_survey():
    st.title("生活習慣に関するアンケート")
    st.write(
        "運動、掃除、食事、睡眠の4つの項目について、次の質問に答えてください。"
    )
    st.write(
        "日常生活において健康を意識して行っている"
    )
    st.write(
        "5：同意できる, 4：やや同意できる, 3：どちらでもない, 2：やや同意できない, 1：同意できない"
    )
    # 運動
    st.session_state.exercise = st.radio("運動", [5, 4, 3, 2, 1], index=2)
    # 掃除
    st.session_state.cleaning = st.radio("掃除", [5, 4, 3, 2, 1], index=2)
    # 食事
    st.session_state.meal = st.radio("食事", [5, 4, 3, 2, 1], index=2)
    # 睡眠
    st.session_state.sleep = st.radio("睡眠", [5, 4, 3, 2, 1], index=2)
    # 提出ボタン
    if st.button("提出"):
        st.session_state.page_control = 1
        st.rerun()

# トピック選択の関数
def deside_topic():
    st.title("説得対話のトピック選択")
    persuade_list = []
    if st.session_state.exercise <= 3:
        persuade_list.append("日常的な運動")
    if st.session_state.cleaning <= 3:
        persuade_list.append("部屋の掃除")
    if st.session_state.meal <= 3:
        persuade_list.append("健康的な食事")
    if st.session_state.sleep <= 3:
        persuade_list.append("十分な睡眠")
    if persuade_list == []:
        st.write("今回は説得対話を行えるトピックがありません。")
        st.stop()
    else :
        st.write("以下の中から、説得対話のトピックを選んでください。")
        st.session_state.topic = st.radio("トピック", persuade_list, index=0)
        # 決定ボタン
        if st.button("トピックを決定"):
            st.session_state.page_control = 2
            st.rerun()

# トピック表示の関数
def to_pd():
    st.write(
        f"あなたが選んだトピックは{st.session_state.topic}です。"
    )
    st.write(
        "ボタンをクリックして説得エージェントとの対話を始めてください。"
    )
    st.session_state.persuaderprompt = st.session_state.persuaderprompt.replace("{topic}", st.session_state.topic)
    if st.button("説得エージェントとの対話を始める"):
        st.session_state.page_control = 3
        st.rerun()

# チャット画面の関数
def chat_system():
    # 最初の説得者の発話
    if st.session_state.chat_log == []:
        st.title("説得対話用のチャットシステム")
        # 最初の挨拶
        assistant_msg = f"こんにちは！今日は{st.session_state.topic}の重要性についてお話をしたいと思います。"
        with st.chat_message(ASSISTANT_NAME):
            st.write(assistant_msg)
        st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})
        st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant_msg + "\n" + "説得者："

        # 最初の説得
        response = response_chatgpt(st.session_state.persuaderprompt + st.session_state.prompt_chat_log)
        with st.chat_message(ASSISTANT_NAME):
            assistant_msg = ""
            assistant_response_area = st.empty()
            for chunk in response:
                if chunk.choices[0].finish_reason is not None:
                    break
                # 回答を逐次表示
                assistant_msg += chunk.choices[0].delta.content
                assistant_response_area.write(assistant_msg)
        st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})
        st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant_msg + "\n" + "被説得者A："

        # 被説得エージェントのメッセージを表示
        response = response_chatgpt(st.session_state.persuadeeprompt1 + st.session_state.prompt_chat_log)
        with st.chat_message(ASSISTANT_NAME2):
            assistant2_msg = ""
            assistant_response_area = st.empty()
            for chunk in response:
                if chunk.choices[0].finish_reason is not None:
                    break
                # 回答を逐次表示
                assistant2_msg += chunk.choices[0].delta.content
                assistant_response_area.write(assistant2_msg)
        st.session_state.chat_log.append({"name": ASSISTANT_NAME2, "msg": assistant2_msg})
        st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant2_msg + "\n" + "被説得者B："

    # turnが6以上の場合は終了
    if st.session_state.turn > p_turn:
        st.title("説得対話用のチャットシステム")
        for chat in st.session_state.chat_log:
            with st.chat_message(chat["name"]):
                st.write(chat["msg"])
        st.write("5ターン経過したので、説得対話は終了しました。")
        st.write("下のボタンをクリックして、発話評価に進んでください。")
        if st.button("評価を開始"):
            st.session_state.page_control = 4
            st.rerun()
    else:
    #ユーザの入力
        if user_msg := st.chat_input("ここにメッセージを入力"):
            st.title("説得対話用のチャットシステム")
            # 以前のチャットログを表示
            for chat in st.session_state.chat_log:
                with st.chat_message(chat["name"]):
                    st.write(chat["msg"])

            # ユーザの発話を表示
            with st.chat_message(USER_NAME):
                st.write(user_msg)
            st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
            st.session_state.prompt_chat_log = st.session_state.prompt_chat_log+ user_msg + "\n" + "説得者："

            # 説得者の発話を表示
            if st.session_state.turn >= p_turn:
                response = response_chatgpt("# タスク説明\n説得者が日説得者を説得する対話を終了する発話を生成してください．\n\n# 注意事項\n「説得者：」に続く部分のみを出力して下さい．\n出力に「説得者：」を含めないで下さい．\nすべて日本語で出力して下さい．\n\n#対話履歴\n" + st.session_state.prompt_chat_log)
            else:
                response = response_chatgpt(st.session_state.persuaderprompt + st.session_state.prompt_chat_log)
            with st.chat_message(ASSISTANT_NAME):
                assistant_msg = ""
                assistant_response_area = st.empty()
                for chunk in response:
                    if chunk.choices[0].finish_reason is not None:
                        break
                    # 回答を逐次表示
                    assistant_msg += chunk.choices[0].delta.content
                    assistant_response_area.write(assistant_msg)
            st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})
            st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant_msg + "\n" + "被説得者A："

            if st.session_state.turn <= 1:
                # 被説得者が反論する発話を生成
                response = response_chatgpt(st.session_state.persuadeeprompt1 + st.session_state.prompt_chat_log)
            else:
                # 被説得者が説得される発話を生成
                response = response_chatgpt(st.session_state.persuadeeprompt2 + st.session_state.prompt_chat_log)
            if st.session_state.turn >= p_turn:
                st.write("5ターン経過したので、説得対話は終了しました。")
                st.write("下のボタンをクリックして、発話評価に進んでください。")
                if st.button("評価を開始"):
                    st.session_state.page_control = 4
                    st.rerun()
            else:
                # 被説得エージェントのメッセージを表示
                with st.chat_message(ASSISTANT_NAME2):
                    assistant2_msg = ""
                    assistant_response_area = st.empty()
                    for chunk in response:
                        if chunk.choices[0].finish_reason is not None:
                            break
                        # 回答を逐次表示
                        assistant2_msg += chunk.choices[0].delta.content
                        assistant_response_area.write(assistant2_msg)
                st.session_state.chat_log.append({"name": ASSISTANT_NAME2, "msg": assistant2_msg})
                st.session_state.prompt_chat_log = st.session_state.prompt_chat_log + assistant2_msg + "\n" + "被説得者B："
            st.session_state.turn += 1

# 発話評価の関数
def utterance_eval():
    st.title("発話ごとの評価")
    st.write(
        "説得エージェントとあなたのそれぞれの発話について、次の質問に答えてください。"
    )
    st.write(
        "説得エージェントの発話は「説得力」と「自然さ」がある"
    )
    st.write(
        "被説得エージェントの発話はあなたから見て説得を受け入れていて「自然さ」がある"
    )
    st.write(
        "あなたのの発話は説得を受け入れている"
    )
    st.write(
        "5：同意できる, 4：やや同意できる, 3：どちらでもない, 2：やや同意できない, 1：同意できない"
    )
    for i, chat in enumerate(st.session_state.chat_log[1:], 1):
        if chat["name"] == ASSISTANT_NAME:
            st.write(f"発話{i}")
            st.write("説得エージェントの発話")
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"発話{i}の説得力", [5, 4, 3, 2, 1], index=2)
            chat["natural"] = st.radio(f"発話{i}の自然さ", [5, 4, 3, 2, 1], index=2)
        elif chat["name"] == ASSISTANT_NAME2:
            st.write(f"発話{i}")
            st.write("被説得エージェントの発話")
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"発話{i}の説得受容度", [5, 4, 3, 2, 1], index=2)
            chat["natural"] = st.radio(f"発話{i}の自然さ", [5, 4, 3, 2, 1], index=2)
        elif chat["name"] == USER_NAME:
            st.write(f"発話{i}")
            st.write("あなたの発話" + chat["msg"])
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"発話{i}の説得受容度", [5, 4, 3, 2, 1], index=2)

    if st.button("対話全体の評価に進む"):
        st.session_state.page_control = 5
        st.rerun()

# 対話全体の評価
def dialogue_eval():
    st.title("対話全体の評価")
    st.write(
        "今回の対話全体を考慮して説得エージェントについて、次の質問に答えてください。"
    )
    st.write(
        "この説得エージェントは「説得力」と「自然さ」がある"
    )
    st.write(
        "5：同意できる, 4：やや同意できる, 3：どちらでもない, 2：やや同意できない, 1：同意できない"
    )
    # 説得力
    st.session_state.persuasive = st.radio("説得力", [5, 4, 3, 2, 1], index=2)
    # 自然さ
    st.session_state.natural = st.radio("自然さ", [5, 4, 3, 2, 1], index=2)
    # 終了ボタン
    if st.button("評価を終了"):
        st.stop()

#ページの管理
if st.session_state.page_control == 0:
    pre_survey()
elif st.session_state.page_control == 1:
    deside_topic()
elif st.session_state.page_control == 2:
    to_pd()
elif st.session_state.page_control == 3:
    chat_system()
elif st.session_state.page_control == 4:
    utterance_eval()
elif st.session_state.page_control == 5:
    dialogue_eval()