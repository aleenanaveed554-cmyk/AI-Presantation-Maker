import json
import streamlit as st
from openai import OpenAI


def get_client():
    try:
        api_key = st.secrets["OPENAI_API_KEY"]

        return OpenAI(
            api_key=api_key
        )

    except Exception:
        st.error(
            "OPENAI_API_KEY nahi mili. "
            "Streamlit Secrets mein API key add karein."
        )

        return None


def generate_presentation(
    topic,
    number_of_slides,
    language,
    audience
):

    client = get_client()

    if client is None:
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

Create a logical and engaging presentation.

Each slide must contain:

- title
- subtitle
- 3 to 5 concise bullet points
- speaker notes

The presentation should cover:

Introduction
Background
Main concepts
Important information
Examples
Applications
Benefits
Challenges
Future perspective
Conclusion

Keep the content professional, clear,
accurate and easy to understand.

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
                        "You are an expert academic "
                        "presentation designer."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7,

            response_format={
                "type": "json_object"
            }
        )

        result = response.choices[0].message.content

        data = json.loads(result)

        slides = data.get("slides", [])

        return slides

    except Exception as e:

        st.error(
            f"AI presentation generate nahi ho saki: {e}"
        )

        return []
