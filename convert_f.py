import os
from bs4 import BeautifulSoup
from weasyprint import HTML


def update_css_style(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    style_tags = soup.find_all("style")
    updated = False

    # CSS 스타일 업데이트
    new_border = "1px solid #dfe2e5"  # 예를 들어 변경할 새로운 border 값
    new_padding = "1px 1px"  # 예를 들어 변경할 새로운 padding 값

    for style in style_tags:
        css_text = style.get_text()
        # CSS 선택자를 정확하게 찾기 위한 패턴 정의
        search_patterns = [
            "#setText table td, #preview-content table td,",
            "#setText table th, #preview-content table th",
        ]
        if all(pattern in css_text for pattern in search_patterns):
            # 새로운 스타일로 교체
            new_css_text = css_text.replace(
                "border: 1px solid #dfe2e5;", f"border: {new_border};"
            )
            new_css_text = new_css_text.replace(
                "padding: 6px 13px;", f"padding: {new_padding};"
            )
            style.string.replace_with(new_css_text)
            updated = True
            break

    if updated:
        return str(soup)
    else:
        return None


def convert_to_pdf(html_content, file_name):
    pdf_path = "./pdf"
    HTML(string=html_content).write_pdf(os.path.join(pdf_path, file_name + ".pdf"))
