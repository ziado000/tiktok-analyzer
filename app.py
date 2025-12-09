import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Pro TikTok Analytics", layout="wide", page_icon="📊")

# --- دالة سحب البيانات ---
@st.cache_data(show_spinner=False) # تخزين مؤقت عشان لو غير اللون ما يعيد التحميل
def get_tiktok_data(urls):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    data = []
    
    # مكان شريط التقدم
    progress_container = st.empty()
    progress_bar = progress_container.progress(0)
    status_text = st.empty()
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            progress = (i + 1) / len(urls)
            progress_bar.progress(progress)
            status_text.caption(f"جاري تحليل الرابط {i+1} من {len(urls)}... ⏳")
            
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

    progress_container.empty() # إخفاء الشريط بعد الانتهاء
    status_text.empty()
    return data

# --- القائمة الجانبية (لوحة التحكم) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3046/3046121.png", width=50)
    st.title("إعدادات التقرير")
    
    st.markdown("### 1️⃣ البيانات")
    raw_urls = st.text_area("الصق الروابط هنا:", height=200, placeholder="https://www.tiktok.com/...")
    
    st.markdown("### 2️⃣ التخصيص (Thmeming)")
    # ميزة اختيار اللون
    chart_color = st.color_picker("اختر لون هوية العميل:", "#E91E63") 
    
    label_choice = st.radio(
        "تسمية البارات بـ:",
        ("اسم الحساب (Display Name)", "عنوان الفيديو (Title)")
    )
    
    analyze_btn = st.button("🚀 إنشاء التقرير الشامل", type="primary")

# --- منطقة العرض الرئيسية ---
st.header("📊 لوحة تحليلات حملة تيك توك")
st.caption("تقرير أداء تفاعلي")
st.markdown("---")

if analyze_btn and raw_urls:
    urls_list = [line.strip() for line in raw_urls.split('\n') if line.strip()]
    
    if urls_list:
        with st.spinner('جاري جلب البيانات وتحليل الأرقام...'):
            results = get_tiktok_data(urls_list)
        
        if results:
            df = pd.DataFrame(results)
            df = df.sort_values(by='Views', ascending=True) # ترتيب للرسم
            
            # --- 1. قسم الأرقام القياسية (KPIs) ---
            total_views = df['Views'].sum()
            avg_views = df['Views'].mean()
            top_video = df.iloc[-1]
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("إجمالي المشاهدات 🔥", f"{total_views:,.0f}")
            c2.metric("متوسط المشاهدات 📈", f"{avg_views:,.0f}")
            c3.metric("عدد المقاطع 🎬", len(df))
            c4.metric("الأعلى أداءً 🏆", f"{top_video['Views']:,}")
            
            st.markdown("---")

            # --- 2. الرسم البياني الرئيسي (البارات) ---
            col_main, col_pie = st.columns([2, 1]) # تقسيم الشاشة ثلثين وثلث
            
            with col_main:
                st.subheader("أداء الفيديوهات")
                
                y_axis = 'Display Name' if label_choice == "اسم الحساب (Display Name)" else 'Title'
                
                fig_bar = px.bar(
                    df, x='Views', y=y_axis, orientation='h', text='Views',
                    hover_data=['Title', 'Username']
                )
                
                # تطبيق لون العميل المختار
                fig_bar.update_traces(marker_color=chart_color, texttemplate='%{text:,}', textposition='outside')
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
                
                st.plotly_chart(fig_bar, use_container_width=True)

            # --- 3. الرسم الدائري (جديد: حصة المشاهدات) ---
            with col_pie:
                st.subheader("حصة المشاهدات (Share)")
                # تجميع البيانات حسب الحساب عشان نعرف مين المسيطر
                pie_df = df.groupby('Display Name')['Views'].sum().reset_index()
                
                fig_pie = px.pie(
                    pie_df, values='Views', names='Display Name',
                    hole=0.4 # عشان يصير شكلها دونات
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(showlegend=False, height=500)
                
                st.plotly_chart(fig_pie, use_container_width=True)

            # --- 4. جدول البيانات والتصدير ---
            st.markdown("### 📋 تفاصيل البيانات")
            
            # ترتيب الجدول من الأكثر للأقل
            df_display = df.sort_values(by='Views', ascending=False)
            st.dataframe(df_display, use_container_width=True)
            
            # زر التحميل (CSV)
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 تحميل التقرير (Excel/CSV)",
                data=csv,
                file_name='tiktok_campaign_report.csv',
                mime='text/csv',
            )
            
        else:
            st.error("لم يتم العثور على بيانات.")
    else:
        st.warning("الرجاء إدخال روابط صحيحة.")

elif not raw_urls:
    st.info("👈 ابدأ بلصق الروابط في القائمة الجانبية واضغط زر الإنشاء.")
