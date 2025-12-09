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
    
    # 1. الروابط
    st.markdown("### 1️⃣ البيانات")
    raw_urls = st.text_area("الروابط:", height=150, placeholder="https://www.tiktok.com/...")
    
    # 2. خيارات التسمية
    label_choice = st.radio("تسمية البارات بـ:", ("اسم الحساب", "عنوان الفيديو"))
    y_axis_col = 'Display Name' if label_choice == "اسم الحساب" else 'Title'

    # 3. خيارات الألوان (جوهر طلبك)
    st.markdown("### 2️⃣ نظام الألوان (Coloring Mode)")
    color_mode = st.selectbox(
        "اختر طريقة التلوين:",
        ("لون موحد (Brand)", "ثيم متدرج (Gradient)", "تخصيص يدوي لكل بار (Custom)")
    )
    
    # متغيرات الألوان
    selected_color = "#E91E63" # افتراضي
    selected_theme = "Viridis"
    
    if color_mode == "لون موحد (Brand)":
        selected_color = st.color_picker("اختر لون الهوية:", "#E91E63")
        
    elif color_mode == "ثيم متدرج (Gradient)":
        selected_theme = st.selectbox("اختر الثيم:", ["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Blues", "Reds"])

    analyze_btn = st.button("🚀 تحليل البيانات", type="primary")

# --- الصفحة الرئيسية ---
st.title("🎨 TikTok Campaign Visualizer")

if raw_urls:
    # التأكد من وجود بيانات في الذاكرة أو سحبها
    if 'data_result' not in st.session_state or analyze_btn:
        urls_list = [line.strip() for line in raw_urls.split('\n') if line.strip()]
        if urls_list:
            with st.spinner('جاري سحب البيانات...'):
                st.session_state['data_result'] = get_tiktok_data(urls_list)
    
    # إذا توفرت البيانات
    if 'data_result' in st.session_state and st.session_state['data_result']:
        df = pd.DataFrame(st.session_state['data_result'])
        df = df.sort_values(by='Views', ascending=True) # ترتيب أساسي
        
        # --- منطق التلوين المتقدم ---
        final_fig = None
        
        # الخيار 1: لون موحد
        if color_mode == "لون موحد (Brand)":
            final_fig = px.bar(
                df, x='Views', y=y_axis_col, orientation='h', text='Views',
                hover_data=['Title', 'Username']
            )
            final_fig.update_traces(marker_color=selected_color)

        # الخيار 2: ثيم متدرج
        elif color_mode == "ثيم متدرج (Gradient)":
            final_fig = px.bar(
                df, x='Views', y=y_axis_col, orientation='h', text='Views',
                color='Views', # التلوين بناء على القيمة
                color_continuous_scale=selected_theme,
                hover_data=['Title', 'Username']
            )

        # الخيار 3: تخصيص يدوي (الجديد)
        elif color_mode == "تخصيص يدوي لكل بار (Custom)":
            st.info("💡 يمكنك تعديل عمود 'Color' في الجدول أدناه لتغيير لون كل شريط على حدة (استخدم أسماء الألوان بالانجليزي أو أكواد #Hex).")
            
            # تجهيز جدول للتعديل
            edit_df = df[[y_axis_col, 'Views']].copy()
            edit_df = edit_df.sort_values(by='Views', ascending=False) # نعرض الأكثر مشاهدة فوق للتسهيل
            
            # إضافة لون افتراضي للكل
            if 'custom_colors' not in st.session_state:
                edit_df['Color'] = '#888888' # رمادي افتراضي
            
            # عرض محرر البيانات (Data Editor)
            edited_data = st.data_editor(
                edit_df,
                column_config={
                    "Color": st.column_config.TextColumn(
                        "لون البار (Hex/Name)",
                        help="اكتب red, blue, gold أو كود مثل #ff0000",
                        default="#888888",
                        required=True
                    ),
                    "Views": st.column_config.NumberColumn("المشاهدات", disabled=True),
                    y_axis_col: st.column_config.TextColumn("الاسم", disabled=True)
                },
                use_container_width=True,
                hide_index=True,
                num_rows="fixed"
            )
            
            # الرسم بناءً على الألوان المعدلة
            # نحتاج ندمج الألوان المعدلة مع الداتا الأصلية للرسم الصحيح
            final_fig = px.bar(
                edited_data, # نستخدم الداتا المعدلة
                x='Views', 
                y=y_axis_col, 
                orientation='h', 
                text='Views'
            )
            # تطبيق الألوان من العمود المعدل
            final_fig.update_traces(marker_color=edited_data['Color'])

        # --- عرض الرسم النهائي ---
        if final_fig:
            final_fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            final_fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(final_fig, use_container_width=True)

        # --- الإحصائيات السريعة ---
        st.markdown("---")
        total = df['Views'].sum()
        col1, col2 = st.columns(2)
        col1.metric("إجمالي المشاهدات", f"{total:,}")
        col2.metric("عدد المقاطع", len(df))
        
        # زر التصدير
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 تحميل البيانات (Excel)", csv, "report.csv", "text/csv")

else:
    st.info("👈 ابدأ بإدخال الروابط واضغط زر التحليل.")
