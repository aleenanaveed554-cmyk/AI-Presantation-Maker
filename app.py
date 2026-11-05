import streamlit as st
import json
import os
from openai import OpenAI

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

/* Main Hero */

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
    box-shadow: 0 15px 45px rgba(37, 99, 235, 0.25);
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

/* Cards */

.card {
    background: white;
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
}

/* Slide Preview */

.slide {
    background: white;
    border-radius: 18px;
    padding: 25px;
    min-height: 240px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.07);
    margin-bottom: 20px;
}

.slide-number {
    color: #2563eb;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
}

.slide-title {
    color: #111827;
    font-size: 24px;
    font-weight: 800;
    margin-top: 8px;
}

.slide-subtitle {
    color: #64748b;
    font-size: 14px;
    margin: 5px 0 15px 0;
}

.bullet {
    color: #334155;
    font-size: 14px;
    margin: 8px 0;
}

/* Buttons */

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 45px;
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
# OPENAI CLIENT
# =========================================================

def get_openai_client():

    try:
        api_key = st.secrets["OPENAI_API_KEY"]

        return OpenAI(api_key=api_key)

    except Exception:
        return None


# =========================================================
# AI PRESENTATION GENERATOR
# =========================================================

def generate_presentation(topic, number_of_slides, language, audience):

    client = get_openai_client()

    if client is None:
        st.error(
            "OPENAI_API_KEY nahi mili. "
            "Streamlit Settings → Secrets mein API key add karein."
        )
        return []

    prompt = f"""
Create a professional university-level presentation.

Topic:
{topic}

Number of slides:
{number_of_slides}

Language:
{language}

Audience:
{audience}

Create a logical presentation structure.

The presentation should include:

1. Title / introduction
2. Background
3. Main concepts
4. Important information
5. Examples
6. Applications
7. Benefits or impact
8. Challenges
9. Future perspective
10. Conclusion

Do not make every slide follow the exact same structure.

Each slide should contain:

- title
- subtitle
- 3 to 5 short bullet points
- speaker notes

Keep the content professional, accurate and easy to understand.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "slides": [
        {{
            "title": "Slide title",
            "subtitle": "Short subtitle",
            "bullets": [
                "Point 1",
                "Point 2",
                "Point 3",
                "Point 4"
            ],
            "speaker_notes": "Speaker notes"
        }}
    ]
}}
"""

    try:

        response = client.chat.completions.create(
            model=st.secrets.get(
                "OPENAI_MODEL",
                "gpt-4.1-mini"
            ),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert presentation designer "
                        "and academic content writer."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content

        data = json.loads(result)

        return data.get("slides", [])

    except Exception as e:

        st.error(f"AI generation error: {e}")

        return []


# =========================================================
# HERO SECTION
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

    st.markdown("""
### 💡 Example Topics

- Artificial Intelligence
- Climate Change
- Digital Marketing
- Cyber Security
- Machine Learning
- Renewable Energy
- Social Media
- E-Commerce
""")


# =========================================================
# TOPIC INPUT
# =========================================================

st.markdown("## 📝 Create Your Presentation")

topic = st.text_input(
    "Enter your topic",
    placeholder="Example: Artificial Intelligence in Education"
)


# =========================================================
# GENERATE BUTTON
# =========================================================

if st.button(
    "✨ Generate Presentation",
    type="primary",
    use_container_width=True
):

    if not topic.strip():

        st.warning("Please enter a presentation topic.")

    else:

        with st.spinner(
            "🤖 AI is creating your professional presentation..."
        ):

            slides = generate_presentation(
                topic,
                number_of_slides,
                language,
                audience
            )

            if slides:

                st.session_state.slides = slides
                st.session_state.generated = True

                st.success(
                    "🎉 Presentation successfully generated!"
                )


# =========================================================
# PRESENTATION EDITOR
# =========================================================

if st.session_state.generated and st.session_state.slides:

    st.divider()

    st.markdown("## 🖼️ Slide Preview")

    slides = st.session_state.slides

    # Preview in 3 columns

    cols = st.columns(3)

    for index, slide in enumerate(slides):

        with cols[index % 3]:

            bullets_html = ""

            for bullet in slide.get("bullets", []):

                bullets_html += f"""
                <div class="bullet">
                • {bullet}
                </div>
                """

            st.markdown(
                f"""
                <div class="slide">

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
    # EDIT SLIDES
    # =====================================================

    st.divider()

    st.markdown("## ✏️ Edit Your Slides")

    for i, slide in enumerate(slides):

        with st.expander(
            f"Slide {i + 1}: {slide.get('title', '')}"
        ):

            title = st.text_input(
                "Slide Title",
                value=slide.get("title", ""),
                key=f"title_{i}"
            )

            subtitle = st.text_input(
                "Subtitle",
                value=slide.get("subtitle", ""),
                key=f"subtitle_{i}"
            )

            bullets = st.text_area(
                "Bullet Points — one point per line",
                value="\n".join(
                    slide.get("bullets", [])
                ),
                height=150,
                key=f"bullets_{i}"
            )

            notes = st.text_area(
                "Speaker Notes",
                value=slide.get(
                    "speaker_notes",
                    ""
                ),
                height=120,
                key=f"notes_{i}"
            )

            slide["title"] = title
            slide["subtitle"] = subtitle

            slide["bullets"] = [
                x.strip()
                for x in bullets.split("\n")
                if x.strip()
            ]

            slide["speaker_notes"] = notes


    # =====================================================
    # ADD SLIDE
    # =====================================================

    if st.button("➕ Add New Slide"):

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


    # =====================================================
    # EXPORT SECTION
    # =====================================================

    st.divider()

    st.markdown("## 📥 Download")

    st.info(
        "PowerPoint aur PDF export ko hum next files mein connect karenge."
    )

    col1, col2 = st.columns(2)

    with col1:

        presentation_json = json.dumps(
            slides,
            indent=2,
            ensure_ascii=False
        )

        st.download_button(
            "⬇️ Download Presentation Data",
            data=presentation_json,
            file_name="presentation.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:

        st.download_button(
            "⬇️ Download Content",
            data="\n\n".join(
                [
                    f"{i + 1}. {s['title']}\n"
                    + "\n".join(
                        f"• {b}"
                        for b in s["bullets"]
                    )
                    for i, s in enumerate(slides)
                ]
            ),
            file_name="presentation.txt",
            mime="text/plain",
            use_container_width=True
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
<div style="text-align:center;color:#64748b;padding:15px;">
AI Presentation Maker • Built with Python + Streamlit + AI
</div>
""",
    unsafe_allow_html=True
)
