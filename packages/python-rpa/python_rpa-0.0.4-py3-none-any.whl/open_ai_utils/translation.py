"""OpenAI API를 사용하여 텍스트를 다른 언어로 번역하는 유틸리티 함수를 제공합니다."""

import os

from bs4 import BeautifulSoup
from openai import OpenAI


# OpenAI API 키 설정
openai_api_client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),  # this is also the default, it can be omitted
)


def translate(text, from_language="Korean", to_language="English"):
    """주어진 텍스트를 다른 언어로 번역합니다."""
    response = openai_api_client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": f"Translate the following {from_language} text to {to_language}, and only provide the translation result. Please preserve the HTML format. Also, ensure to properly escape HTML characters such as &, <, and > "},
            {"role": "user", "content": text}
        ],
        temperature=0,
    )

    translation = response.choices[0].message.content.strip()

    return translation


def translate_html_content(html_content):
    """주어진 HTML 컨텐츠의 모든 텍스트를 번역합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # HTML 내의 모든 텍스트 요소를 순회
    for element in soup.find_all(string=True):
        if element.strip():  # 요소가 공백이 아닌 텍스트를 포함하는지 확인
            translated_text = translate(element)
            element.replace_with(translated_text)

    return str(soup)
