import streamlit as st
from ai_generator import generate_presentation
from presentation_builder import build_pptx, build_pdf


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Presentation Maker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #f5f7ff 0%, #eef4ff 100%);
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* HERO */

.hero {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #1d4ed8 50%,
        #2563eb 100%
    );

    padding: 45px;
    border-radius: 25px;
    color: white;

    margin-bottom: 30px;

    box-shadow:
        0 15px 45px rgba(37, 99, 235, 0.25);
}

.hero-badge {
    display: inline-block;

    background: rgba(255,255,255,0.15);

    border: 1px solid rgba(255,255,255,0.25);

    padding: 7px 14px;

    border-radius: 50px;

    font-size: 12px;

    font-weight: 700;

    letter-spacing: 2px;
}

.hero h1 {
    font-size: 48px;
    margin: 15px 0 8px 0;
}

.hero p {
    font-size: 18px;
    opacity: 0.9;
}


/* SLIDE PREVIEW */

.slide-card {
    background: white;

    border-radius: 18px;

    padding: 22px;

    min-height: 250px;

    border: 1px solid #e5e7eb;

    box-shadow:
        0 8px 25px rgba(15, 23, 42, 0.07);

    margin-bottom: 20px;
}

.slide-number {
    color: #2563eb;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 2px;
}

.slide-title {
    color: #111827;

    font-size: 22px;

    font-weight: 800;

    margin-top: 8px;
}

.slide-subtitle {
    color: #64748b;

    font-size: 13px;

    margin: 5px 0 15px 0;
}

.slide-bullet {
    color: #334155;

    font-size: 13px;

    margin: 7px 0;
}


/* BUTTONS */

.stButton > button {
    border-radius: 12px;

    font-weight: 700;

    min-height: 45px;
}


/* DOWNLOAD BUTTONS */

.stDownloadButton > button {
    border-radius: 12px;

    font-weight: 700;

    min-height: 48px;
}


/* INFO BOX */

.info-box {
    background: white;

    padding: 20px;

    border-radius: 18px;

    border: 1px solid #e5e7eb;

    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "slides" not in st.session_state:
    st.session_state.slides = []

if "generated" not in st.session_state:
    st.session_state.generated = False


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero">

    <div class="hero-badge">
        AI PRESENTATION STUDIO
    </div>

    <h1>
        🎓 AI Presentation Maker
    </h1>

    <p>
        Turn any topic into a professional university-level presentation.
    </p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚙️ Presentation Settings")

    language = st.selectbox(
        "🌐 Language",
        [
            "English",
            "Urdu",
            "Roman Urdu"
        ]
    )

    audience = st.selectbox(
        "👥 Audience",
        [
            "University Students",
            "School Students",
            "Teachers",
            "Business Professionals",
            "General Audience"
        ]
    )

    number_of_slides = st.slider(
        "📑 Number of Slides",
        min_value=4,
        max_value=15,
        value=8
    )

    theme = st.selectbox(
        "🎨 Design Theme",
        [
            "Modern Blue",
            "Elegant Purple",
            "Professional Green",
            "Minimal Dark"
        ]
    )

    st.divider()

    st.markdown("### 💡 Example Topics")

    st.markdown("""
    • Artificial Intelligence

    • Climate Change

    • Digital Marketing

    • Cyber Security

    • Machine Learning

    • Renewable Energy

    • Social Media

    • E-Commerce
    """)


# =========================================================
# TOPIC
# =========================================================

st.markdown("## 📝 Create Your Presentation")

topic = st.text_input(
    "Enter your presentation topic",
    placeholder="Example: Artificial Intelligence in Education"
)


# =========================================================
# GENERATE
# =========================================================

if st.button(
    "✨ Generate Presentation",
    type="primary",
    use_container_width=True
):

    if not topic.strip():

        st.warning(
            "⚠️ Please enter a presentation topic first."
        )

    else:

        with st.spinner(
            "🤖 AI is creating your presentation..."
        ):

            slides = generate_presentation(
                topic=topic,
                number_of_slides=number_of_slides,
                language=language,
                audience=audience
            )

            if slides:

                st.session_state.slides = slides

                st.session_state.generated = True

                st.success(
                    "🎉 Presentation generated successfully!"
                )


# =========================================================
# PRESENTATION
# =========================================================

if (
    st.session_state.generated
    and st.session_state.slides
):

    slides = st.session_state.slides

    st.divider()

    # =====================================================
    # PREVIEW
    # =====================================================

    st.markdown("## 🖼️ Slide Preview")

    preview_columns = st.columns(3)

    for index, slide in enumerate(slides):

        with preview_columns[index % 3]:

            bullets_html = ""

            for bullet in slide.get(
                "bullets",
                []
            ):

                bullets_html += f"""
                <div class="slide-bullet">
                    • {bullet}
                </div>
                """

            st.markdown(
                f"""
                <div class="slide-card">

                    <div class="slide-number">
                        SLIDE {index + 1:02d}
                    </div>

                    <div class="slide-title">
                        {slide.get("title", "")}
                    </div>

                    <div class="slide-subtitle">
                        {slide.get("subtitle", "")}
                    </div>

                    {bullets_html}

                </div>
                """,
                unsafe_allow_html=True
            )


    # =====================================================
    # EDITOR
    # =====================================================

    st.divider()

    st.markdown("## ✏️ Edit Slides")

    st.caption(
        "Aap har slide ka title, subtitle, bullet points "
        "aur speaker notes edit kar sakti hain."
    )

    for i, slide in enumerate(slides):

        with st.expander(
            f"Slide {i + 1} — {slide.get('title', 'Untitled')}"
        ):

            new_title = st.text_input(
                "Slide Title",
                value=slide.get(
                    "title",
                    ""
                ),
                key=f"title_{i}"
            )

            new_subtitle = st.text_input(
                "Subtitle",
                value=slide.get(
                    "subtitle",
                    ""
                ),
                key=f"subtitle_{i}"
            )

            new_bullets = st.text_area(
                "Bullet Points — one point per line",
                value="\n".join(
                    slide.get(
                        "bullets",
                        []
                    )
                ),
                height=140,
                key=f"bullets_{i}"
            )

            new_notes = st.text_area(
                "Speaker Notes",
                value=slide.get(
                    "speaker_notes",
                    ""
                ),
                height=120,
                key=f"notes_{i}"
            )

            slide["title"] = new_title

            slide["subtitle"] = new_subtitle

            slide["bullets"] = [
                item.strip()
                for item in new_bullets.splitlines()
                if item.strip()
            ]

            slide["speaker_notes"] = new_notes


    # =====================================================
    # ADD / DELETE SLIDES
    # =====================================================

    st.markdown("### 🛠️ Slide Management")

    add_col, delete_col = st.columns(2)

    with add_col:

        if st.button(
            "➕ Add New Slide",
            use_container_width=True
        ):

            slides.append(
                {
                    "title": "New Slide",
                    "subtitle": "Add your subtitle",
                    "bullets": [
                        "Add your first point",
                        "Add your second point",
                        "Add your third point"
                    ],
                    "speaker_notes": ""
                }
            )

            st.rerun()


    with delete_col:

        if len(slides) > 1:

            if st.button(
                "🗑️ Delete Last Slide",
                use_container_width=True
            ):

                slides.pop()

                st.rerun()


    # =====================================================
    # EXPORT
    # =====================================================

    st.divider()

    st.markdown("## 📥 Download Your Presentation")

    st.markdown(
        """
        <div class="info-box">
        Your edited presentation can be exported as a professional
        PowerPoint file or PDF file.
        </div>
        """,
        unsafe_allow_html=True
    )

    export_col1, export_col2 = st.columns(2)


    # =====================================================
    # POWERPOINT
    # =====================================================

    with export_col1:

        try:

            pptx_file = build_pptx(
                slides=slides,
                topic=topic,
                theme=theme
            )

            st.download_button(
                label="📊 Download PowerPoint",
                data=pptx_file,
                file_name="AI_Presentation.pptx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "presentationml.presentation"
                ),
                use_container_width=True
            )

        except Exception as error:

            st.error(
                f"PowerPoint export error: {error}"
            )


    # =====================================================
    # PDF
    # =====================================================

    with export_col2:

        try:

            pdf_file = build_pdf(
                slides=slides,
                topic=topic,
                theme=theme
            )

            st.download_button(
                label="📄 Download PDF",
                data=pdf_file,
                file_name="AI_Presentation.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as error:

            st.error(
                f"PDF export error: {error}"
            )


    # =====================================================
    # JSON BACKUP
    # =====================================================

    st.markdown("### 💾 Presentation Backup")

    st.download_button(
        label="⬇️ Download Presentation JSON",
        data=str(slides),
        file_name="presentation_backup.json",
        mime="application/json"
    )


# =========================================================
# EMPTY STATE
# =========================================================

else:

    st.markdown("""
    <div class="info-box">

    ### 🚀 Ready to create?

    Enter any topic above and click
    <b>Generate Presentation</b>.

    AI will create the slide content automatically,
    then you can edit the slides and download them
    as PowerPoint or PDF.

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        padding:15px;
        font-size:13px;
    ">

        🎓 AI Presentation Maker
        <br>
        Built with Python • Streamlit • OpenAI

    </div>
    """,
    unsafe_allow_html=True
)
