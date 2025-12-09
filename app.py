import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="TikTok Analytics Pro", layout="wide", page_icon="🎨")

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
                    # uploader = الاسم الظاهر (Display Name)
                    # uploader_id = اليوزرنيم (@username)
                    data.append({
                        'Title': info.get('title', 'No Title'),
                        'Display Name': info.get('uploader', 'Unknown'), 
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
    st.header("⚙️ الإعدادات")
    
    st.markdown("### 1️⃣ البيانات")
    raw_urls = st.text_area("الروابط:", height=150, placeholder="https://www.tiktok.com/...")
    
    # خيار التسمية (تلقائياً اخترت لك الاسم الظاهر)
    label_choice = st.radio("تسمية البارات بـ:", ("اسم الحساب (الظاهر)", "عنوان الفيديو"))
    
    # تحديد العمود بناء على الاختيار
    if label_choice == "اسم الحساب (الظاهر)":
        y_axis_col = 'Display Name'
    else:
        y_axis_col = 'Title'

    st.markdown("### 2️⃣ التلوين")
    color_mode = st.selectbox(
        "نظام الألوان:",
        ("لون موحد (Brand)", "تخصيص يدوي (القائمة)", "ثيم متدرج")
    )
    
    selected_color = "#E91E63"
    selected_theme = "Viridis"
    
    if color_mode == "لون موحد (Brand)":
        selected_color = st.color_picker("اختر اللون:", "#E91E63")
    elif color_mode == "ثيم متدرج":
        selected_theme = st.selectbox("اختر الثيم:", ["Viridis", "Plasma", "Inferno", "Magma", "Blues", "Reds"])

    analyze_btn = st.button("🚀 تحليل البيانات", type="primary")

# --- الصفحة الرئيسية ---
st.title("🎨 TikTok Campaign Visualizer")

if raw_urls:
    if 'data_result' not in st.session_state or analyze_btn:
        urls_list = [line.strip() for line in raw_urls.split('\n') if line.strip()]
        if urls_list:
            with st.spinner('جاري سحب البيانات...'):
                st.session_state['data_result'] = get_tiktok_data(urls_list)
    
    if 'data_result' in st.session_state and st.session_state['data_result']:
        df = pd.DataFrame(st.session_state['data_result'])
        df = df.sort_values(by='Views', ascending=True) 
        
        final_fig = None
        
        # --- الوضع 1: تخصيص يدوي (قائمة منسدلة) ---
        if color_mode == "تخصيص يدوي (القائمة)":
            st.info("👇 عدّل الألوان من القائمة في الجدول، والرسم بيتغير فوراً.")
            
            # نجهز الداتا للتعديل
            edit_df = df.copy()
            # نضيف عمود لون افتراضي
            if 'Color' not in edit_df.columns:
                edit_df['Color'] = 'Gray' 
            
            # ترتيب للعرض (الأكثر فوق)
            edit_df = edit_df.sort_values(by='Views', ascending=False)
            
            # عرض الجدول مع "قائمة منسدلة" للألوان
            edited_data = st.data_editor(
                edit_df[[y_axis_col, 'Views', 'Color']], # نعرض بس الأعمدة المهمة
                column_config={
                    "Color": st.column_config.SelectboxColumn(
                        "اختر اللون",
                        help="اختر لون البار من القائمة",
                        width="medium",
                        # هذه القائمة اللي تطلع لك
                        options=[
                            "Red", "Blue", "Green", "Orange", "Purple", 
                            "Gold", "Black", "Gray", "Pink", "Teal", "Cyan"
                        ],
                        required=True
                    ),
                    "Views": st.column_config.NumberColumn("المشاهدات", disabled=True),
                    y_axis_col: st.column_config.TextColumn("الاسم", disabled=True)
                },
                use_container_width=True,
                hide_index=True,
                num_rows="fixed"
            )
            
            # الرسم بالألوان المختارة
            final_fig = px.bar(
                edited_data, 
                x='Views', 
                y=y_axis_col, 
                orientation='h', 
                text='Views'
            )
            final_fig.update_traces(marker_color=edited_data['Color'])

        # --- الوضع 2: لون موحد ---
        elif color_mode == "لون موحد (Brand)":
            final_fig = px.bar(
                df, x='Views', y=y_axis_col, orientation='h', text='Views',
                hover_data=['Title', 'Username']
            )
            final_fig.update_traces(marker_color=selected_color)

        # --- الوضع 3: متدرج ---
        elif color_mode == "ثيم متدرج":
            final_fig = px.bar(
                df, x='Views', y=y_axis_col, orientation='h', text='Views',
                color='Views',
                color_continuous_scale=selected_theme,
                hover_data=['Title', 'Username']
            )

        # تنسيقات الرسم النهائية
        if final_fig:
            final_fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            # ضمان الترتيب (الأكثر فوق)
            final_fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(final_fig, use_container_width=True)

        # تصدير
        st.markdown("---")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 تحميل البيانات (Excel)", csv, "report.csv", "text/csv")

else:
    st.info("👈 ابدأ بإدخال الروابط.")
