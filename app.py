import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import time

# --- 1) Page setup + CSS ---
st.set_page_config(page_title="TikTok Campaign Pro Dashboard", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; }

    .css-1r6slb0, .stDataFrame, .plotly-graph-div, div[data-testid="stDataEditor"] {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .section-header {
        font-size: 24px; font-weight: 700; color: #1a1a1a;
        margin-bottom: 15px; display: flex; align-items: center;
    }

    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
        border-radius: 15px; padding: 20px; text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03); border: 1px solid #eee;
    }
    .kpi-metric { font-size: 32px; font-weight: 800; color: #E91E63; }
    .kpi-label { font-size: 14px; color: #666; margin-top: 5px; }

    /* Print */
    @media print {
        section[data-testid="stSidebar"] { display: none !important; }
        .stButton, div[data-testid="stStatusWidget"], header { display: none !important; }
        div[data-testid="stDecoration"] { display: none !important; }

        .stApp { background-color: white !important; }

        .css-1r6slb0, .stDataFrame, .plotly-graph-div {
            box-shadow: none !important;
            border: 1px solid #ddd !important;
            margin-bottom: 10px !important;
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }

        @page { size: A4; margin: 10mm; }
        body { font-size: 12pt !important; }

        a { text-decoration: none !important; color: black !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- 2) Data fetch ---
@st.cache_data(show_spinner=False)
def get_tiktok_data(urls):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }

    data = []

    loading_container = st.empty()
    with loading_container.container():
        st.markdown("### 🔄 جاري سحب البيانات...")
        progress_bar = st.progress(0)
        status_text = st.empty()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            progress_bar.progress((i + 1) / len(urls))
            status_text.info(f"تحليل الرابط {i+1} من {len(urls)}...")

            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    display_name = info.get("uploader", info.get("uploader_id", "Unknown"))
                    likes = info.get("like_count", 0) or 0
                    shares = info.get("repost_count", 0) or 0
                    views = info.get("view_count", 0) or 0

                    data.append({
                        "Title": info.get("title", "No Title"),
                        "Display Name": display_name,
                        "Username": info.get("uploader_id", "Unknown"),
                        "Views": int(views),
                        "Likes": int(likes),
                        "Shares": int(shares),
                        "Link": url
                    })
            except Exception:
                pass

            time.sleep(0.1)

    loading_container.empty()
    return data

# --- 3) Sidebar ---
with st.sidebar:
    st.title("⚙️ إعدادات الداشبورد")
    st.markdown("---")

    st.markdown("### 1️⃣ روابط الحملة")
    raw_urls = st.text_area("الروابط:", height=150, placeholder="https://www.tiktok.com/...")

    st.markdown("### 2️⃣ تخصيص العرض")
    label_choice = st.radio("تسمية البارات بـ:", ("اسم الحساب", "عنوان الفيديو"))

    st.markdown("### 3️⃣ الثيم")
    color_mode = st.selectbox("نمط التلوين:", ("تدرج احترافي", "تخصيص يدوي", "لون موحد"))

    selected_theme = "Viridis"
    selected_color = "#FF0050"

    if color_mode == "تدرج احترافي":
        selected_theme = st.selectbox("اختر التدرج:", ["Sunsetdark", "Agsunset", "Tealgrn", "Viridis"])
    elif color_mode == "لون موحد":
        selected_color = st.color_picker("اختر اللون:", "#FF0050")

    st.markdown("---")
    analyze_btn = st.button("🚀 إنشاء التقرير", type="primary", use_container_width=True)
    st.info("💡 **لطباعة التقرير:** اضغط `Ctrl + P`.")

# --- 4) Main content ---
st.markdown("""
<div style="background: linear-gradient(90deg, #000000, #2c3e50); padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px; text-align: center;">
    <h1 style='margin:0; font-size: 36px;'>🚀 TikTok Campaign Pro Report</h1>
    <p style='font-size: 16px; opacity: 0.8;'>تقرير تحليلي شامل للأداء</p>
</div>
""", unsafe_allow_html=True)

if analyze_btn and raw_urls:
    urls_list = [line.strip() for line in raw_urls.split("\n") if line.strip()]

    if urls_list:
        data_result = get_tiktok_data(urls_list)

        if data_result:
            df = pd.DataFrame(data_result)
            df_sorted = df.sort_values(by="Views", ascending=True).copy()

            # --- KPIs + total videos ---
            st.markdown('<div class="section-header">📊 ملخص الأداء (Overview)</div>', unsafe_allow_html=True)
            k1, k2, k3, k4, k5 = st.columns(5)

            k1.markdown(f"""<div class="kpi-card"><div class="kpi-metric">🔥 {df['Views'].sum():,.0f}</div><div class="kpi-label">المشاهدات</div></div>""", unsafe_allow_html=True)
            k2.markdown(f"""<div class="kpi-card"><div class="kpi-metric">❤️ {df['Likes'].sum():,.0f}</div><div class="kpi-label">اللايكات</div></div>""", unsafe_allow_html=True)
            k3.markdown(f"""<div class="kpi-card"><div class="kpi-metric">↗️ {df['Shares'].sum():,.0f}</div><div class="kpi-label">المشاركات</div></div>""", unsafe_allow_html=True)
            k4.markdown(f"""<div class="kpi-card"><div class="kpi-metric">📈 {df['Views'].mean():,.0f}</div><div class="kpi-label">متوسط/فيديو</div></div>""", unsafe_allow_html=True)
            k5.markdown(f"""<div class="kpi-card"><div class="kpi-metric">🎬 {len(df):,.0f}</div><div class="kpi-label">عدد الفيديوهات</div></div>""", unsafe_allow_html=True)

            st.markdown("---")

            # --- Chart ---
            st.markdown('<div class="section-header">📈 تحليل الفيديوهات (Performance Chart)</div>', unsafe_allow_html=True)

            y_col_name = "Display Name" if label_choice == "اسم الحساب" else "Title"

            # clickable label for viewing; won't be exported
            df_sorted["Linked_Label"] = df_sorted.apply(
                lambda x: f'<a href="{x["Link"]}" target="_blank" style="color: #2980b9; text-decoration: none; font-weight: bold;">{x[y_col_name]}</a>',
                axis=1
            )

            final_fig = None
            if color_mode == "تخصيص يدوي":
                st.info("⚠️ التخصيص اليدوي قد يلغي خاصية الروابط في الرسم.")
                edit_df = df.copy().sort_values(by="Views", ascending=False)
                if "Color" not in edit_df.columns:
                    edit_df["Color"] = "Gray"

                edited_data = st.data_editor(
                    edit_df[[y_col_name, "Views", "Color"]],
                    column_config={
                        "Color": st.column_config.SelectboxColumn("اللون", options=["Red", "Blue", "Green", "#FF0050", "Gray"], required=True),
                        "Views": st.column_config.NumberColumn("المشاهدات", disabled=True),
                    },
                    use_container_width=True, hide_index=True
                )
                final_fig = px.bar(edited_data, x="Views", y=y_col_name, orientation="h", text="Views")
                final_fig.update_traces(marker_color=edited_data["Color"])

            elif color_mode == "لون موحد":
                final_fig = px.bar(df_sorted, x="Views", y="Linked_Label", orientation="h", text="Views")
                final_fig.update_traces(marker_color=selected_color)

            else:
                final_fig = px.bar(
                    df_sorted,
                    x="Views",
                    y="Linked_Label",
                    orientation="h",
                    text="Views",
                    color="Views",
                    color_continuous_scale=selected_theme
                )

            if final_fig:
                final_fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
                final_fig.update_layout(
                    height=max(500, len(df) * 45),
                    yaxis={"title": None, "tickfont": {"size": 13}},
                    xaxis={"showgrid": False, "showticklabels": False},
                    margin=dict(l=20, r=20, t=20, b=20),
                    font=dict(family="Arial", size=12)
                )
                st.plotly_chart(final_fig, use_container_width=True)

            # --- Table + Export (clean) ---
            st.markdown("---")
            st.markdown('<div class="section-header">💾 البيانات التفصيلية</div>', unsafe_allow_html=True)

            st.dataframe(df, use_container_width=True, hide_index=True)

            # Export clean CSV (Excel-friendly for Arabic)
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="⬇️ تحميل ملف CSV (يفتح في Excel)",
                data=csv,
                file_name="tiktok_campaign_report.csv",
                mime="text/csv",
                type="primary"
            )

else:
    if not raw_urls:
        st.info("👋 ابدأ بإضافة الروابط من القائمة الجانبية.")
