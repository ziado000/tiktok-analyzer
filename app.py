import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- 1. إعدادات الصفحة والتصميم الفخم (CSS) ---
st.set_page_config(page_title="TikTok Pro Dashboard", layout="wide", page_icon="🎵")

st.markdown("""
<style>
    /* خلفية الصفحة رمادية فاتحة لإبراز البطاقات */
    .stApp { background-color: #f0f2f5; }
    
    /* تصميم البطاقات البيضاء بزوايا دائرية وظل */
    .css-1r6slb0, .stDataFrame, .stDataEditor, .plotly-graph-div {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* تنسيق زر الإضافة والحذف */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    /* كروت الأرقام KPI */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        border: 1px solid #eee;
    }
    .kpi-metric { font-size: 32px; font-weight: 800; color: #000000; }
    .kpi-label { font-size: 14px; color: #666; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 2. البار العلوي الأسود الكبير (كما طلبت) ---
st.markdown("""
<div style="background-color: #000000; padding: 40px; border-radius: 0 0 25px 25px; color: white; margin-bottom: 40px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
    <img src="https://lf16-tiktok-web.ttwstatic.com/obj/tiktok-web/tiktok-logo.png" style="width: 150px; margin-bottom: 15px;">
    <h1 style='margin:0; font-size: 42px; font-weight: 700; color: white;'>Campaign Dashboard</h1>
    <p style='font-size: 18px; opacity: 0.8; color: #e0e0e0;'>نظام تحليل الحملات الإعلانية المتقدم</p>
</div>
""", unsafe_allow_html=True)

# --- 3. إدارة الروابط (نظام الخانات) ---
if 'input_links' not in st.session_state:
    st.session_state['input_links'] = [""]

def add_link(): st.session_state['input_links'].append("")
def remove_link(index): st.session_state['input_links'].pop(index)

# --- 4. دالة سحب البيانات ---
@st.cache_data(show_spinner=False)
def get_tiktok_data(urls):
    ydl_opts = {
        'quiet': True, 'skip_download': True, 'no_warnings': True, 'ignoreerrors': True,
    }
    data = []
    loading = st.empty()
    with loading.container():
        st.info("جاري الاتصال بقاعدة بيانات تيك توك... ⏳")
        bar = st.progress(0)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            bar.progress((i + 1) / len(urls))
            if not url.strip(): continue
            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    data.append({
                        'Title': info.get('title', 'No Title'),
                        'Display Name': info.get('uploader', info.get('uploader_id', 'Unknown')),
                        'Username': info.get('uploader_id', 'Unknown'),
                        'Views': info.get('view_count', 0),
                        'Followers': info.get('channel_follower_count', 0), # غالباً 0
                        'Likes': info.get('like_count', 0),
                        'Link': url
                    })
            except: pass
            time.sleep(0.2)
    loading.empty()
    return data

# --- 5. القائمة الجانبية (نظام الخانات الجديد) ---
with st.sidebar:
    st.title("⚙️ الإعدادات")
    st.markdown("---")
    
    st.markdown("### 1️⃣ الروابط")
    for i, link in enumerate(st.session_state['input_links']):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.session_state['input_links'][i] = st.text_input(f"رابط {i+1}", value=link, placeholder="https://tiktok.com/...", key=f"lk_{i}", label_visibility="collapsed")
        with c2:
            if len(st.session_state['input_links']) > 1:
                if st.button("✕", key=f"rm_{i}"):
                    remove_link(i)
                    st.rerun()
    
    if st.button("➕ إضافة رابط جديد", use_container_width=True):
        add_link()
        st.rerun()

    st.markdown("---")
    st.markdown("### 2️⃣ التخصيص")
    color_mode = st.selectbox("نمط الألوان:", ("ثيم تيك توك (أسود/أزرق/وردي)", "تخصيص يدوي", "تدرج لوني"))
    analyze_btn = st.button("🚀 تحديث الداشبورد", type="primary", use_container_width=True)

# --- 6. المحتوى الرئيسي ---

# التحقق والتشغيل
valid_urls = [x for x in st.session_state['input_links'] if x.strip()]

if valid_urls:
    if 'raw_data' not in st.session_state or analyze_btn:
        st.session_state['raw_data'] = get_tiktok_data(valid_urls)
            
    if st.session_state['raw_data']:
        df = pd.DataFrame(st.session_state['raw_data'])
        
        # --- جدول التعديل (الحل لمشكلة المتابعين) ---
        st.markdown("### ✏️ مراجعة البيانات (يمكنك تعديل الأرقام هنا)")
        edited_df = st.data_editor(
            df,
            column_config={
                "Followers": st.column_config.NumberColumn("المتابعين (عدّل الـ 0 هنا)", required=True, min_value=0, format="%d"),
                "Views": st.column_config.NumberColumn("المشاهدات", disabled=True),
                "Color": st.column_config.SelectboxColumn("اللون (للتخصيص)", options=["#000000", "#FE2C55", "#25F4EE", "Gold", "Gray"], required=False)
            },
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True
        )
        
        df_final = edited_df.sort_values(by='Views', ascending=True)
        
        st.markdown("---")
        
        # --- قسم الـ KPIs بتصميم البطاقات ---
        st.markdown("### 📊 ملخص الأداء")
        total_views = df_final['Views'].sum()
        total_followers = df_final['Followers'].sum()
        total_likes = df_final['Likes'].sum()
        
        k1, k2, k3 = st.columns(3)
        with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-metric">{total_views:,.0f}</div><div class="kpi-label">👁️ إجمالي المشاهدات</div></div>', unsafe_allow_html=True)
        with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-metric">{total_followers:,.0f}</div><div class="kpi-label">📢 مجموع المتابعين (Reach)</div></div>', unsafe_allow_html=True)
        with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-metric">{total_likes:,.0f}</div><div class="kpi-label">❤️ إجمالي الإعجابات</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # --- الرسم البياني ---
        st.markdown("### 📈 التحليل البصري")
        
        fig = None
        # منطق الألوان
        if color_mode == "تخصيص يدوي":
            if "Color" not in df_final.columns: df_final["Color"] = "#000000"
            df_final["Color"] = df_final["Color"].fillna("#000000")
            fig = px.bar(df_final, x='Views', y='Display Name', orientation='h', text='Views')
            fig.update_traces(marker_color=df_final['Color'])
        
        elif color_mode == "تدرج لوني":
            fig = px.bar(df_final, x='Views', y='Display Name', orientation='h', text='Views', color='Views', color_continuous_scale='Viridis')
        
        else: # ثيم تيك توك
            fig = px.bar(df_final, x='Views', y='Display Name', orientation='h', text='Views')
            fig.update_traces(marker_color='#FE2C55') # لون تيك توك الوردي

        # تنسيق الرسم النظيف
        if fig:
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=13)
            fig.update_layout(
                height=600,
                yaxis={'title': None, 'categoryorder':'total ascending'},
                xaxis={'showgrid': False, 'showticklabels': False, 'title': None},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # زر التحميل
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("💾 تحميل التقرير (Excel)", csv, "report.csv", "text/csv", use_container_width=True, type="primary")

else:
    st.info("👈 ابدأ بإضافة الروابط من القائمة الجانبية.")
