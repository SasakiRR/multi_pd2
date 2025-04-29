import os
import time
import pytz
import json
import random
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
if "exercise" not in st.session_state:
    st.session_state.exercise = ""
if "sleep" not in st.session_state:
    st.session_state.sleep = ""
if "cleaning" not in st.session_state:
    st.session_state.cleaning = ""

# 表示用チャットログの初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# プロンプトの初期化
if "persuaderprompt" not in st.session_state:
    with open(PERSUADER_PROMPTFILE, "r") as f:
        st.session_state.persuaderprompt = f.read()
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

# 説得度評価の練習用ページの関数
def practice():
    st.title("説得度評価の練習")
    st.markdown(
        "ピンクのアイコンの対話エージェントが説得されているかの基準を明確化するため、評価の練習を行います。  \n次の基準を確認して、10個の質問に答えてください。"
    )
    st.markdown(
        "**5：「完全に同意」エージェントが説得内容を受け入れた意思を表明している**"
    )
    st.markdown(
        "**4：「やや同意」内容にはある程度納得し、改善の意志は見えるがやや曖昧な表現が使われている**"
    )
    st.markdown(
        "**3：「中立」情報に対して興味や理解は示すが、明確な同意も否定もしないか、態度が不明確**"
    )
    st.markdown(
        "**2：「やや不同意」内容に対して否定的な反応が見られ、改善する意思が弱いか、一部は理解するが、実行の意思はない**"
    )
    st.markdown(
        "**1：「完全に不同意」内容に明確に反対するか、改善する意志を完全に拒否**"
    )
    answer = ["" for i in range(10)]
    score = 0
    st.write(
        "**練習問題1**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "歩くことは誰でもできる運動で、たとえ10分だけでも血糖値のコントロールや脳の活性化に良い影響があるとされています。まずは通勤中に一駅分歩いてみるのはどうでしょう？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "うーん、一駅分歩くのは面倒だし、朝はギリギリでバタバタしてるからちょっと出来そうにないですね。"
            )
    answer[0] = st.radio(
        "練習問題1において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#1
    if int(answer[0][0]) < 3: score += 1
    st.write(
        "**練習問題2**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "仕事が忙しくて運動する時間が取れない方も多いですが、実は階段を使うなどのちょっとした工夫で、1日の活動量はぐっと増えます。今の生活に無理なく取り入れられる工夫から始めてみませんか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "確かにエレベーター使うのが当たり前になってましたけど、階段ならすぐ試せそうです。明日から意識してみます。"
            )
    answer[1] = st.radio(
        "練習問題2において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#5
    if int(answer[1][0]) > 3: score += 1
    st.write(
        "**練習問題3**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "動画を見ながらの運動なら、自分のペースで無理なくできるので忙しい方にもぴったりです。1本5分のものもありますよ。"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "運動のために動画を見るのは面倒に感じるうえに、動画サイトを見てると運動しようって気持ちにならない気がします。"
            )
    answer[2] = st.radio(
        "練習問題3において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#1
    if int(answer[2][0]) < 3: score += 1
    st.write(
        "**練習問題4**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "1日10分の軽い体操でも肩こりや気分のリフレッシュに効果があると言われています。習慣化すれば自然と気分も整ってくるので、まずは朝の準備前など、生活に取り入れてみませんか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "なるほど、朝の準備前なら無理なくできそうですね。まずはストレッチだけでも毎日やってみようと思います。"
            )
    answer[3] = st.radio(
        "練習問題4において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#5
    if int(answer[3][0]) > 3: score += 1
    st.write(
        "**練習問題5**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "無理なく続けるのが大事なので、まずは“ながら運動”からで大丈夫ですよ。"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "それなら歯磨き中のスクワットとかから始めてみようかな。続けられそうですし。"
            )
    answer[4] = st.radio(
        "練習問題5において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#5
    if int(answer[4][0]) > 3: score += 1
    st.write(
        "**練習問題6**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "少しの工夫で生活に運動を取り入れることは可能ですし、健康への効果も積み重なっていきます。今の自分の体を守るためにも、一緒に考えてみませんか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "健康のことは分かってるつもりなんですけど、運動ってやっぱり嫌いなのでやる気になれないです。"
            )
    answer[5] = st.radio(
        "練習問題6において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#1
    if int(answer[5][0]) < 3: score += 1
    st.write(
        "**練習問題7**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "疲れていると運動するのも面倒に感じますが、逆に軽い運動をすることでストレスが軽減されて、結果的に気分がスッキリするという研究もあります。気分転換のつもりで5分だけ体を動かしてみませんか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "確かに気分転換は必要と思ってたので、5分くらいならやってみようかな。最近は座りっぱなしでいることが多くて疲れが溜まってたので。"
            )
    answer[6] = st.radio(
        "練習問題7において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#5
    if int(answer[6][0]) > 3: score += 1
    st.write(
        "**練習問題8**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "たとえば1日5分のラジオ体操でも、筋肉がほぐれて血流が良くなると言われています。特に運動不足が気になっている方には効果的なので、まずは試してみてはいかがでしょうか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "正直1日に5分程度で自覚できるほど変わると思えないし、やる気も出ないです。"
            )
    answer[7] = st.radio(
        "練習問題8において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#1
    if int(answer[7][0]) < 3: score += 1
    st.write(
        "**練習問題9**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "運動が苦手でも、ストレッチやヨガのようにリラックスしながらできるものから始めれば、心身ともに整いますよ。"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "ヨガとか、素人の知識でやっても効果がでなそうな気がするし、運動でリラックスできるとはあまり思えません。"
            )
    answer[8] = st.radio(
        "練習問題9において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#1
    if int(answer[8][0]) < 3: score += 1
    st.write(
        "**練習問題10**"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "週に1回でも軽く体を動かす日を作るだけで、睡眠の質が上がったり、姿勢がよくなったりという効果があります。完璧じゃなくても、まずは“動く習慣”を意識してみるのが大切です。"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "そんなに変わるなら、ちょっとやってみたくなりました。とりあえず週末に散歩から始めてみます。"
            )
    answer[9] = st.radio(
        "練習問題10において対話エージェントは発話を行った時点で説得を受け入れていた",
        ["6：無回答", "5：同意できる", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない"],
        index=0)#5
    if int(answer[9][0]) > 3: score += 1
    # 提出ボタン
    if st.button("解答を完了"):
        for i in range(10):
            if int(answer[i][0]) == 6:
                st.write(":red[無回答の質問があります。全ての質問に答えてください。]")
                st.stop()
        if score > 6:
            st.session_state.page_control = 1
            st.rerun()
        else:
            st.write(":red[正解数が基準に達していません。もう一度評価基準を確認して質問に回答してください。]")

# 説得度評価の解答用ページの関数
def answer():
    st.title("説得度評価の練習")
    st.markdown(
        "正解率が基準に達したため、解答と解説を確認してから先に進んでください"
    )
    st.write(
        "練習問題1"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "歩くことは誰でもできる運動で、たとえ10分だけでも血糖値のコントロールや脳の活性化に良い影響があるとされています。まずは通勤中に一駅分歩いてみるのはどうでしょう？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "うーん、一駅分歩くのは面倒だし、朝はギリギリでバタバタしてるからちょっと出来そうにないですね。"
            )
    st.write(
        "**現実的な障害を理由に提案を完全に拒否しており、説得の効果は見られないため、説得されていない**"
        )
    st.write(
        "練習問題2"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "仕事が忙しくて運動する時間が取れない方も多いですが、実は階段を使うなどのちょっとした工夫で、1日の活動量はぐっと増えます。今の生活に無理なく取り入れられる工夫から始めてみませんか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "確かにエレベーター使うのが当たり前になってましたけど、階段ならすぐ試せそうです。明日から意識してみます。"
            )
    st.write(
        "**提案された方法に納得し、具体的に「明日から」と言っていることから、受け入れの度合いが高いため、説得されている**"
        )
    st.write(
        "練習問題3"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "動画を見ながらの運動なら、自分のペースで無理なくできるので忙しい方にもぴったりです。1本5分のものもありますよ。"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "運動のために動画を見るのは面倒に感じるうえに、動画サイトを見てると運動しようって気持ちにならない気がします。"
            )
    st.write(
        "**行動の第一歩に対しても拒否的で、説得内容に対する前向きな兆しが見えないため、説得されていない**"
        )
    st.write(
        "練習問題4"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "1日10分の軽い体操でも肩こりや気分のリフレッシュに効果があると言われています。習慣化すれば自然と気分も整ってくるので、まずは朝の準備前など、生活に取り入れてみませんか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "なるほど、朝の準備前なら無理なくできそうですね。まずはストレッチだけでも毎日やってみようと思います。"
            )
    st.write(
        "**相手の提案を受け入れ、自ら明日から始めると具体的に述べているため、説得されている**"
        )
    st.write(
        "練習問題5"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "無理なく続けるのが大事なので、まずは“ながら運動”からで大丈夫ですよ。"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "それなら歯磨き中のスクワットとかから始めてみようかな。続けられそうですし。"
            )
    st.write(
        "**“ながら運動”という提案を自分に合う形で取り入れようとしているため、説得されている**"
        )
    st.write(
        "練習問題6"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "少しの工夫で生活に運動を取り入れることは可能ですし、健康への効果も積み重なっていきます。今の自分の体を守るためにも、一緒に考えてみませんか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "健康のことは分かってるつもりなんですけど、運動ってやっぱり嫌いなのでやる気になれないです。"
            )
    st.write(
        "**健康の重要性は認識していても、運動への拒否感が強く、説得されていない**"
        )
    st.write(
        "練習問題7"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "疲れていると運動するのも面倒に感じますが、逆に軽い運動をすることでストレスが軽減されて、結果的に気分がスッキリするという研究もあります。気分転換のつもりで5分だけ体を動かしてみませんか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "確かに気分転換は必要と思ってたので、5分くらいならやってみようかな。最近は座りっぱなしでいることが多くて疲れが溜まってたので。"
            )
    st.write(
        "**説得の内容を肯定し、動機づけとして自身の状況とも結びつけているため、説得されている**"
        )
    st.write(
        "練習問題8"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "たとえば1日5分のラジオ体操でも、筋肉がほぐれて血流が良くなると言われています。特に運動不足が気になっている方には効果的なので、まずは試してみてはいかがでしょうか？"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "正直1日に5分程度で自覚できるほど変わると思えないし、やる気も出ないです。"
            )
    st.write(
        "**提案された方法の効果に懐疑的で、実行する気もまったく示していないため、説得されていない**"
        )
    st.write(
        "練習問題9"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "運動が苦手でも、ストレッチやヨガのようにリラックスしながらできるものから始めれば、心身ともに整いますよ。"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "ヨガとか、素人の知識でやっても効果がでなそうな気がするし、運動でリラックスできるとはあまり思えません。"
            )
    st.write(
        "**やる行為そのものを否定しており、その効果についても懐疑的であるため、説得されていない**"
        )
    st.write(
        "練習問題10"
        )
    with st.chat_message(ASSISTANT_NAME, avatar=assistant_icon):
        st.write(
            "週に1回でも軽く体を動かす日を作るだけで、睡眠の質が上がったり、姿勢がよくなったりという効果があります。完璧じゃなくても、まずは“動く習慣”を意識してみるのが大切です。"
            )
    with st.chat_message(ASSISTANT_NAME2, avatar=assistant2_icon):
        st.write(
            "そんなに変わるなら、ちょっとやってみたくなりました。とりあえず週末に散歩から始めてみます。"
            )
    st.write(
        "**運動の効果に興味を持ち、自発的に「週末に散歩」と具体的なアクションを宣言しているため、説得されている**"
        )
    st.markdown("## :red[全ての解答を確認したらボタンを押してください]")
    if st.button("確認完了"):
        st.session_state.page_control = 2
        st.rerun()

# 事前アンケートの関数
def pre_survey():
    st.title("事前アンケート")
    st.write(
        "以下のアンケート全てに答えてください。（無回答が存在すると先に進めません）"
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
        options=["6：無回答", "5：毎日", "4：週3〜4日程度", "3：週1〜2日程度", "2：月1〜2日程度", "1：ほとんどの日に3食食べない"], 
        index=0
        )
    st.session_state.meal2 = st.radio(
        label="食事を取る際、栄養バランスを考えていますか？", 
        options=["6：無回答", "5：考えている", "4：少し考えている", "3：どちらとも言えない", "2：あまり考えていない", "1：考えていない"], 
        index=0
        )
    st.session_state.exercise = st.radio(
        label="1週間に何日くらい、20分以上の運動をしていますか？", 
        options=["6：無回答", "5：毎日", "4：週3〜4日程度", "3：週1〜2日程度", "2：月に2〜3日程度", "1：ほとんどしていない"], 
        index=0
        )
    st.session_state.sleep = st.radio(
        label="1日の平均睡眠時間はどのくらいですか？", 
        options=["6：無回答", "5：7時間以上", "4：6〜7時間", "3：5〜6時間", "2：4〜5時間", "1：4時間未満"], 
        index=0
        )
    st.session_state.cleaning = st.radio(
        label="普段部屋の掃除をどれくらいの頻度で行っていますか？（掃除とは整理整頓、ホコリ取りなどを含みます）", 
        options=["6：無回答", "5：ほぼ毎日", "4：週に2〜3回", "3：週に1回程度", "2：月に2〜3回程度", "1：月に1回以下"], 
        index=0
        )
    #最終確認
    st.markdown("## :red[上にスクロールして、全てのアンケートに答えているかを確認してからボタンを押してください]")
    # 提出ボタン
    if st.button("提出"):
        if int(st.session_state.meal1[0]) == 6 or int(st.session_state.meal2[0]) == 6 or int(st.session_state.exercise[0]) == 6 or int(st.session_state.sleep[0]) == 6 or int(st.session_state.cleaning[0]) == 6:
            st.write(":red[無回答の質問があります。全ての質問に答えてください。]")
            st.stop()
        st.session_state.page_control = 3
        st.rerun()

# トピック表示の関数
def to_pd():
    st.session_state.topic = ""
    if int(st.session_state.meal1[0]) <= 3 and int(st.session_state.meal2[0]) <= 2:
        st.session_state.topic = "規則的で栄養バランスの取れた食事"
    elif int(st.session_state.meal1[0]) <= 3:
        st.session_state.topic = "規則的な食事"
    elif int(st.session_state.meal2[0]) <= 2:
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
        z_topic_list = [int(st.session_state.exercise[0]), int(st.session_state.sleep[0]), int(st.session_state.cleaning[0])]
        min_val = min(z_topic_list)
        min_indices = [i for i, v in enumerate(z_topic_list) if v == min_val]
        chosen_index = random.choice(min_indices)
        if chosen_index == 0:
            ztopic = "　- 運動・体を動かす習慣（散歩、ストレッチ、軽い運動など）\n　- 最近やってみた運動や体を動かす機会"
        elif chosen_index == 1:
            ztopic = "　- 睡眠習慣について（睡眠時間、質、寝る時間など）\n　- 最近の睡眠リズムの変化（寝不足、よく眠れた など）"
        elif chosen_index == 2:
            ztopic = "　- ちょっとした片付けの習慣（ホコリ取り、整理整頓など）\n　- 掃除のタイミングや気分（スッキリした、面倒くさい など）"
        if st.session_state.name == "":
            st.session_state.name = "ユーザ"
        st.session_state.persuadeeprompt0 = st.session_state.persuadeeprompt0.replace("{user}", st.session_state.name).replace("{ztopic}", ztopic)
        st.session_state.persuadeeprompt1 = st.session_state.persuadeeprompt1.replace("{topic}", st.session_state.topic).replace("{user}", st.session_state.name)
        st.session_state.persuadeeprompt2 = st.session_state.persuadeeprompt2.replace("{topic}", st.session_state.topic).replace("{user}", st.session_state.name)
        st.session_state.persuaderprompt = st.session_state.persuaderprompt.replace("{topic}", st.session_state.topic).replace("{user}", st.session_state.name)
        if st.button("対話エージェントとの対話を始める"):
            st.session_state.page_control = 4
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
            assistant2_msg = f"こんにちは！私はAIのユウです。説得対話が始まる前に私と少し雑談をしましょう!"
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
            time.sleep(len(assistant_msg) * 0.1 + 2)
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
                        st.session_state.page_control = 5
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
                    time.sleep(len(assistant_msg) * 0.1 + 2)
                    st.rerun()

# 発話評価の関数
def utterance_eval():
    st.title("発話ごとの評価")
    st.write(
        "説得エージェントと対話エージェントとあなたのそれぞれの発話について、次の質問に答えてください。（無回答が存在すると先に進めません）"
    )
    st.write(
        "説得されているかどうかの評価は次の基準を参考にしてください。"
    )
    st.markdown(
        "**5：「完全に同意」エージェントが説得内容を受け入れた意思を表明している**"
    )
    st.markdown(
        "**4：「やや同意」内容にはある程度納得し、改善の意志は見えるがやや曖昧な表現が使われている**"
    )
    st.markdown(
        "**3：「中立」情報に対して興味や理解は示すが、明確な同意も否定もしないか、態度が不明確**"
    )
    st.markdown(
        "**2：「やや不同意」内容に対して否定的な反応が見られ、改善する意思が弱いか、一部は理解するが、実行の意思はない**"
    )
    st.markdown(
        "**1：「完全に不同意」内容に明確に反対するか、改善する意志を完全に拒否**"
    )
    for chat in st.session_state.chat_log[1:13]:
        chat["persuasive"] = "0"
        if chat["name"] != USER_NAME:
            chat["natural"] = "0"
    for i, chat in enumerate(st.session_state.chat_log[13:], 1):
        if chat["name"] == ASSISTANT_NAME:
            st.write(f"説得エージェントの発話{i}")
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"説得エージェントの発話{i}は説得力がある", ["6：無回答", "5：同意できる（説得力がある）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（説得力がない）"], index=0)
            chat["natural"] = st.radio(f"説得エージェントの発話{i}は応答として自然である", ["6：無回答", "5：同意できる（自然である）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（不自然である）"], index=0)
        elif chat["name"] == ASSISTANT_NAME2:
            st.write(f"対話エージェントの発話{i}")
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"あなたから見て、対話エージェントは発話{i}を行った時点で説得を受け入れていた", ["6：無回答", "5：同意できる（その時点で説得を受け入れ、生活習慣を改善しようと考えている）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（その時点では説得を受け入れておらず、生活習慣を改善しようとは考えていない）"], index=0)
            chat["natural"] = st.radio(f"対話エージェントの発話{i}は応答として自然である", ["6：無回答", "5：同意できる（自然である）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（不自然である）"], index=0)
        else:
            st.write(f"あなたの発話{i}")
            st.write("「" + chat["msg"] + "」")
            chat["persuasive"] = st.radio(f"あなたは発話{i}を行った時点で説得を受け入れていた", ["6：無回答", "5：同意できる（その時点で説得を受け入れ、生活習慣を改善しようと考えている）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（その時点では説得を受け入れておらず、生活習慣を改善しようとは考えていない）"], index=0)
    #最終確認
    st.markdown("## :red[上にスクロールして、全てのアンケートに答えているかを確認してからボタンを押してください]")
    if st.button("対話全体の評価に進む"):
        for chat in st.session_state.chat_log[13:]:
            if int(chat["persuasive"][0]) == 6:
                st.write(":red[無回答の質問があります。全ての質問に答えてください。]")
                st.stop()
            elif chat["name"] != USER_NAME and int(chat["natural"][0]) == 6:
                st.write(":red[無回答の質問があります。全ての質問に答えてください。]")
                st.stop()
        st.session_state.page_control = 6
        st.rerun()

# 対話全体の評価
def dialogue_eval():
    st.title("対話全体の評価")
    st.write(
        "今回の対話全体を考慮して説得エージェントについて、次の質問に答えてください。（無回答が存在すると先に進めません）"
    )
    # 説得力
    persuasive = st.radio(
        label="この説得エージェントは説得力がある", 
        options=["6：無回答", "5：同意できる（説得力がある）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（説得力がない）"], 
        index=0
        )
    # 自然さ
    natural = st.radio(
        label="この説得エージェントの応答は自然である", 
        options=["6：無回答", "5：同意できる（自然である）", "4：やや同意できる", "3：どちらでもない", "2：やや同意できない", "1：同意できない（不自然である）"], 
        index=0
        )
    # 具体的な説得力の評価
    meal1_eval = st.radio(
        label="今後どれくらいの頻度で1日に3食食べたいたいと思いますか？", 
        options=["6：無回答", "5：毎日", "4：週に3〜4回程度", "3：週に1〜2回程度", "2：月に1〜2回程度", "1：ほとんどの日に3食食べない"], 
        index=0
        )
    meal2_eval = st.radio(
        label="今後食事を取る際、栄養バランスを考えたいと思いますか？", 
        options=["6：無回答", "5：思う", "4：少し思う", "3：どちらとも言えない", "2：あまり思わない", "1：思わない"], 
        index=0
        )
    txt = st.text_area(
        label="エージェントと対話をして気づいたことや感想を自由に記述してください。", height=150, max_chars=200
    )
    #最終確認
    st.markdown("## :red[上にスクロールして、全てのアンケートに答えているかを確認してからボタンを押してください]")
    # 終了ボタン
    if st.button("評価を終了"):
        if int(persuasive[0]) == 6 or int(natural[0]) == 6 or int(meal1_eval[0]) == 6 or int(meal2_eval[0]) == 6:
            st.write(":red[無回答の質問があります。全ての質問に答えてください。]")
            st.stop()
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
        st.session_state.page_control = 7
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
    practice()
elif st.session_state.page_control == 1:
    answer()
elif st.session_state.page_control == 2:
    pre_survey()
elif st.session_state.page_control == 3:
    to_pd()
elif st.session_state.page_control == 4:
    chat_system()
elif st.session_state.page_control == 5:
    utterance_eval()
elif st.session_state.page_control == 6:
    dialogue_eval()
elif st.session_state.page_control == 7:
    finish()