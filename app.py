import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- إعدادات الصفحة بتصميم حديث ---
st.set_page_config(page_title="TikTok Pro Analytics", layout="wide", page_icon="✨")

# --- تحسين المظهر العام بالـ CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .css-1d391kg {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- دالة سحب البيانات ---
@st.cache_data(show_spinner=False)
def get_tiktok_data(urls):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    data = []
    progress_container = st.empty()
    progress_bar = progress_container.progress(0)
    status_text = st.empty()
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            progress = (i + 1) / len(urls)
            progress_bar.progress(progress)
            status_text.caption(f"جاري معالجة الرابط {i+1} من {len(urls)}... ⏳")
            
            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    # محاولة سحب الاسم الظاهر بدقة
                    display_name = info.get('uploader', info.get('uploader_id', 'Unknown'))
                    
                    data.append({
                        'Title': info.get('title', 'No Title'),
                        'Display Name': display_name,
                        'Username': info.get('uploader_id', 'Unknown'),
                        'Views': info.get('view_count', 0),
                        'Link': url
                    })
            except Exception:
                pass
            time.sleep(0.5)

    progress_container.empty()
    status_text.empty()
    return data

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    
    st.markdown("### 1️⃣ الروابط")
    raw_urls = st.text_area("ألصق الروابط هنا:", height=150, placeholder="https://www.tiktok.com/...")
    
    label_choice = st.radio("تسمية البارات بـ:", ("اسم الحساب (الظاهر)", "عنوان الفيديو"))
    if label_choice == "اسم الحساب (الظاهر)":
        y_axis_col = 'Display Name'
    else:
        y_axis_col = 'Title'

    st.markdown("---")
    st.markdown("### 2️⃣ المظهر والألوان")
    color_mode = st.selectbox(
        "طريقة التلوين:",
        ("لون موحد (Brand)", "تخصيص يدوي (القائمة)", "ثيم متدرج أنيق")
    )
    
    selected_color = "#E91E63"
    selected_theme = "Viridis"
    
    if color_mode == "لون موحد (Brand)":
        selected_color = st.color_picker("اختر لون الهوية:", "#FF0050") # لون تيك توك الافتراضي
    elif color_mode == "ثيم متدرج أنيق":
        selected_theme = st.selectbox("اختر التدرج:", ["Agsunset", "Sunsetdark", "Tealgrn", "Viridis", "Plasma"])

    st.markdown("---")
    analyze_btn = st.button("🚀 تحليل وبناء التقرير", type="primary", use_container_width=True)

# --- الصفحة الرئيسية ---
st.title("✨ TikTok Campaign Visualizer")
st.caption("تقرير احترافي لأداء الفيديوهات")

if raw_urls:
    if 'data_result' not in st.session_state or analyze_btn:
        urls_list = [line.strip() for line in raw_urls.split('\n') if line.strip()]
        if urls_list:
            with st.spinner('جاري الاتصال بالسيرفرات وتحليل البيانات...'):
                st.session_state['data_result'] = get_tiktok_data(urls_list)
    
    if 'data_result' in st.session_state and st.session_state['data_result']:
        df = pd.DataFrame(st.session_state['data_result'])
        df = df.sort_values(by='Views', ascending=True)
        
        # --- قسم الأرقام (KPIs) بتصميم جديد ---
        st.markdown("### 📊 نظرة عامة")
        total = df['Views'].sum()
        avg = df['Views'].mean()
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("إجمالي المشاهدات 🔥", f"{total:,.0f}")
        kpi2.metric("متوسط المشاهدات", f"{avg:,.0f}")
        kpi3.metric("عدد المقاطع", len(df))
        
        st.markdown("---")
        
        # --- تجهيز الرسم البياني ---
        final_fig = None
        st.subheader("📈 تفاصيل الأداء")

        # منطق التلوين
        if color_mode == "تخصيص يدوي (القائمة)":
            st.info("👇 استخدم القائمة المنسدلة في الجدول أدناه لتلوين كل بار على حدة.")
            edit_df = df.copy().sort_values(by='Views', ascending=False)
            if 'Color' not in edit_df.columns: edit_df['Color'] = 'Gray'
            
            edited_data = st.data_editor(
                edit_df[[y_axis_col, 'Views', 'Color']],
                column_config={
                    "Color": st.column_config.SelectboxColumn(
                        "اختر اللون",
                        options=["Red", "Blue", "Green", "Orange", "Purple", "Gold", "Black", "Gray", "Pink", "Cyan", "#FF0050"],
                        required=True, width="medium"
                    ),
                    "Views": st.column_config.NumberColumn("المشاهدات", disabled=True, format="%d"),
                    y_axis_col: st.column_config.TextColumn("الاسم", disabled=True)
                },
                use_container_width=True, hide_index=True, num_rows="fixed"
            )
            final_fig = px.bar(edited_data, x='Views', y=y_axis_col, orientation='h', text='Views')
            final_fig.update_traces(marker_color=edited_data['Color'])

        elif color_mode == "لون موحد (Brand)":
            final_fig = px.bar(df, x='Views', y=y_axis_col, orientation='h', text='Views', hover_data=['Title', 'Username'])
            final_fig.update_traces(marker_color=selected_color)

        elif color_mode == "ثيم متدرج أنيق":
            final_fig = px.bar(df, x='Views', y=y_axis_col, orientation='h', text='Views', color='Views',
                               color_continuous_scale=selected_theme, hover_data=['Title', 'Username'])

        # --- تطبيق الستايل الاحترافي والنظيف على الرسم (أهم جزء) ---
        if final_fig:
            final_fig.update_traces(
                texttemplate='%{text:,.0f}', # تنسيق الرقم بدون فواصل عشرية
                textposition='outside',
                textfont_size=14,
                # محاولة لتنعيم الحواف قليلاً (ليست دائرية تماماً لكن أفضل)
                marker=dict(line=dict(width=0)) 
            )
            
            # تنظيف خلفية الرسم وإزالة الخطوط المزعجة
            final_fig.update_layout(
                height=600,
                yaxis={'categoryorder':'total ascending', 'title': None, 'tickfont': {'size': 14}}, # إخفاء عنوان المحور
                xaxis={'title': None, 'showgrid': False, 'zeroline': False, 'showticklabels': False}, # إخفاء شبكة المحور السيني
                plot_bgcolor='rgba(0,0,0,0)', # خلفية شفافة للرسم
                paper_bgcolor='rgba(0,0,0,0)', # خلفية شفافة للإطار
                showlegend=False,
                font=dict(family="Arial, sans-serif", size=12, color="#333333"), # خط حديث
                margin=dict(l=20, r=20, t=30, b=20) # هوامش نظيفة
            )
            st.plotly_chart(final_fig, use_container_width=True)

        # تصدير
        st.markdown("---")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 تحميل البيانات (Excel Report)", csv, "tiktok_report.csv", "text/csv", type="secondary")

else:
    st.info("👈 ابدأ بلصق روابط الفيديو في القائمة الجانبية.")
