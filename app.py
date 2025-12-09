import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="محلل حملات تيك توك", layout="wide")

# --- الدالة الأساسية لسحب البيانات ---
def get_tiktok_data(urls):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    data = []
    
    # شريط التقدم في الواجهة
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            # تحديث شريط التقدم
            progress = (i + 1) / len(urls)
            progress_bar.progress(progress)
            status_text.text(f"جاري تحليل الرابط {i+1} من {len(urls)}...")
            
            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    data.append({
                        'Title': info.get('title', 'No Title'),
                        'Display Name': info.get('uploader', 'Unknown'), # الاسم المكتوب (اللقب)
                        'Username': info.get('uploader_id', 'Unknown'),  # اليوزرنيم (للمرجع فقط)
                        'Views': info.get('view_count', 0),
                        'Link': url
                    })
            except Exception:
                pass # تجاهل الروابط الخربانة
            
            time.sleep(0.5) 

    progress_bar.empty()
    status_text.empty()
    return data

# --- واجهة التطبيق ---
st.title("📊 تقرير حملة تيك توك الإعلانية")
st.markdown("---")

# 1. القائمة الجانبية للإدخال
with st.sidebar:
    st.header("إعدادات التقرير")
    
    # مكان لصق الروابط
    raw_urls = st.text_area("الصق روابط تيك توك هنا (رابط في كل سطر):", height=300)
    
    # خيار التصنيف
    label_choice = st.radio(
        "عرض الرسم البياني بناءً على:",
        ("اسم الحساب (Display Name)", "عنوان الفيديو (Title)")
    )
    
    analyze_btn = st.button("🚀 استخراج التقرير", type="primary")

# 2. منطقة العرض الرئيسية
if analyze_btn and raw_urls:
    urls_list = [line.strip() for line in raw_urls.split('\n') if line.strip()]
    
    if urls_list:
        with st.spinner('جاري الاتصال بسيرفرات تيك توك وسحب الأرقام...'):
            results = get_tiktok_data(urls_list)
        
        if results:
            df = pd.DataFrame(results)
            
            # الترتيب: الأكثر مشاهدة يكون تحت في الداتا فريم عشان يطلع فوق في الرسم (لأن الرسم يبدأ من تحت)
            # أو نستخدم المنطق المباشر ونرتب الرسم نفسه
            df = df.sort_values(by='Views', ascending=True)
            
            # --- عرض الإجماليات ---
            total_views = df['Views'].sum()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="إجمالي المشاهدات للحملة 🔥", value=f"{total_views:,}")
            with col2:
                st.metric(label="عدد الفيديوهات", value=len(df))
            with col3:
                top_video = df.iloc[-1]
                st.metric(label="أعلى فيديو مشاهدة", value=f"{top_video['Views']:,}")

            st.markdown("---")

            # --- الرسم البياني ---
            st.subheader("📈 أداء الفيديوهات (الأكثر مشاهدة)")
            
            # تحديد المحور الصادي
            if label_choice == "اسم الحساب (Display Name)":
                y_axis = 'Display Name' # هنا نستخدم الاسم المكتوب
            else:
                y_axis = 'Title'
            
            fig = px.bar(
                df, 
                x='Views', 
                y=y_axis, 
                orientation='h',
                text='Views',
                color='Views',
                color_continuous_scale='Viridis',
                hover_data=['Title', 'Display Name', 'Username', 'Views'] # يطلع لك اليوزرنيم كمان لما تحط الماوس
            )
            
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(
                height=600, 
                showlegend=False,
                yaxis={'categoryorder':'total ascending'} # يضمن ترتيب الأكثر فوق
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # --- عرض الجدول التفصيلي ---
            with st.expander("عرض الجدول التفصيلي للبيانات"):
                # نعرض الجدول مرتب من الأكثر للأقل، ونحط الأعمدة المهمة
                st.dataframe(
                    df.sort_values(by='Views', ascending=False)
                    [['Display Name', 'Username', 'Views', 'Title', 'Link']]
                )
                
        else:
            st.error("لم يتم العثور على بيانات. تأكد من صحة الروابط.")
    else:
        st.warning("الرجاء وضع روابط أولاً.")

elif analyze_btn and not raw_urls:
    st.warning("فضلاً الصق الروابط في الخانة الجانبية.")