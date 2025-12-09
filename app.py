import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- 1. إعدادات الصفحة والتصميم (CSS) ---
st.set_page_config(page_title="TikTok Pro Dashboard", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    /* تحسين الخطوط والخلفية */
    .stApp { background-color: #f4f7f6; }
    
    /* تصميم البطاقات البيضاء */
    .css-1r6slb0, .stDataFrame, .plotly-graph-div {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* تصميم زر الإضافة والحذف */
    div.stButton > button {
        border-radius: 10px;
        font-weight: bold;
    }

    /* عناوين الأقسام */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 15px;
        border-right: 5px solid #E91E63;
        padding-right: 15px;
    }
    
    /* بطاقات الأرقام KPI */
    .kpi-box {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .kpi-value { font-size: 28px; font-weight: 800; color: #E91E63; }
    .kpi-label { font-size: 14px; color: #7f8c8d; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 2. إدارة الروابط (Session State) ---
if 'input_links' not in st.session_state:
    st.session_state['input_links'] = [""] # نبدأ برابط واحد فارغ

def add_link():
    st.session_state['input_links'].append("")

def remove_link(index):
    st.session_state['input_links'].pop(index)

# --- 3. دالة سحب البيانات ---
@st.cache_data(show_spinner=False)
def get_tiktok_data(urls):
    ydl_opts = {
        'quiet': True, 'skip_download': True, 'no_warnings': True, 'ignoreerrors': True,
    }
    data = []
    
    # واجهة تحميل جميلة
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.info("جاري الاتصال بسيرفرات تيك توك... ⏳")
        progress_bar = st.progress(0)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            progress_bar.progress((i + 1) / len(urls))
            if not url.strip(): continue # تجاهل الخانات الفاضية
            
            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    # محاولة جلب البيانات
                    display_name = info.get('uploader', info.get('uploader_id', 'Unknown'))
                    # ملاحظة: المتابعين غالباً 0 بسبب حماية تيك توك، سنسمح بتعديلها يدوياً
                    followers = info.get('channel_follower_count', 0) 
                    
                    data.append({
                        'Title': info.get('title', 'No Title'),
                        'Display Name': display_name,
                        'Username': info.get('uploader_id', 'Unknown'),
                        'Views': info.get('view_count', 0),
                        'Likes': info.get('like_count', 0),
                        'Shares': info.get('repost_count', 0),
                        'Followers': followers, # قد يكون 0
                        'Link': url
                    })
            except:
                pass
            time.sleep(0.2)

    loading_placeholder.empty()
    return data

# --- 4. القائمة الجانبية (الإدخال الديناميكي) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3046/3046120.png", width=60)
    st.title("لوحة التحكم")
    st.markdown("---")
    
    st.markdown("### 1️⃣ إضافة الروابط")
    
    # حلقة تكرار لعرض حقول الإدخال
    for i, link in enumerate(st.session_state['input_links']):
        col_in, col_btn = st.columns([4, 1])
        with col_in:
            st.session_state['input_links'][i] = st.text_input(
                f"رابط {i+1}", 
                value=link, 
                placeholder="https://www.tiktok.com/@...", 
                key=f"link_{i}",
                label_visibility="collapsed"
            )
        with col_btn:
            if len(st.session_state['input_links']) > 1:
                if st.button("🗑️", key=f"del_{i}", help="حذف هذا الرابط"):
                    remove_link(i)
                    st.rerun()

    if st.button("➕ إضافة خانة جديدة", use_container_width=True):
        add_link()
        st.rerun()

    st.markdown("---")
    st.markdown("### 2️⃣ التخصيص")
    color_mode = st.selectbox("الألوان:", ("ثيم متدرج (Viridis)", "لون موحد (أحمر تيك توك)", "تخصيص يدوي"))
    
    analyze_btn = st.button("🚀 تحليل البيانات", type="primary", use_container_width=True)

# --- 5. الصفحة الرئيسية ---
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color:#2c3e50;">📊 TikTok Campaign Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# التنفيذ عند الضغط
if analyze_btn:
    # فلترة الروابط الفارغة
    valid_urls = [x for x in st.session_state['input_links'] if x.strip()]
    
    if valid_urls:
        if 'raw_data' not in st.session_state:
            st.session_state['raw_data'] = get_tiktok_data(valid_urls)
            
        # --- مرحلة تعديل البيانات (الحل لمشكلة المتابعين) ---
        if st.session_state['raw_data']:
            df = pd.DataFrame(st.session_state['raw_data'])
            
            st.markdown("""
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; color: #856404; margin-bottom: 20px;">
                💡 <b>تنبيه ذكي:</b> إذا ظهر عدد المتابعين (0)، يمكنك تعديل الرقم يدوياً في الجدول أدناه قبل عرض الرسوم البيانية.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="section-title">✏️ مراجعة وتعديل البيانات</div>', unsafe_allow_html=True)
            
            # عرض محرر البيانات (Data Editor)
            edited_df = st.data_editor(
                df,
                column_config={
                    "Followers": st.column_config.NumberColumn("عدد المتابعين (عدل هنا)", required=True, min_value=0),
                    "Views": st.column_config.NumberColumn("المشاهدات", disabled=True),
                    "Link": st.column_config.LinkColumn("الرابط"),
                    "Color": st.column_config.SelectboxColumn("لون البار (للتخصيص اليدوي)", options=["Red", "Blue", "Green", "Gold", "Black", "#FF0050"], required=False)
                },
                use_container_width=True,
                num_rows="dynamic",
                key="editor"
            )
            
            # استخدام البيانات المعدلة (Edited) للرسم
            final_df = edited_df.sort_values(by='Views', ascending=True)

            st.markdown("---")
            
            # --- قسم الـ KPIs ---
            st.markdown('<div class="section-title">📌 ملخص الأداء (KPIs)</div>', unsafe_allow_html=True)
            total_views = final_df['Views'].sum()
            total_followers = final_df['Followers'].sum() # هذا الرقم الآن سيكون صحيحاً بعد تعديلك
            total_likes = final_df['Likes'].sum()
            
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f'<div class="kpi-box"><div class="kpi-value">{total_views:,.0f}</div><div class="kpi-label">إجمالي المشاهدات</div></div>', unsafe_allow_html=True)
            with k2: st.markdown(f'<div class="kpi-box"><div class="kpi-value">{total_followers:,.0f}</div><div class="kpi-label">مجموع المتابعين (Reach)</div></div>', unsafe_allow_html=True)
            with k3: st.markdown(f'<div class="kpi-box"><div class="kpi-value">{total_likes:,.0f}</div><div class="kpi-label">إجمالي الإعجابات</div></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # --- الرسم البياني ---
            st.markdown('<div class="section-title">📈 التحليل البصري</div>', unsafe_allow_html=True)
            
            fig = None
            if color_mode == "تخصيص يدوي":
                # التأكد من وجود عمود Color
                if "Color" not in final_df.columns:
                    final_df["Color"] = "#FF0050"
                # تعبئة القيم الفارغة بلون افتراضي
                final_df["Color"] = final_df["Color"].fillna("#FF0050")
                
                fig = px.bar(final_df, x='Views', y='Display Name', orientation='h', text='Views')
                fig.update_traces(marker_color=final_df['Color'])
            
            elif color_mode == "ثيم متدرج (Viridis)":
                fig = px.bar(final_df, x='Views', y='Display Name', orientation='h', text='Views', color='Views', color_continuous_scale='Viridis')
            
            else: # لون موحد
                fig = px.bar(final_df, x='Views', y='Display Name', orientation='h', text='Views')
                fig.update_traces(marker_color='#FF0050')

            # تنسيق احترافي للرسم (Clean UI)
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=13)
            fig.update_layout(
                height=500,
                yaxis={'title': None, 'categoryorder':'total ascending'},
                xaxis={'showgrid': False, 'showticklabels': False, 'title': None},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # --- التحميل ---
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 تحميل التقرير النهائي (Excel)", csv, "final_report.csv", "text/csv", use_container_width=True, type="primary")

    else:
        st.warning("الرجاء إضافة رابط واحد على الأقل.")
else:
    # شاشة البداية
    st.info("👈 استخدم القائمة الجانبية لإضافة روابط حملتك واضغط 'تحليل'.")
