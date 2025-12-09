import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- 1. إعدادات الصفحة والتصميم الاحترافي (CSS) ---
# (نفس الستايل اللي أرسلته لي بالضبط)
st.set_page_config(page_title="TikTok Campaign Pro Dashboard", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    /* خلفية الصفحة */
    .stApp {
        background-color: #f0f2f5;
    }
    
    /* تصميم البطاقات (Cards) */
    .css-1r6slb0, .stDataFrame, .stDataEditor, .plotly-graph-div {
        background-color: #ffffff;
        border-radius: 20px; /* زوايا دائرية للحاويات */
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); /* ظل خفيف */
        margin-bottom: 20px;
    }

    /* تصميم خاص لعناوين الأقسام */
    .section-header {
        font-size: 24px;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    
    /* تصميم بطاقات الـ KPI الصغيرة */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        border: 1px solid #eee;
    }
    .kpi-metric {
        font-size: 32px;
        font-weight: 800;
        color: #E91E63;
    }
    .kpi-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    
    /* تنسيق أزرار الإضافة والحذف */
    div.stButton > button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- إضافة: إدارة الروابط (Session State) ---
if 'input_links' not in st.session_state:
    st.session_state['input_links'] = [""]

def add_link():
    st.session_state['input_links'].append("")

def remove_link(index):
    st.session_state['input_links'].pop(index)

# --- 2. دالة سحب البيانات ---
@st.cache_data(show_spinner=False)
def get_tiktok_data(urls):
    ydl_opts = {
        'quiet': True, 'skip_download': True, 'no_warnings': True, 'ignoreerrors': True,
    }
    
    data = []
    loading_container = st.empty()
    with loading_container.container():
        st.markdown("### 🔄 جاري الاتصال بمنصة TikTok...")
        progress_bar = st.progress(0)
        status_text = st.empty()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            progress = (i + 1) / len(urls)
            progress_bar.progress(progress)
            status_text.info(f"تحليل الرابط {i+1} من {len(urls)}: {url[:30]}...")
            
            if not url.strip(): continue

            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    display_name = info.get('uploader', info.get('uploader_id', 'Unknown'))
                    followers = info.get('channel_follower_count', 0)
                    likes = info.get('like_count', 0)
                    shares = info.get('repost_count', 0)
                    avatar = info.get('uploader_url', '')

                    data.append({
                        'Title': info.get('title', 'No Title'),
                        'Display Name': display_name,
                        'Username': info.get('uploader_id', 'Unknown'),
                        'Views': info.get('view_count', 0),
                        'Likes': likes,
                        'Shares': shares,
                        'Followers': followers,
                        'Avatar URL': avatar,
                        'Link': url
                    })
            except Exception as e:
                pass
            time.sleep(0.3)

    loading_container.empty()
    return data

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3046/3046120.png", width=70)
    st.title("إعدادات الداشبورد")
    st.markdown("---")
    
    st.markdown("### 1️⃣ روابط الحملة")
    
    # --- التعديل: نظام الخانات (+) بدلاً من النص ---
    for i, link in enumerate(st.session_state['input_links']):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.session_state['input_links'][i] = st.text_input(f"رابط {i+1}", value=link, placeholder="https://tiktok.com/...", key=f"lnk_{i}", label_visibility="collapsed")
        with c2:
            if len(st.session_state['input_links']) > 1:
                if st.button("✕", key=f"del_{i}"):
                    remove_link(i)
                    st.rerun()
    
    if st.button("➕ إضافة رابط", use_container_width=True):
        add_link()
        st.rerun()
    # ---------------------------------------------
    
    st.markdown("---")
    st.markdown("### 2️⃣ تخصيص العرض")
    label_choice = st.radio("تسمية البارات بـ:", ("اسم الحساب (الظاهر)", "عنوان الفيديو"))
    y_axis_col = 'Display Name' if label_choice == "اسم الحساب (الظاهر)" else 'Title'

    st.markdown("### 3️⃣ الثيم والألوان")
    color_mode = st.selectbox("نمط التلوين:", ("ثيم متدرج احترافي", "تخصيص يدوي (للتأكيد)", "لون موحد"))
    
    selected_theme = "Viridis"
    selected_color = "#FF0050"

    if color_mode == "ثيم متدرج احترافي":
        selected_theme = st.selectbox("اختر التدرج:", ["Sunsetdark", "Agsunset", "Tealgrn", "Viridis", "Plasma"])
    elif color_mode == "لون موحد":
        selected_color = st.color_picker("اختر لون الهوية:", "#FF0050")

    st.markdown("---")
    analyze_btn = st.button("🚀 إنشاء الداشبورد الشامل", type="primary", use_container_width=True)
    st.caption("Powered by Streamlit & yt-dlp")

# --- 4. منطقة المحتوى الرئيسية ---

st.markdown("""
<div style="background: linear-gradient(90deg, #000000, #2c3e50); padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px; text-align: center;">
    <h1 style='margin:0; font-size: 42px;'>🚀 TikTok Campaign Pro Dashboard</h1>
    <p style='font-size: 18px; opacity: 0.8;'>لوحة تحكم تحليلية شاملة للأداء والمؤثرين</p>
</div>
""", unsafe_allow_html=True)

# فلترة الروابط الفارغة
valid_urls = [x for x in st.session_state['input_links'] if x.strip()]

if valid_urls and analyze_btn:
    if 'data_result' not in st.session_state or analyze_btn:
        st.session_state['data_result'] = get_tiktok_data(valid_urls)

if valid_urls and 'data_result' in st.session_state and st.session_state['data_result']:
    df = pd.DataFrame(st.session_state['data_result'])
    
    # --- التعديل: إضافة جدول التحرير (Data Editor) ---
    st.markdown('<div class="section-header">✏️ مراجعة وتعديل البيانات (خاصة المتابعين)</div>', unsafe_allow_html=True)
    st.info("💡 يمكنك الضغط على أي خلية لتعديلها (مثلاً: إذا ظهر عدد المتابعين 0).")
    
    edited_df = st.data_editor(
        df,
        column_config={
            "Followers": st.column_config.NumberColumn("المتابعين (عدل هنا)", required=True, min_value=0, format="%d"),
            "Views": st.column_config.NumberColumn("المشاهدات", disabled=True),
            "Color": st.column_config.SelectboxColumn("لون (للوضع اليدوي)", options=["Red", "Blue", "Green", "Gold", "Black", "#FF0050"], required=False)
        },
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True
    )
    
    # استخدام البيانات المعدلة للرسم والحسابات
    df_final = edited_df.sort_values(by='Views', ascending=True)
    
    # ================= القسم الأول: نظرة عامة على الحملة (KPIs) =================
    st.markdown('<div class="section-header">📊 ملخص أداء الحملة (Campaign Overview)</div>', unsafe_allow_html=True)
    
    total_views = df_final['Views'].sum()
    total_likes = df_final['Likes'].sum()
    total_shares = df_final['Shares'].sum()
    avg_views = df_final['Views'].mean()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-metric">🔥 {total_views:,.0f}</div><div class="kpi-label">إجمالي المشاهدات</div></div>""", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-metric">❤️ {total_likes:,.0f}</div><div class="kpi-label">إجمالي الإعجابات</div></div>""", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-metric">↗️ {total_shares:,.0f}</div><div class="kpi-label">إجمالي المشاركات</div></div>""", unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-metric">📈 {avg_views:,.0f}</div><div class="kpi-label">متوسط المشاهدات/فيديو</div></div>""", unsafe_allow_html=True)
    
    st.markdown("---")

    # ================= القسم الثاني: تحليل صحة الحسابات =================
    st.markdown('<div class="section-header">👥 تحليل الحسابات والمتابعين (Influencer Health)</div>', unsafe_allow_html=True)
    
    # استخدام البيانات المعدلة هنا أيضاً
    accounts_df = df_final.drop_duplicates(subset=['Username']).copy()
    total_reach = accounts_df['Followers'].sum() # سيحسب الرقم الصحيح بعد تعديلك

    col_reach_summary, col_accounts_list = st.columns([1, 2])

    with col_reach_summary:
        st.markdown(f"""
        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 15px; text-align: center;">
            <h3 style="color: #1565c0; margin:0;">إجمالي الوصول المحتمل<br>(Total Potential Reach)</h3>
            <h1 style="color: #0d47a1; font-size: 48px; margin: 10px 0;">📢 {total_reach:,.0f}</h1>
            <p style="color: #546e7a;">مجموع متابعي جميع الحسابات المشاركة (بعد التعديل).</p>
        </div>
        """, unsafe_allow_html=True)

    with col_accounts_list:
        st.markdown("#### قائمة الحسابات المشاركة:")
        st.dataframe(
            accounts_df[['Display Name', 'Username', 'Followers']].sort_values(by='Followers', ascending=False),
            column_config={
                "Display Name": "الاسم الظاهر",
                "Username": "اليوزرنيم",
                "Followers": st.column_config.NumberColumn("عدد المتابعين", format="%d ⭐")
            },
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # ================= القسم الثالث: الرسم البياني =================
    st.markdown('<div class="section-header">📈 تفاصيل أداء الفيديوهات (Performance Visuals)</div>', unsafe_allow_html=True)

    final_fig = None
    
    if color_mode == "تخصيص يدوي (للتأكيد)":
        if 'Color' not in df_final.columns: df_final['Color'] = "#FF0050"
        df_final['Color'] = df_final['Color'].fillna("#FF0050")
        
        final_fig = px.bar(df_final, x='Views', y=y_axis_col, orientation='h', text='Views')
        final_fig.update_traces(marker_color=df_final['Color'])

    elif color_mode == "لون موحد":
        final_fig = px.bar(df_final, x='Views', y=y_axis_col, orientation='h', text='Views', hover_data=['Title', 'Username', 'Likes'])
        final_fig.update_traces(marker_color=selected_color)

    elif color_mode == "ثيم متدرج احترافي":
        final_fig = px.bar(df_final, x='Views', y=y_axis_col, orientation='h', text='Views', color='Views',
                           color_continuous_scale=selected_theme, hover_data=['Title', 'Username', 'Likes'])

    if final_fig:
        final_fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=13)
        final_fig.update_layout(
            height=600,
            yaxis={'categoryorder':'total ascending', 'title': None, 'tickfont': {'size': 14}},
            xaxis={'title': None, 'showgrid': False, 'showticklabels': False},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family="Helvetica, Arial, sans-serif", size=12, color="#333")
        )
        st.plotly_chart(final_fig, use_container_width=True)

    # ================= القسم الرابع: التصدير =================
    st.markdown("---")
    col_export_text, col_export_btn = st.columns([3, 1])
    with col_export_text:
         st.markdown("### 💾 تصدير البيانات الشاملة")
         st.caption("قم بتحميل ملف Excel يحتوي على كافة التفاصيل (المشاهدات، اللايكات، المتابعين، الروابط).")
    with col_export_btn:
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ تحميل تقرير Excel",
            data=csv,
            file_name="tiktok_pro_campaign_report.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

elif not valid_urls and not analyze_btn:
    st.info("👋 مرحباً! ابدأ بلصق روابط حملة التيك توك في القائمة الجانبية.")
    st.image("https://cdn.dribbble.com/users/2057731/screenshots/16924739/media/67111394872296129441942d04010026.png?resize=800x600&vertical=center", use_container_width=True)
