import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# --- 1. ページ設定（プロトタイプ感を出しつつ洗練） ---
st.set_page_config(page_title="誹謗中傷リスク・可視化ツール", page_icon="⚖️", layout="wide")

# カスタムCSS（X風、5ch風のスタイル）
st.markdown("""
    <style>
    .report-box { padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #e1e8ed; margin-bottom: 10px; }
    .x-post { border: 1px solid #e1e8ed; padding: 15px; border-radius: 12px; background-color: #ffffff; }
    .x-user { font-weight: bold; color: #14171a; }
    .x-handle { color: #657786; font-size: 0.9em; }
    .ch5-post { background-color: #efefef; padding: 10px; border: 1px solid #ccc; font-family: "MS PGothic", "ＭＳ Ｐゴシック", sans-serif; font-size: 0.9em; line-height: 1.4; color: #000; }
    .ch5-header { color: #228b22; font-weight: bold; }
    .level-badge { padding: 2px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.8em; }
    .lv1 { background-color: #6c757d; } .lv2 { background-color: #ffc107; color: black; } 
    .lv3 { background-color: #fd7e14; } .lv4 { background-color: #dc3545; } .lv5 { background-color: #8b0000; }
    .amount-text { font-size: 1.2em; font-weight: bold; color: #d63384; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 慰謝料ロジック & ワードデータベース ---
RISK_LEVELS = {
    "Lv.1": {"name": "受忍限度内", "range": (0, 30000), "class": "lv1", "desc": "単発の侮辱"},
    "Lv.2": {"name": "名誉感情の侵害", "range": (50000, 150000), "class": "lv2", "desc": "執拗な侮辱"},
    "Lv.3": {"name": "プライバシー侵害", "range": (100000, 500000), "class": "lv3", "desc": "私事の暴露"},
    "Lv.4": {"name": "名誉毀損(個人)", "range": (200000, 500000), "class": "lv4", "desc": "事実の摘示"},
    "Lv.5": {"name": "名誉毀損(法人)", "range": (500000, 1000000), "class": "lv5", "desc": "業務妨害"}
}

KEYWORD_MAP = {
    "バカ": "Lv.1", "ブス": "Lv.1", "下手くそ": "Lv.1", "消えろ": "Lv.1",
    "死ね": "Lv.2", "キモい": "Lv.2", "ゴミ": "Lv.2", "社会の害悪": "Lv.2",
    "本名": "Lv.3", "住所": "Lv.3", "経歴": "Lv.3", "元カレ": "Lv.3",
    "不倫": "Lv.4", "詐欺師": "Lv.4", "前科": "Lv.4", "パクリ": "Lv.4",
    "食中毒": "Lv.5", "反社": "Lv.5", "隠蔽": "Lv.5", "粉飾": "Lv.5"
}

# --- 3. 診断シミュレーション ---
def get_simulated_posts(keyword):
    platforms = ["X (Twitter)", "5ちゃんねる"]
    posts = []
    total_estimated = 0
    
    for i in range(8):
        platform = random.choice(platforms)
        risk_word = random.choice(list(KEYWORD_MAP.keys()))
        level_key = KEYWORD_MAP[risk_word]
        level_info = RISK_LEVELS[level_key]
        
        amount = random.randint(level_info["range"][0], level_info["range"][1])
        total_estimated += amount
        
        if platform == "X (Twitter)":
            content = f"さっきの{keyword}の配信見たけど、本当に{risk_word}だわ。これ許されるの？ #炎上 #拡散希望"
            html = f"""
            <div class="x-post">
                <span class="x-user">匿名ユーザー @user_{random.randint(100,999)}</span> <span class="x-handle">・ 2h</span><br>
                {content}<br><br>
                <span class="level-badge {level_info['class']}">{level_key}: {level_info['name']}</span>
                <span style="margin-left:10px;">想定慰謝料: <span class="amount-text">{amount:,}円</span></span>
            </div><br>
            """
        else:
            id_str = f"{random.choice('abcdefg')}{random.randint(1000,9999)}"
            html = f"""
            <div class="ch5-post">
                <span class="ch5-header">{i+1} 名前：名無しさん＠お腹いっぱい。 [sage] 投稿日：2026/03/24(火) 14:02:15.82 ID:{id_str}</span><br><br>
                {keyword}について語るスレ<br>
                >>{i} {risk_word}すぎて草。はやく引退しろよ。<br><br>
                <span class="level-badge {level_info['class']}">{level_key}: {level_info['name']}</span>
                <span style="margin-left:10px;">想定慰謝料: <span class="amount-text">{amount:,}円</span></span>
            </div><br>
            """
        posts.append(html)
    
    return posts, total_estimated

# --- 4. 画面レイアウト ---
st.title("⚖️ 誹謗中傷リスク・可視化プロトタイプ")
st.caption("※本ツールは個人による技術検証用プロトタイプです。実際の検索結果とは異なります。")

target_kw = st.text_input("調査キーワード（タレント名・事務所名など）", placeholder="例：AnyColor")

if st.button("リスク診断を開始"):
    if target_kw:
        with st.spinner('各プラットフォームからデータを解析中...'):
            time.sleep(1.5)
            results, total_amount = get_simulated_posts(target_kw)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("検知されたリスク件数", f"{len(results)} 件")
        col2.metric("想定合計回収金額", f"¥{total_amount:,}")
        col3.error("最優先アクション：開示請求準備")
        
        st.divider()
        
        tab1, tab2 = st.tabs(["📊 タイムライン分析", "📜 慰謝料算出ロジック"])
        
        with tab1:
            for p in results:
                st.markdown(p, unsafe_allow_html=True)
                
        with tab2:
            st.write("本プロトタイプで採用している慰謝料相場（判例に基づく想定）")
            st.table(pd.DataFrame([
                {"レベル": k, "内容": v["name"], "相場": f"{v['range'][0]:,}〜{v['range'][1]:,}円", "区分": v["desc"]}
                for k, v in RISK_LEVELS.items()
            ]))

        # --- 5. Yahoo! JAPAN への誘導ボタン（ここを修正！） ---
        st.markdown(f"""
            <div style="background-color: #f0f4f8; padding: 25px; border-radius: 10px; text-align: center; border: 2px solid #003399; margin-top: 30px;">
                <h3 style="color: #003399; margin-top:0;">このキーワードについてさらに調べますか？</h3>
                <p>検知された「名誉毀損」等のリスクについて、一般的な解決方法や事例を検索エンジンで確認できます。</p>
                <a href="https://www.yahoo.co.jp/" target="_blank" style="text-decoration: none;">
                    <button style="background-color: #003399; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em; font-weight: bold;">
                        Yahoo! JAPAN で誹謗中傷対策を調べる
                    </button>
                </a>
            </div>
            <p style="font-size: 0.8em; color: #666; text-align: center; margin-top: 10px;">
                ※本金額はシミュレーションであり、実際の賠償額を保証するものではありません。
            </p>
        """, unsafe_allow_html=True)
    else:
        st.warning("キーワードを入力してください。")
