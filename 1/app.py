import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Scatter
from pyecharts import options as opts
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

def fetch_text(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # 检查请求是否成功
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        return text
    except Exception as e:
        st.error(f"无法抓取文章： {e}")
        return None

def process_text(text):
    if not text:
        return {}
    words = jieba.lcut(text)
    filtered_words = [word for word in words if len(word.strip()) > 1] # 过滤掉单字符词
    word_counts = Counter(filtered_words)
    return word_counts

def create_wordcloud(word_counts):
    wordcloud = (
        WordCloud()
        .add("", list(word_counts.items()), word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
    )
    return wordcloud.render_embed()

def create_bar_chart(top_words):
    fig, ax = plt.subplots()
    ax.bar(top_words.keys(), top_words.values())
    plt.xticks(rotation=90)
    plt.title("柱状图")
    plt.tight_layout()
    return fig

def create_line_chart(top_words):
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=list(top_words.keys()), y=list(top_words.values()))
    plt.xticks(rotation=90)
    plt.title("折线图")
    plt.tight_layout()
    return plt.gcf()

def create_pie_chart(top_words):
    fig = px.pie(names=top_words.keys(), values=top_words.values(), title="饼图")
    return fig.to_html(full_html=False)

def create_scatter_chart(top_words):
    scatter = (
        Scatter()
        .add_xaxis(list(range(len(top_words))))
        .add_yaxis("词频", list(top_words.values()))
        .set_global_opts(title_opts=opts.TitleOpts(title="散点图"))
    )
    return scatter.render_embed()

st.title('文章分析工具')

# 初始化变量
text = ""
word_counts = {}

# 侧边栏输入框
url = st.sidebar.text_input("请输入文章URL")
if url:
    text = fetch_text(url)
    if text:
        word_counts = process_text(text)
        st.write("文章已成功抓取并处理！")

# 只有当有文本被处理后才显示图表选项
if word_counts:
    # 侧边栏选择图表类型
    chart_type = st.sidebar.selectbox("选择图表类型", ["词云图", "柱状图", "折线图", "饼图", "散点图"])

    # 侧边栏过滤低频词
    min_freq = st.sidebar.slider("最低词频", min_value=1, max_value=max(word_counts.values()), value=5)
    filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_freq}
    top_words = dict(Counter(filtered_word_counts).most_common(20))

    # 根据图表类型选择的绘制图表
    if chart_type == "词云图":
        chart_html = create_wordcloud(top_words)
    elif chart_type == "柱状图":
        chart = create_bar_chart(top_words)
        st.pyplot(chart)
    elif chart_type == "折线图":
        chart = create_line_chart(top_words)
        st.pyplot(chart)
    elif chart_type == "饼图":
        chart_html = create_pie_chart(top_words)
    elif chart_type == "散点图":
        chart_html = create_scatter_chart(top_words)

    if chart_type in ["词云图", "饼图", "散点图"]:
        components.html(chart_html, height=600)