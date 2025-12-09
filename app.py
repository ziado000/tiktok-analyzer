import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- إعدادات الصفحة (نفس التصميم السابق اللي عجبك) ---
st.set_page_config(page_title="TikTok Pro Analytics", layout="wide", page_icon="✨")

# --- تحسين المظهر (CSS) القديم ---
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .css-1d391kg, .stDataFrame, .stDataEditor {
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
    /* تنسيق زر الإضافة والحذف */
    div.stButton > button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- إدارة الروابط (ديناميكي) ---
if 'input_links' not in st.session_state:
    st.session_state['input_links'] = [""]

def add_link():
    st.session_state['input_links'].append("")

def remove_link(index):
    st.session_state['input_links'].pop(index)

# --- دالة سحب البيانات ---
@st.cache_data(show_spinner=False)
def get_tiktok_data(urls):
    ydl_opts = {
        'quiet': True, 'skip_download': True, 'no_warnings': True, 'ignoreerrors': True,
    }
    data = []
    progress_container = st.empty()
    progress_bar = progress_container.progress(0)
    status_text = st.empty()
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            progress_bar.progress((i + 1) / len(urls))
            status_text.caption(f"جاري معالجة الرابط {i+1} من {len(urls)}... ⏳")
            if not url.strip(): continue
            
            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    # محاولة سحب الاسم
                    display_name = info.get('uploader', info.get('uploader_id', 'Unknown'))
                    followers = info.get('channel_follower_count', 0)
                    
                    data.append({
                        'Title': info.get('title', 'No Title'),
                        'Display Name': display_name,
                        'Username': info.get('uploader_id', 'Unknown'),
                        'Views': info.get('view_count', 0),
                        'Followers': followers,
                        'Link': url
                    })
            except Exception:
                pass
            time.sleep(0.3)

    progress_container.empty()
    status_text.empty()
    return data

# --- القائمة الجانبية (نفس القديمة مع تعديل الروابط فقط) ---
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    
    st.markdown("### 1️⃣ الروابط")
    # --- نظام الخانات الجديد ---
    for i, link in enumerate(st.session_state['input_links']):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.session_state['input_links'][i] = st.text_input(f"رابط {i+1}", value=link, placeholder="https://tiktok.com/...", key=f"lnk_{i}", label_visibility="collapsed")
        with c2:
            if len(st.session_state['input_links']) > 1:
                if st.button("🗑️", key=f"del_{i}"):
                    remove_link(i)
                    st.rerun()
    
    if st.button("➕ إضافة رابط", use_container_width=True):
        add_link()
        st.rerun()
    # ---------------------------

    st.markdown("---")
    
    label_choice = st.radio("تسمية البارات بـ:", ("اسم الحساب (الظاهر)", "عنوان الفيديو"))
    y_axis_col = 'Display Name' if label_choice == "اسم الحساب (الظاهر)" else 'Title'

    st.markdown("### 2️⃣ المظهر والألوان")
    color_mode = st.selectbox(
        "طريقة التلوين:",
        ("لون موحد (Brand)", "تخصيص يدوي (القائمة)", "ثيم متدرج أنيق")
    )
    
    selected_color = "#E91E63"
    selected_theme = "Viridis"
    
    if color_mode == "لون موحد (Brand)":
        selected_color = st.color_picker("اختر لون الهوية:", "#FF0050")
    elif color_mode == "ثيم متدرج أنيق":
        selected_theme = st.selectbox("اختر التدرج:", ["Agsunset", "Sunsetdark", "Tealgrn", "Viridis", "Plasma"])

    st.markdown("---")
    analyze_btn = st.button("🚀 تحليل وبناء التقرير", type="primary", use_container_width=True)

# --- الصفحة الرئيسية (التصميم القديم) ---
st.title("✨ TikTok Campaign Visualizer")
st.caption("تقرير احترافي لأداء الفيديوهات")

# التأكد من وجود روابط
valid_urls = [x for x in st.session_state['input_links'] if x.strip()]

if valid_urls:
    if 'data_result' not in st.session_state or analyze_btn:
        with st.spinner('جاري الاتصال بالسيرفرات وتحليل البيانات...'):
            st.session_state['data_result'] = get_tiktok_data(valid_urls)
    
    if 'data_result' in st.session_state and st.session_state['data_result']:
        df = pd.DataFrame(st.session_state['data_result'])
        
        # --- (مهم) جعل الجدول قابل للتعديل عشان مشكلة المتابعين ---
        st.info("💡 إذا ظهر عدد المتابعين (0)، عدّله يدوياً في الجدول أدناه وسيتم تحديث التقرير فوراً.")
        
        edited_df = st.data_editor(
            df,
            column_config={
                "Followers": st.column_config.NumberColumn("المتابعين (عدّل هنا)", required=True, min_value=0),
                "Views": st.column_config.NumberColumn("المشاهدات", disabled=True),
                "Color": st.column_config.SelectboxColumn("لون (للوضع اليدوي)", options=["Red", "Blue", "Green", "Gold", "Black", "#FF0050"], required=False)
            },
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True
        )
        
        # نستخدم البيانات المعدلة
        df_final = edited_df.sort_values(by='Views', ascending=True)
        
        # --- قسم الأرقام (KPIs) - نفس الشكل القديم ---
        st.markdown("### 📊 نظرة عامة")
        total = df_final['Views'].sum()
        total_followers = df_final['Followers'].sum() # بيطلع صح بعد تعديلك
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("إجمالي المشاهدات 🔥", f"{total:,.0f}")
        kpi2.metric("مجموع المتابعين (Reach)", f"{total_followers:,.0f}")
        kpi3.metric("عدد المقاطع", len(df_final))
        
        st.markdown("---")
        
        # --- الرسم البياني ---
        final_fig = None
        st.subheader("📈 تفاصيل الأداء")

        # منطق التلوين
        if color_mode == "تخصيص يدوي (القائمة)":
            # إذا ما فيه عمود لون ننشئه
            if 'Color' not in df_final.columns:
                 df_final['Color'] = "#FF0050"
            df_final['Color'] = df_final['Color'].fillna("#FF0050")
            
            final_fig = px.bar(df_final, x='Views', y=y_axis_col, orientation='h', text='Views')
            final_fig.update_traces(marker_color=df_final['Color'])

        elif color_mode == "لون موحد (Brand)":
            final_fig = px.bar(df_final, x='Views', y=y_axis_col, orientation='h', text='Views', hover_data=['Title', 'Username'])
            final_fig.update_traces(marker_color=selected_color)

        elif color_mode == "ثيم متدرج أنيق":
            final_fig = px.bar(df_final, x='Views', y=y_axis_col, orientation='h', text='Views', color='Views',
                               color_continuous_scale=selected_theme, hover_data=['Title', 'Username'])

        # --- الستايل النظيف (القديم) ---
        if final_fig:
            final_fig.update_traces(
                texttemplate='%{text:,.0f}',
                textposition='outside',
                textfont_size=14,
                marker=dict(line=dict(width=0)) 
            )
            
            final_fig.update_layout(
                height=600,
                yaxis={'categoryorder':'total ascending', 'title': None, 'tickfont': {'size': 14}},
                xaxis={'title': None, 'showgrid': False, 'zeroline': False, 'showticklabels': False},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                font=dict(family="Arial, sans-serif", size=12, color="#333333"),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(final_fig, use_container_width=True)

        # تصدير
        st.markdown("---")
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("💾 تحميل البيانات (Excel Report)", csv, "tiktok_report.csv", "text/csv", type="secondary")

else:
    st.info("👈 استخدم زر 'إضافة رابط' في القائمة الجانبية.")
