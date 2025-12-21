import streamlit as st
import yt_dlp
import pandas as pd
import plotly.express as px
import plotly.io as pio
import time
from io import BytesIO
import math

# =======================
# Force Plotly -> Kaleido
# =======================
try:
    pio.kaleido.scope.default_format = "png"
    pio.kaleido.scope.default_scale = 2
except Exception:
    pass

# =======================
# Page config + CSS
# =======================
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
        .page-break { page-break-after: always; break-after: page; }
    }
</style>
""", unsafe_allow_html=True)

# =======================
# Helpers
# =======================
def safe_int(v, default=0) -> int:
    try:
        if v is None:
            return default
        return int(v)
    except Exception:
        return default

def fmt_followers(v) -> str:
    if v is None:
        return "N/A"
    v = safe_int(v, 0)
    if v <= 0:
        return "N/A"
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.1f}K"
    return f"{v}"

def pick_followers(info: dict):
    candidates = ["channel_follower_count", "uploader_follower_count", "follower_count", "followers"]
    for k in candidates:
        v = info.get(k)
        try:
            vi = int(v)
            if vi > 0:
                return vi
        except Exception:
            pass

    for parent_key in ("channel", "uploader", "author"):
        parent = info.get(parent_key)
        if isinstance(parent, dict):
            for k in ("follower_count", "followers", "channel_follower_count"):
                v = parent.get(k)
                try:
                    vi = int(v)
                    if vi > 0:
                        return vi
                except Exception:
                    pass
    return None

def chunk_df(df: pd.DataFrame, chunk_size: int):
    for start in range(0, len(df), chunk_size):
        yield df.iloc[start:start + chunk_size], start // chunk_size + 1

def make_excel_or_csv(df_export: pd.DataFrame):
    try:
        import openpyxl  # noqa: F401
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Report")
        output.seek(0)
        return ("excel", output.getvalue(), "tiktok_campaign_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception:
        csv = df_export.to_csv(index=False).encode("utf-8-sig")
        return ("csv", csv, "tiktok_campaign_report.csv", "text/csv")

def fig_to_png_bytes(fig) -> tuple[bytes | None, str | None]:
    """
    Returns (png_bytes, error_message). If Chrome missing, returns None with error msg.
    """
    try:
        png = fig.to_image(format="png", scale=2)
        return png, None
    except Exception as e:
        return None, str(e)

# =======================
# Data fetch
# =======================
@st.cache_data(show_spinner=False)
def get_tiktok_data(urls):
    ydl_opts = {"quiet": True, "skip_download": True, "no_warnings": True, "ignoreerrors": True}

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
                    data.append({
                        "Title": info.get("title", "No Title"),
                        "Display Name": info.get("uploader", info.get("uploader_id", "Unknown")),
                        "Username": info.get("uploader_id", "Unknown"),
                        "Views": safe_int(info.get("view_count"), 0),
                        "Likes": safe_int(info.get("like_count"), 0),
                        "Shares": safe_int(info.get("repost_count"), 0),
                        "Followers": pick_followers(info),
                        "Link": url
                    })
            except Exception:
                pass

            time.sleep(0.1)

    loading_container.empty()
    return data

# =======================
# Sidebar
# =======================
with st.sidebar:
    st.title("⚙️ إعدادات الداشبورد")
    st.markdown("---")

    st.markdown("### 1️⃣ روابط الحملة")
    raw_urls = st.text_area("الروابط:", height=150, placeholder="https://www.tiktok.com/...")

    st.markdown("### 2️⃣ تخصيص العرض")
    label_choice = st.radio("تسمية البارات بـ:", ("اسم الحساب", "عنوان الفيديو"))

    st.markdown("### 3️⃣ الثيم")
    color_mode = st.selectbox("نمط التلوين:", ("تدرج احترافي", "تخصيص يدوي", "لون موحد"))

    st.markdown("### 4️⃣ وضع الطباعة (PDF)")
    print_mode = st.toggle(
        "🖨️ Print Mode (أفضل للطباعة PDF)",
        value=True,
        help="يستخدم صور PNG بدل الرسم التفاعلي (لكن يحتاج Chrome/Chromium داخل السيرفر)."
    )

    selected_theme = "Viridis"
    selected_color = "#FF0050"

    if color_mode == "تدرج احترافي":
        selected_theme = st.selectbox("اختر التدرج:", ["Sunsetdark", "Agsunset", "Tealgrn", "Viridis"])
    elif color_mode == "لون موحد":
        selected_color = st.color_picker("اختر اللون:", "#FF0050")

    st.markdown("---")
    analyze_btn = st.button("🚀 إنشاء التقرير", type="primary", use_container_width=True)
    st.info("💡 للطباعة: Ctrl + P ثم Save as PDF. (مع Print Mode النتائج أفضل إذا Chrome موجود)")

# =======================
# Main header
# =======================
st.markdown("""
<div style="background: linear-gradient(90deg, #000000, #2c3e50); padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px; text-align: center;">
    <h1 style='margin:0; font-size: 36px;'>🚀 TikTok Campaign Pro Report</h1>
    <p style='font-size: 16px; opacity: 0.8;'>تقرير تحليلي شامل للأداء</p>
</div>
""", unsafe_allow_html=True)

# =======================
# Run analysis
# =======================
if analyze_btn and raw_urls:
    urls_list = [line.strip() for line in raw_urls.split("\n") if line.strip()]

    if not urls_list:
        st.warning("⚠️ لم يتم العثور على روابط صالحة.")
    else:
        data_result = get_tiktok_data(urls_list)

        if not data_result:
            st.error("لم يتم سحب بيانات من الروابط.")
        else:
            df = pd.DataFrame(data_result)
            df_sorted = df.sort_values(by="Views", ascending=True).copy()

            # KPIs
            st.markdown('<div class="section-header">📊 ملخص الأداء (Overview)</div>', unsafe_allow_html=True)
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.markdown(f"""<div class="kpi-card"><div class="kpi-metric">🔥 {df['Views'].sum():,.0f}</div><div class="kpi-label">المشاهدات</div></div>""", unsafe_allow_html=True)
            k2.markdown(f"""<div class="kpi-card"><div class="kpi-metric">❤️ {df['Likes'].sum():,.0f}</div><div class="kpi-label">اللايكات</div></div>""", unsafe_allow_html=True)
            k3.markdown(f"""<div class="kpi-card"><div class="kpi-metric">↗️ {df['Shares'].sum():,.0f}</div><div class="kpi-label">المشاركات</div></div>""", unsafe_allow_html=True)
            k4.markdown(f"""<div class="kpi-card"><div class="kpi-metric">📈 {df['Views'].mean():,.0f}</div><div class="kpi-label">متوسط/فيديو</div></div>""", unsafe_allow_html=True)
            k5.markdown(f"""<div class="kpi-card"><div class="kpi-metric">🎬 {len(df):,.0f}</div><div class="kpi-label">عدد الفيديوهات</div></div>""", unsafe_allow_html=True)
            st.markdown("---")

            # Labels
            st.markdown('<div class="section-header">📈 تحليل الفيديوهات (Performance Chart)</div>', unsafe_allow_html=True)

            base_label_col = "Display Name" if label_choice == "اسم الحساب" else "Title"
            df_sorted["FollowersFmt"] = df_sorted["Followers"].apply(fmt_followers)
            df_sorted["LabelText"] = df_sorted.apply(
                lambda x: f"{x[base_label_col]}  •  👥 {x['FollowersFmt']}",
                axis=1
            )
            df_sorted["Linked_Label"] = df_sorted.apply(
                lambda x: (
                    f'<a href="{x["Link"]}" target="_blank" '
                    f'style="color: #2980b9; text-decoration: none; font-weight: bold;">'
                    f'{x["LabelText"]}</a>'
                ),
                axis=1
            )

            # Chunk charts
            CHUNK_SIZE = 20
            total_chunks = math.ceil(len(df_sorted) / CHUNK_SIZE)

            def build_fig(dfx: pd.DataFrame):
                if color_mode == "لون موحد":
                    fig = px.bar(dfx, x="Views", y="Linked_Label", orientation="h", text="Views")
                    fig.update_traces(marker_color=selected_color)
                elif color_mode == "تخصيص يدوي":
                    # For print mode, manual editor is annoying; keep it simple:
                    fig = px.bar(dfx, x="Views", y="Linked_Label", orientation="h", text="Views")
                else:
                    fig = px.bar(
                        dfx, x="Views", y="Linked_Label", orientation="h", text="Views",
                        color="Views", color_continuous_scale=selected_theme
                    )

                fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
                fig.update_layout(
                    height=max(650, len(dfx) * 55),
                    yaxis={"title": None, "tickfont": {"size": 13}},
                    xaxis={"showgrid": False, "showticklabels": False},
                    margin=dict(l=20, r=20, t=20, b=20),
                    font=dict(family="Arial", size=12),
                )
                return fig

            chrome_missing_warned = False

            for chunk, idx in chunk_df(df_sorted, CHUNK_SIZE):
                fig = build_fig(chunk)

                if print_mode:
                    png, err = fig_to_png_bytes(fig)
                    if png is None:
                        # Chrome missing -> fallback to table so printing still works across pages
                        if (not chrome_missing_warned) and err:
                            chrome_missing_warned = True
                            st.error(
                                "❌ Print Mode يحتاج Chrome/Chromium داخل السيرفر.\n\n"
                                "✅ إذا على Streamlit Cloud: أنشئ ملف packages.txt وضع فيه:\n"
                                "chromium\nchromium-driver\n\n"
                                "ثم اعمل Reboot.\n\n"
                                f"تفاصيل الخطأ: {err}"
                            )
                        st.dataframe(
                            chunk.sort_values("Views", ascending=False)[
                                ["LabelText", "Views", "Likes", "Shares", "Followers", "Link"]
                            ],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.image(png, use_container_width=True)
                else:
                    st.plotly_chart(fig, use_container_width=True)

                if idx < total_chunks:
                    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

            # Table + Export
            st.markdown("---")
            st.markdown('<div class="section-header">💾 البيانات التفصيلية</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

            df_export = df.copy()
            kind, data_bytes, fname, mime = make_excel_or_csv(df_export)

            st.download_button(
                label="⬇️ تحميل ملف Excel (.xlsx)" if kind == "excel" else "⬇️ تحميل CSV (بديل لأن Excel غير متاح)",
                data=data_bytes,
                file_name=fname,
                mime=mime,
                type="primary"
            )

            missing_followers = df_export["Followers"].isna().sum()
            if missing_followers > 0:
                st.warning(f"⚠️ عدد المتابعين غير متاح عبر yt_dlp لـ {missing_followers} روابط، لذلك يظهر كـ N/A.")

else:
    if not raw_urls:
        st.info("👋 ابدأ بإضافة الروابط من القائمة الجانبية.")
