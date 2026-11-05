import streamlit as st
import json
import io
import re
from datetime import datetime

from groq import Groq
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Presentation Studio",
    page_icon="🎞️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 0% 0%, #172554 0%, transparent 35%),
        radial-gradient(circle at 100% 100%, #581c87 0%, transparent 35%),
        #050816;
    color: white;
}

[data-testid="stSidebar"] {
    background: #0b1020;
    border-right: 1px solid #26314f;
}

.main-title {
    font-size: 52px;
    font-weight: 900;
    text-align: center;
    margin-top: 15px;

    background: linear-gradient(
        90deg,
        #22d3ee,
        #6366f1,
        #c084fc,
        #f472b6
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #aab4cc;
    font-size: 18px;
    margin-bottom: 35px;
}

.card {
    background: rgba(15, 23, 42, 0.88);
    border: 1px solid #293553;
    border-radius: 22px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.25);
}

.feature {
    background: linear-gradient(
        145deg,
        rgba(30,41,59,0.9),
        rgba(15,23,42,0.9)
    );

    border: 1px solid #293553;
    border-radius: 18px;
    padding: 22px;
    min-height: 160px;
}

.feature-icon {
    font-size: 35px;
}

.feature-title {
    font-size: 18px;
    font-weight: 700;
    margin-top: 8px;
}

.feature-text {
    color: #9ca9c5;
    font-size: 13px;
}

.section-title {
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 15px;
}

.status {
    color: #4ade80;
    font-weight: 700;
}

.small {
    color: #8f9bb5;
    font-size: 13px;
}

.slide-card {
    background: linear-gradient(
        135deg,
        #111827,
        #1e293b
    );

    border: 1px solid #334155;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 15px;
}

.slide-number {
    color: #60a5fa;
    font-weight: 800;
    font-size: 13px;
}

.slide-title {
    font-size: 25px;
    font-weight: 800;
    margin-top: 8px;
}

.slide-content {
    color: #b6c0d4;
    line-height: 1.7;
    margin-top: 10px;
}

div.stButton > button {
    width: 100%;
    min-height: 45px;
    border-radius: 12px;

    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );

    border: 1px solid #3b4a72;
    color: white;
    font-weight: 700;
}

div.stButton > button:hover {
    border-color: #22d3ee;
    box-shadow: 0 0 22px rgba(34,211,238,0.3);
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "presentation" not in st.session_state:
    st.session_state.presentation = None

if "generated" not in st.session_state:
    st.session_state.generated = False


# =========================================================
# GROQ CLIENT
# =========================================================

def get_groq_client():

    try:
        api_key = st.secrets["GROQ_API_KEY"]

        if not api_key:
            return None

        return Groq(api_key=api_key)

    except Exception:
        return None


# =========================================================
# AI GENERATION
# =========================================================

def generate_presentation(
    topic,
    description,
    slide_count,
    language,
    level,
    style
):

    client = get_groq_client()

    if client is None:
        raise Exception(
            "GROQ_API_KEY is missing. "
            "Please add it to Streamlit Secrets."
        )

    system_prompt = """
You are an expert presentation designer and educational content creator.

Create a professional PowerPoint presentation.

Return ONLY valid JSON.
Do not use Markdown.
Do not add explanations outside JSON.

The JSON must have exactly this structure:

{
  "title": "Presentation title",
  "subtitle": "Short subtitle",
  "slides": [
    {
      "title": "Slide title",
      "bullets": [
        "Bullet point 1",
        "Bullet point 2",
        "Bullet point 3",
        "Bullet point 4"
      ],
      "speaker_notes": "Short speaker notes"
    }
  ]
}

Rules:
- Make the content accurate and useful.
- Avoid repeating the same information.
- Use clear presentation language.
- Each slide should have 3 to 5 concise bullet points.
- Keep bullets short.
- Create a logical flow.
- Include introduction, main content and conclusion.
"""

    user_prompt = f"""
Create a presentation with these requirements:

Topic:
{topic}

Description:
{description}

Number of slides:
{slide_count}

Language:
{language}

Content level:
{level}

Presentation style:
{style}

Generate exactly {slide_count} slides.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.6,
        max_tokens=5000
    )

    content = response.choices[0].message.content.strip()

    # Remove accidental markdown fences
    content = re.sub(
        r"```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"```\s*$",
        "",
        content
    )

    data = json.loads(content)

    return data


# =========================================================
# POWERPOINT CREATOR
# =========================================================

def create_powerpoint(data, style):

    prs = Presentation()

    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ---------------------------------------------
    # THEME COLORS
    # ---------------------------------------------

    if style == "Professional Blue":
        background = RGBColor(8, 24, 48)
        accent = RGBColor(37, 99, 235)
        text_color = RGBColor(255, 255, 255)

    elif style == "Creative Gradient":
        background = RGBColor(45, 20, 65)
        accent = RGBColor(168, 85, 247)
        text_color = RGBColor(255, 255, 255)

    elif style == "Minimal White":
        background = RGBColor(245, 247, 250)
        accent = RGBColor(37, 99, 235)
        text_color = RGBColor(20, 25, 35)

    elif style == "Futuristic AI":
        background = RGBColor(5, 12, 30)
        accent = RGBColor(34, 211, 238)
        text_color = RGBColor(255, 255, 255)

    else:
        background = RGBColor(7, 12, 25)
        accent = RGBColor(99, 102, 241)
        text_color = RGBColor(255, 255, 255)

    # =================================================
    # TITLE SLIDE
    # =================================================

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = background

    # Accent shape
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0),
        Inches(0),
        Inches(0.18),
        Inches(7.5)
    )

    shape.fill.solid()
    shape.fill.fore_color.rgb = accent
    shape.line.fill.background()

    # Title
    textbox = slide.shapes.add_textbox(
        Inches(1.0),
        Inches(2.0),
        Inches(11),
        Inches(1.2)
    )

    tf = textbox.text_frame
    tf.clear()

    p = tf.paragraphs[0]
    p.text = data.get("title", "AI Presentation")
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = text_color

    # Subtitle
    textbox2 = slide.shapes.add_textbox(
        Inches(1.0),
        Inches(3.35),
        Inches(10.5),
        Inches(1)
    )

    tf2 = textbox2.text_frame
    tf2.clear()

    p2 = tf2.paragraphs[0]
    p2.text = data.get(
        "subtitle",
        "Created with AI Presentation Studio"
    )
    p2.font.size = Pt(20)
    p2.font.color.rgb = accent

    # =================================================
    # CONTENT SLIDES
    # =================================================

    for index, slide_data in enumerate(
        data.get("slides", [])
    ):

        slide = prs.slides.add_slide(
            prs.slide_layouts[6]
        )

        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = background

        # Top accent
        accent_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0),
            Inches(0),
            Inches(13.333),
            Inches(0.12)
        )

        accent_shape.fill.solid()
        accent_shape.fill.fore_color.rgb = accent
        accent_shape.line.fill.background()

        # Slide number
        num_box = slide.shapes.add_textbox(
            Inches(10.8),
            Inches(0.35),
            Inches(1.5),
            Inches(0.4)
        )

        num_tf = num_box.text_frame
        num_tf.clear()

        num_p = num_tf.paragraphs[0]
        num_p.text = f"{index + 1:02d}"
        num_p.alignment = PP_ALIGN.RIGHT
        num_p.font.size = Pt(16)
        num_p.font.bold = True
        num_p.font.color.rgb = accent

        # Title
        title_box = slide.shapes.add_textbox(
            Inches(0.75),
            Inches(0.65),
            Inches(10),
            Inches(0.8)
        )

        title_tf = title_box.text_frame
        title_tf.clear()

        title_p = title_tf.paragraphs[0]
        title_p.text = slide_data.get(
            "title",
            f"Slide {index + 1}"
        )

        title_p.font.size = Pt(30)
        title_p.font.bold = True
        title_p.font.color.rgb = text_color

        # Bullet area
        body_box = slide.shapes.add_textbox(
            Inches(0.9),
            Inches(1.7),
            Inches(11.4),
            Inches(4.8)
        )

        body_tf = body_box.text_frame
        body_tf.clear()
        body_tf.word_wrap = True

        bullets = slide_data.get(
            "bullets",
            []
        )

        for bullet_index, bullet in enumerate(
            bullets
        ):

            if bullet_index == 0:
                p = body_tf.paragraphs[0]
            else:
                p = body_tf.add_paragraph()

            p.text = bullet
            p.font.size = Pt(21)
            p.font.color.rgb = text_color
            p.space_after = Pt(14)
            p.level = 0

        # Footer
        footer = slide.shapes.add_textbox(
            Inches(0.75),
            Inches(6.85),
            Inches(11),
            Inches(0.3)
        )

        footer_tf = footer.text_frame
        footer_tf.clear()

        footer_p = footer_tf.paragraphs[0]
        footer_p.text = "AI Presentation Studio"
        footer_p.font.size = Pt(9)
        footer_p.font.color.rgb = RGBColor(
            130, 140, 160
        )

    # =================================================
    # SAVE TO MEMORY
    # =================================================

    output = io.BytesIO()

    prs.save(output)

    output.seek(0)

    return output


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🎞️ AI Presentation Studio")

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "✨ Create Presentation",
            "📑 My Presentation",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    if get_groq_client():

        st.markdown(
            '<p class="status">● Groq API Connected</p>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<p style="color:#f87171;font-weight:700">'
            '● Groq API Not Connected'
            '</p>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<p class="small">'
        'AI Presentation Studio v3.0'
        '</p>',
        unsafe_allow_html=True
    )


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">'
        'AI PRESENTATION STUDIO'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Create professional PowerPoint presentations using Groq AI'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("🤖 AI", "Groq")

    with c2:
        st.metric("🎞️ PPTX", "Ready")

    with c3:
        st.metric("⚡ Generation", "Fast")

    with c4:
        st.metric("🔐 API", "Secure")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">'
        '✨ Features'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("""
        <div class="feature">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">
                Groq AI
            </div>
            <div class="feature-text">
                Generate presentation content with Groq models.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class="feature">
            <div class="feature-icon">🎨</div>
            <div class="feature-title">
                Modern Design
            </div>
            <div class="feature-text">
                Professional slide layouts and multiple themes.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown("""
        <div class="feature">
            <div class="feature-icon">📥</div>
            <div class="feature-title">
                PowerPoint Export
            </div>
            <div class="feature-text">
                Download your generated presentation as PPTX.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Start Creating"):

        st.info(
            "Sidebar mein '✨ Create Presentation' select karein."
        )


# =========================================================
# CREATE PRESENTATION
# =========================================================

elif page == "✨ Create Presentation":

    st.markdown(
        '<div class="main-title">'
        'CREATE PRESENTATION'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Enter your topic and let Groq AI build your presentation'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        '📝 Presentation Details'
        '</div>',
        unsafe_allow_html=True
    )

    topic = st.text_input(
        "Presentation Topic",
        placeholder="Example: Artificial Intelligence"
    )

    description = st.text_area(
        "What should the presentation cover?",
        placeholder=(
            "Example: Explain AI, its applications, "
            "advantages, challenges and future."
        ),
        height=120
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        slide_count = st.number_input(
            "Number of Slides",
            min_value=3,
            max_value=20,
            value=8,
            step=1
        )

    with c2:

        language = st.selectbox(
            "Language",
            [
                "English",
                "Urdu",
                "Roman Urdu"
            ]
        )

    with c3:

        level = st.selectbox(
            "Content Level",
            [
                "Beginner",
                "Intermediate",
                "Professional"
            ]
        )

    style = st.selectbox(
        "🎨 Presentation Style",
        [
            "Modern Dark",
            "Professional Blue",
            "Creative Gradient",
            "Minimal White",
            "Futuristic AI"
        ]
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Generate button

    if st.button(
        "✨ Generate with Groq AI",
        type="primary"
    ):

        if not topic.strip():

            st.error(
                "Please enter a presentation topic."
            )

        else:

            try:

                with st.spinner(
                    "🤖 Groq AI is creating your presentation..."
                ):

                    presentation = generate_presentation(
                        topic=topic,
                        description=description,
                        slide_count=int(slide_count),
                        language=language,
                        level=level,
                        style=style
                    )

                    st.session_state.presentation = {
                        "data": presentation,
                        "style": style,
                        "created": datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        )
                    }

                    st.session_state.generated = True

                st.success(
                    "🎉 Presentation generated successfully!"
                )

            except json.JSONDecodeError:

                st.error(
                    "Groq returned an invalid JSON response. "
                    "Please try generating again."
                )

            except Exception as e:

                st.error(
                    f"Generation failed: {str(e)}"
                )

    # =====================================================
    # PREVIEW
    # =====================================================

    if st.session_state.generated:

        presentation = st.session_state.presentation

        data = presentation["data"]

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">'
            '👀 Presentation Preview'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="card">

                <h2>
                    🎞️ {data.get("title", topic)}
                </h2>

                <p class="small">
                    {data.get("subtitle", "")}
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        slides_data = data.get(
            "slides",
            []
        )

        for index, slide in enumerate(
            slides_data
        ):

            bullets_html = ""

            for bullet in slide.get(
                "bullets",
                []
            ):

                bullets_html += (
                    f"<li>{bullet}</li>"
                )

            st.markdown(
                f"""
                <div class="slide-card">

                    <div class="slide-number">
                        SLIDE {index + 1}
                    </div>

                    <div class="slide-title">
                        {slide.get("title", "")}
                    </div>

                    <div class="slide-content">
                        <ul>
                            {bullets_html}
                        </ul>
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        # =================================================
        # CREATE PPTX
        # =================================================

        try:

            pptx_file = create_powerpoint(
                data,
                presentation["style"]
            )

            st.download_button(
                label="📥 Download PowerPoint (.pptx)",
                data=pptx_file.getvalue(),
                file_name="AI_Presentation.pptx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "presentationml.presentation"
                )
            )

        except Exception as e:

            st.error(
                f"PowerPoint creation failed: {str(e)}"
            )

        # JSON download

        json_data = json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )

        st.download_button(
            label="📄 Download Presentation JSON",
            data=json_data,
            file_name="presentation.json",
            mime="application/json"
        )


# =========================================================
# MY PRESENTATION
# =========================================================

elif page == "📑 My Presentation":

    st.markdown(
        '<div class="main-title">'
        'MY PRESENTATION'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Your latest AI-generated presentation'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.presentation:

        st.info(
            "No presentation generated yet."
        )

    else:

        presentation = st.session_state.presentation

        data = presentation["data"]

        st.markdown(
            f"""
            <div class="card">

                <h2>
                    🎞️ {data.get("title", "Presentation")}
                </h2>

                <p>
                    {data.get("subtitle", "")}
                </p>

                <p class="small">
                    Created: {presentation["created"]}
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        for index, slide in enumerate(
            data.get("slides", [])
        ):

            with st.expander(
                f"Slide {index + 1}: "
                f"{slide.get('title', '')}"
            ):

                for bullet in slide.get(
                    "bullets",
                    []
                ):

                    st.write(
                        f"• {bullet}"
                    )

                if slide.get(
                    "speaker_notes"
                ):

                    st.caption(
                        "Speaker Notes: "
                        + slide["speaker_notes"]
                    )


# =========================================================
# SETTINGS
# =========================================================

elif page == "⚙️ Settings":

    st.markdown(
        '<div class="main-title">'
        'SETTINGS'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Configure your presentation studio'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown("### 🤖 AI Model")

    st.text_input(
        "Groq Model",
        value="llama-3.3-70b-versatile",
        disabled=True
    )

    st.markdown("### 🎨 Interface")

    st.toggle(
        "Dark Mode",
        value=True
    )

    st.toggle(
        "Animations",
        value=True
    )

    st.markdown("### 📝 Default Language")

    st.selectbox(
        "Language",
        [
            "English",
            "Urdu",
            "Roman Urdu"
        ]
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.success(
        "Groq-powered presentation generation is enabled."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<br><br>

<div style="
text-align:center;
color:#68738e;
padding:20px;
">

🎞️ AI Presentation Studio
<br>
Powered by Groq AI • Built with Streamlit

</div>
""", unsafe_allow_html=True)
