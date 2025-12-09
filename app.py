import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- 1. إعدادات الصفحة والتصميم الاحترافي (CSS) ---
st.set_page_config(page_title="TikTok Campaign Pro Dashboard", layout="wide", page_icon="🚀")

# حقن CSS لتخصيص المظهر وجعله احترافياً (بطاقات، ظلال، زوايا دائرية للحاويات)
st.markdown("""
<style>
    /* خلفية الصفحة */
    .stApp {
        background-color: #f0f2f5;
    }
    
    /* تصميم البطاقات (Cards) */
    .css-1r6slb0, .stDataFrame, .plotly-graph-div {
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
</style>
""", unsafe_allow_html=True)

# --- 2. دالة سحب البيانات (محدثة لسحب المتابعين واللايكات) ---
@st.cache_data(show_spinner=False)
def get_tiktok_data(urls):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    data = []
    # عناصر واجهة التحميل
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
            
            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    # محاولة سحب البيانات الإضافية
                    display_name = info.get('uploader', info.get('uploader_id', 'Unknown'))
                    followers = info.get('channel_follower_count', 0) # سحب عدد المتابعين
                    likes = info.get('like_count', 0) # سحب عدد اللايكات
                    shares = info.get('repost_count', 0) # سحب عدد المشاركات
                    avatar = info.get('uploader_url', '') # صورة البروفايل (أحياناً تضبط)

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
                print(f"Error showing URL {url}: {e}")
                pass
            time.sleep(0.3) # تسريع قليل

    loading_container.empty() # إخفاء شاشة التحميل
    return data

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3046/3046120.png", width=70)
    st.title("إعدادات الداشبورد")
    st.markdown("---")
    
    st.markdown("### 1️⃣ روابط الحملة")
    raw_urls = st.text_area("ألصق الروابط هنا:", height=200, placeholder="https://www.tiktok.com/...")
    
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

# هيدر الصفحة مع صورة خلفية جمالية
st.markdown("""
<div style="background: linear-gradient(90deg, #000000, #2c3e50); padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px; text-align: center;">
    <h1 style='margin:0; font-size: 42px;'>🚀 TikTok Campaign Pro Dashboard</h1>
    <p style='font-size: 18px; opacity: 0.8;'>لوحة تحكم تحليلية شاملة للأداء والمؤثرين</p>
</div>
""", unsafe_allow_html=True)


if raw_urls and analyze_btn:
    urls_list = [line.strip() for line in raw_urls.split('\n') if line.strip()]
    if urls_list:
        # سحب البيانات
        data_result = get_tiktok_data(urls_list)

    if data_result:
        df = pd.DataFrame(data_result)
        df_sorted = df.sort_values(by='Views', ascending=True)
        
        # ================= القسم الأول: نظرة عامة على الحملة (KPIs) =================
        st.markdown('<div class="section-header">📊 ملخص أداء الحملة (Campaign Overview)</div>', unsafe_allow_html=True)
        
        # حساب الإجماليات
        total_views = df['Views'].sum()
        total_likes = df['Likes'].sum()
        total_shares = df['Shares'].sum()
        avg_views = df['Views'].mean()

        # عرض الـ KPIs في بطاقات مخصصة
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

        # ================= القسم الثاني: تحليل صحة الحسابات (الجديد!) =================
        st.markdown('<div class="section-header">👥 تحليل الحسابات والمتابعين (Influencer Health)</div>', unsafe_allow_html=True)
        
        # تجميع البيانات حسب الحساب الفريد للحصول على المتابعين
        accounts_df = df.drop_duplicates(subset=['Username']).copy()
        total_reach = accounts_df['Followers'].sum()

        col_reach_summary, col_accounts_list = st.columns([1, 2])

        with col_reach_summary:
            st.markdown(f"""
            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="color: #1565c0; margin:0;">إجمالي الوصول المحتمل<br>(Total Potential Reach)</h3>
                <h1 style="color: #0d47a1; font-size: 48px; margin: 10px 0;">📢 {total_reach:,.0f}</h1>
                <p style="color: #546e7a;">مجموع متابعي جميع الحسابات الفريدة في الحملة.</p>
            </div>
            """, unsafe_allow_html=True)

        with col_accounts_list:
            st.markdown("#### قائمة الحسابات المشاركة:")
            # عرض جدول بسيط ونظيف للحسابات ومتابعيهم
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

        # ================= القسم الثالث: الرسم البياني للأداء (البارات) =================
        st.markdown('<div class="section-header">📈 تفاصيل أداء الفيديوهات (Performance Visuals)</div>', unsafe_allow_html=True)

        final_fig = None
        
        # منطق التلوين (كما طلبته سابقاً)
        if color_mode == "تخصيص يدوي (للتأكيد)":
            st.info("💡 استخدم الجدول أدناه لتحديد لون خاص لكل فيديو.")
            edit_df = df.copy().sort_values(by='Views', ascending=False)
            if 'Color' not in edit_df.columns: edit_df['Color'] = 'Gray'
            
            edited_data = st.data_editor(
                edit_df[[y_axis_col, 'Views', 'Color']],
                column_config={
                    "Color": st.column_config.SelectboxColumn("اختر اللون", options=["Red", "Blue", "Green", "Gold", "Black", "Gray", "Pink", "#FF0050"], required=True, width="medium"),
                    "Views": st.column_config.NumberColumn("المشاهدات", disabled=True, format="%d"),
                    y_axis_col: st.column_config.TextColumn("الاسم", disabled=True)
                },
                use_container_width=True, hide_index=True
            )
            final_fig = px.bar(edited_data, x='Views', y=y_axis_col, orientation='h', text='Views')
            final_fig.update_traces(marker_color=edited_data['Color'])

        elif color_mode == "لون موحد":
            final_fig = px.bar(df_sorted, x='Views', y=y_axis_col, orientation='h', text='Views', hover_data=['Title', 'Username', 'Likes'])
            final_fig.update_traces(marker_color=selected_color)

        elif color_mode == "ثيم متدرج احترافي":
            final_fig = px.bar(df_sorted, x='Views', y=y_axis_col, orientation='h', text='Views', color='Views',
                               color_continuous_scale=selected_theme, hover_data=['Title', 'Username', 'Likes'])

        # تنسيق الرسم البياني ليكون نظيفاً جداً داخل البطاقة
        if final_fig:
            final_fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=13)
            final_fig.update_layout(
                height=600,
                yaxis={'categoryorder':'total ascending', 'title': None, 'tickfont': {'size': 14}},
                xaxis={'title': None, 'showgrid': False, 'showticklabels': False}, # إخفاء المحور السيني
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20),
                font=dict(family="Helvetica, Arial, sans-serif", size=12, color="#333")
            )
            # عرض الرسم داخل حاوية بيضاء (البطاقة)
            st.plotly_chart(final_fig, use_container_width=True)

        # ================= القسم الرابع: التصدير =================
        st.markdown("---")
        col_export_text, col_export_btn = st.columns([3, 1])
        with col_export_text:
             st.markdown("### 💾 تصدير البيانات الشاملة")
             st.caption("قم بتحميل ملف Excel يحتوي على كافة التفاصيل (المشاهدات، اللايكات، المتابعين، الروابط).")
        with col_export_btn:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ تحميل تقرير Excel",
                data=csv,
                file_name="tiktok_pro_campaign_report.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

elif not raw_urls and not analyze_btn:
    # رسالة ترحيبية عند فتح الصفحة
    st.info("👋 مرحباً! ابدأ بلصق روابط حملة التيك توك في القائمة الجانبية لإنشاء الداشبورد.")
    st.image("https://cdn.dribbble.com/users/2057731/screenshots/16924739/media/67111394872296129441942d04010026.png?resize=800x600&vertical=center", use_container_width=True)
