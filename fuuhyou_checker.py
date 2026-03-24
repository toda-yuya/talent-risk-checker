import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta

# --- 1. ページ設定（アシロ社をイメージしたリーガルテック風） ---
st.set_page_config(page_title="アシロ版・風評チェッカー", page_icon="⚖️", layout="wide")

# カスタムCSSでデザインを調整
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #004a99; color: white; border-radius: 5px; width: 100%; }
    .report-box { padding: 20px; border-radius: 10px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .status-a { color: #28a745; font-weight: bold; }
    .status-d { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ネガティブワード辞書（30種類以上） ---
NEGATIVE_WORDS = {
    "炎上": 15, "最悪": 10, "ブラック": 12, "詐欺": 20, "逮捕": 25, 
    "不倫": 18, "枕": 15, "パワハラ": 15, "セクハラ": 15, "嫌い": 8,
    "事件": 20, "不祥事": 20, "怪しい": 10, "ゴミ": 10, "無能": 10,
    "倒産": 20, "裁判": 15, "訴訟": 15, "被害": 12, "隠蔽": 18,
    "反社": 25, "嘘": 10, "パクリ": 10, "低評価": 8, "対応悪い": 10,
    "ステマ": 12, "流出": 18, "謝罪": 10, "危険": 15, "不潔": 10,
    "辞めたい": 10, "パワハラ会議": 15, "偽装": 18, "捏造": 18
}

# --- 3. 診断ロジック（デモ用シミュレーター） ---
def simulate_search(keyword):
    # 本来はここでGoogle Custom Search API等を叩く
    # デモ用にキーワードに応じたランダムな結果を生成
    results = []
    found_negatives = []
    total_score = 0
    
    # シミュレーション用の検索結果（直近24時間分を想定）
    for i in range(10):
        # キーワードによってリスクを変える（デモ用）
        if "AnyColor" in keyword or "炎上" in keyword:
            is_neg = random.random() < 0.4
        else:
            is_neg = random.random() < 0.1
            
        if is_neg:
            word = random.choice(list(NEGATIVE_WORDS.keys()))
            title = f"【悲報】{keyword}、ネットで「{word}」と話題に..."
            snippet = f"直近24時間の投稿をまとめると、{keyword}に関する{word}疑惑が浮上しており..."
            score = NEGATIVE_WORDS[word]
            found_negatives.append(word)
            total_score += score
        else:
            title = f"{keyword}の最新活動レポート - 公式ニュース"
            snippet = f"{keyword}の今後の展開について、ポジティブな意見が集まっています。"
            
        results.append({"title": title, "snippet": snippet, "is_neg": is_neg})
    
    # ランク判定
    if total_score == 0: rank, color = "A", "safe"
    elif total_score < 20: rank, color = "B", "warning"
    elif total_score < 50: rank, color = "C", "alert"
    else: rank, color = "D", "danger"
    
    return results, rank, total_score, list(set(found_negatives))

# --- 4. 画面レイアウト ---
st.title("⚖️ 風評被害・即時診断ツール (Prototye)")
st.write("直近24時間のネット上の書き込みをスキャンし、法的リスクをスコアリングします。")

# 検索窓
col1, col2 = st.columns([4, 1])
with col1:
    target_kw = st.text_input("調査したいキーワードを入力してください（タレント名、会社名など）", placeholder="例：株式会社アシロ")
with col2:
    st.write(" ") # 余白
    search_btn = st.button("診断開始")

if search_btn or target_kw:
    with st.spinner('AIが直近24時間のデータを解析中...'):
        time.sleep(1.5) # 演出
        results, rank, score, neg_list = simulate_search(target_kw)

    # 診断結果ヘッダー
    st.subheader(f"「{target_kw}」の診断結果")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("リスクランク", f"ランク {rank}")
    with c2:
        st.metric("リスクスコア", f"{score} pt")
    with c3:
        st.metric("検知ワード数", f"{len(neg_list)} 件")

    # プログレスバー（ゲージ代わり）
    st.progress(min(score, 100) / 100)

    # 詳細タブ
    tab1, tab2 = st.tabs(["🔍 検出されたリスク詳細", "📄 全検索結果一覧"])
    
    with tab1:
        if neg_list:
            st.warning(f"以下のネガティブワードが検出されました： {', '.join(neg_list)}")
            st.write("これらは将来的に**発信者情報開示請求**や**削除請求**の対象となる可能性があります。")
        else:
            st.success("直近24時間以内に顕著なリスクは検出されませんでした。")

    with tab2:
        for res in results:
            if res["is_neg"]:
                st.error(f"**{res['title']}**\n\n{res['snippet']}")
            else:
                st.info(f"**{res['title']}**\n\n{res['snippet']}")

    # --- 5. 弁護士相談CTAバナー ---
    st.markdown("---")
    st.markdown(f"""
        <div style="background-color: #eef4ff; padding: 30px; border-radius: 10px; text-align: center; border: 2px solid #004a99;">
            <h3 style="color: #004a99;">法的措置をご検討ですか？</h3>
            <p>検知された「{', '.join(neg_list[:3])}...」等の書き込みは、弁護士を通じて削除や特定ができる可能性があります。</p>
            <a href="https://benchmark.legal/" target="_blank">
                <button style="background-color: #004a99; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 18px;">
                    ベンナビで専門弁護士を探す（無料相談可能）
                </button>
            </a>
        </div>
    """, unsafe_allow_html=True)

else:
    # 初期画面のガイド
    st.info("検索窓にキーワードを入力して「診断開始」を押してください。")