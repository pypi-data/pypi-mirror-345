"""html_publisher.py: HTML 테이블을 생성하는 함수를 포함합니다."""

from bs4 import BeautifulSoup

html_escape_dict = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
}


def html_escape(text:str):
    """주어진 문자열에서 HTML 특수 문자를 변환합니다."""
    return ''.join(html_escape_dict.get(c, c) for c in text)


def html_escape_all_elements(html_content:str):
    soup = BeautifulSoup(html_content, 'html.parser')

    # HTML 내의 모든 텍스트 요소를 순회
    for element in soup.find_all(string=True):
        if element.strip():  # 요소가 공백이 아닌 텍스트를 포함하는지 확인
            escaped_element= html_escape(element)
            element.replace_with(escaped_element)

    return str(soup)


def generate_html_table(data_list: list, *link_args):
    """주어진 데이터를 HTML 테이블로 변환합니다."""
    # 예외 처리: 데이터가 비어 있다면
    if not data_list:
        return "<p>No data available</p>"

    # link_fields와 link_titles 만들기
    link_fields = link_args[::2]  # 홀수 인덱스의 값
    link_titles = link_args[1::2]  # 짝수 인덱스의 값
    link_dict = dict(zip(link_titles, link_fields))

    # HTML 테이블의 시작 부분
    html = '<table class="wrapped">\n'
    html += '  <colgroup>\n'

    # 첫 번째 데이터의 키를 사용하여 열 정의 추가
    keys = data_list[0].keys()
    for key in keys:
        if key in link_fields:
            continue

        html += '    <col class=""/>\n'  # 각 열에 대한 col 요소 생성

    html += '  </colgroup>\n'
    html += '  <tbody class="">\n'

    # 헤더 추가
    html += '    <tr class="">\n'
    for key in keys:
        if key in link_fields:
            continue

        html += f'      <th>{key}</th>\n'
    html += '    </tr>\n'

    # 데이터 행 추가
    for item in data_list:
        html += '    <tr class="">\n'
        for key in keys:
            if key in link_fields:
                continue

            value = html_escape(str(item.get(key, "")))  # 각 키에 대한 값을 가져옴

            if key in link_titles: 
                link_field = link_dict[key]
                link = html_escape(str(item.get(link_field, value)))
                html += f'      <td><p><a href="{link}">{value}</a></p></td>\n'
            else:
                html += f'      <td>{value}</td>\n'
        html += '    </tr>\n'

    html += '  </tbody>\n'
    html += '</table>'

    return html
