import os
import streamlit as st
import feedparser, requests, time, base64
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# --- 1. ページ設定 & デザイン ---
st.set_page_config(page_title="HK & JP TAX INSIGHTS", layout="wide")

# カスタムCSS (Colab版の見た目を継承)
st.markdown("""
<style>
    .main { background-color: #000; color: #fff; }
    .stButton>button { width: 100%; border-radius: 0; background-color: transparent; color: #444; border: 1px solid #222; }
    .stButton>button:hover { color: #ff3b30; border-color: #ff3b30; }
    .report-card { border-left: 5px solid #fff; background-color: #0a0a0a; padding: 20px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. 監視設定 ---
KEYWORDS = ["tax", "ird", "accounting", "audit", "crypto", "blockchain", "web3", "移転価格", "租税条約", "国際課税"]
SOURCES = [
    {"name": "IRD (HK Tax)", "url": "https://www.ird.gov.hk/eng/new/index.data.xml", "type": "label-hk"},
    {"name": "国税庁 (NTA Japan)", "url": "https://www.nta.go.jp/whatsnew/rss/whatsnew.xml", "type": "label-jp"},
    {"name": "PwC HK", "url": "https://www.pwchk.com/en/rss/tax.xml", "type": "label-hk"}
]

# --- 3. ニュース取得ロジック (キャッシュを使用して高速化) ---
@st.cache_data(ttl=3600)  # 1時間に1回だけ取得
def fetch_news():
    news_list = []
    translator = GoogleTranslator(source='auto', target='ja')
    for src in SOURCES:
        feed = feedparser.parse(src['url'])
        for entry in feed.entries[:10]:
            content = (entry.title + " " + (entry.summary if 'summary' in entry else "")).lower()
            if any(kw in content for kw in KEYWORDS):
                # 翻訳処理
                title_ja = entry.title if src['type'] == 'label-jp' else translator.translate(entry.title)
                news_list.append({
                    "id": entry.link,
                    "src_name": src['name'],
                    "type": src['type'],
                    "title": title_ja,
                    "link": entry.link,
                    "date": entry.get('published', 'RECENT')[:16]
                })
    return news_list

# --- 4. メイン画面 ---
# ロゴとタイトルの表示
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1 style='letter-spacing:5px;'>HK & JP TAX INSIGHTS</h1>", unsafe_allow_html=True)
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)

# ニュースの表示管理 (削除機能)
if 'news_data' not in st.session_state:
    st.session_state.news_data = fetch_news()

for idx, item in enumerate(st.session_state.news_data):
    with st.container():
        # Streamlit独自の「削除ボタン」
        c_title, c_del = st.columns([9, 1])
        with c_title:
            color = "#007aff" if item['type'] == 'label-hk' else "#ff3b30"
            st.markdown(f"<span style='color:{color}; font-weight:bold; border:1px solid {color}; padding:2px 5px; font-size:10px;'>{item['src_name']}</span>", unsafe_allow_html=True)
            st.markdown(f"### {item['title']}")
            st.write(f"📅 {item['date']}")
            st.markdown(f"[VIEW REPORT →]({item['link']})")
        with c_del:
            if st.button("×", key=f"del_{idx}"):
                st.session_state.news_data.pop(idx)
                st.rerun()
        st.markdown("---")
