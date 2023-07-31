from docx import Document
from bs4 import BeautifulSoup
from html2json.script import convert
import json
from docxtpl import DocxTemplate

def is_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return bool(soup.find())

def check_styles():
    docTeste = Document("template.docx")
    styles = docTeste.styles

    # Imprime o nome de todos os estilos disponíveis
    for style in styles:
        print(style.name)

def data_table(data):
    table_data = data['values'][0]['values']

    # Cria uma matriz vazia para armazenar os objetos de célula
    matrix = []

    # Percorre as linhas da tabela e extrai os valores das células
    for row in table_data:
        row_values = []
        for cell in row['values']:
            cell_text = cell['values'][0]
            cell_style = cell['attributes'].get('style', None)
            cell_obj = {'text': cell_text, 'style': cell_style}
            row_values.append(cell_text)
        matrix.append(row_values)

    return matrix

def data_list(data):
    list = data['values']

    # Cria uma matriz vazia para armazenar os objetos de célula
    arr = []

    # Percorre as linhas da tabela e extrai os valores das células
    for item in list:
        arr.append(item["values"])
    print(arr)
    return arr

def render_values(paragraph, item, bold=False, italic=False, underline=False):
    for value in item:
        run = paragraph.add_run()
        run.italic = italic
        run.bold = bold
        run.underline = underline
        if isinstance(value, str):
            run.add_text(value)
        elif value["tag_name"] == "img":
            run.add_picture('TCC Control.png')
        elif value["tag_name"] == "strong":
            run.bold = True
            render_values(paragraph, value["values"], bold=run.bold, italic=run.italic, underline=run.underline)
        elif value["tag_name"] == "em":
            run.italic = True
            render_values(paragraph, value["values"], bold=run.bold, italic=run.italic, underline=run.underline)
        elif value["tag_name"] == "span":
            run.underline = True
            render_values(paragraph, value["values"], bold=run.bold, italic=run.italic, underline=run.underline)

def get_html_context(doc, items, sections):
    subDocument = doc.new_subdoc()

    for key in items["keys"]:
        if key["tag_name"] == "h1":
            paragraph = subDocument.add_heading(level=1)
            sections.append(key)
        elif key["tag_name"] == "h2":
            subDocument.add_paragraph()
            paragraph = subDocument.add_heading(level=2)
            sections.append(key)
        elif key["tag_name"] == "h3":
            subDocument.add_paragraph()
            paragraph = subDocument.add_heading(level=3)
            sections.append(key)
        elif key["tag_name"] == "p":
            paragraph = subDocument.add_paragraph()

        if key["tag_name"] == "ul":
            for li in key["values"]:
                p = subDocument.add_paragraph("Teste", style="List Paragraph")
                render_values(p, li["values"])
        elif key["tag_name"] == "table":
            data = data_table(key)
            table = doc.add_table(rows=1, cols=3, style="Normal Table")
            hdr_cells = table.rows[0].cells
            for row_index, row in enumerate(data):
                if row_index == 0:
                    for index, hdr_text in enumerate(data[row_index]):
                        hdr_cells[index].text = hdr_text
                else:
                    row_cells = table.add_row().cells
                    for index, text in enumerate(data[row_index]):
                        row_cells[index].text = text
        else:
            render_values(paragraph, key["values"])
    return subDocument

def json2docx(data):
    doc = DocxTemplate("template.docx")
    context = {}
    sections = []

    for field in data["fields"]:
        key = field["key"]
        value = field["value"]

        if is_html(value):
            json_string = convert(value)
            items = json.loads(json_string)
            context.update({key: get_html_context(doc, items, sections)})
        else:
            context[key] = value

    print(sections)
    doc.render(context)

    doc.save("documento_final.docx")


if __name__ == '__main__':
    data = {
        "fields": [
            {
                "key": "titulo",
                "value": "TCC CONTROL: UM SISTEMA PARA GERENCIAMENTO DE TCC",
            },
            {
                "key": "coordenador",
                "value": "Lucas"
            },
            {
                "key": "aluno",
                "value": "Lucas"
            },
            {
                "key": "orientador",
                "value": "Felipe Pereira Perez"
            },
            {
                "key": "content",
                "value": """
                <h1>INTRODU&Ccedil;&Atilde;O</h1>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quam pellentesque nec nam aliquam sem et tortor consequat. Amet mauris commodo quis imperdiet. Egestas egestas fringilla phasellus faucibus scelerisque eleifend donec pretium. Auctor elit sed vulputate mi sit. Semper viverra nam libero justo. Auctor elit sed vulputate mi. At ultrices mi tempus imperdiet nulla malesuada. Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget. Condimentum lacinia quis vel eros donec ac odio tempor. Ac placerat vestibulum lectus mauris ultrices eros. Enim praesent elementum facilisis leo. Enim nulla aliquet porttitor lacus. Auctor elit sed vulputate mi sit amet mauris. Volutpat commodo sed egestas egestas fringilla phasellus faucibus scelerisque eleifend. Gravida arcu ac tortor dignissim convallis. Gravida rutrum quisque non tellus orci ac auctor augue.</p>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quam pellentesque nec nam aliquam sem et tortor consequat. Amet mauris commodo quis imperdiet. Egestas egestas fringilla phasellus faucibus scelerisque eleifend donec pretium. Auctor elit sed vulputate mi sit. Semper viverra nam libero justo. Auctor elit sed vulputate mi. At ultrices mi tempus imperdiet nulla malesuada. Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget. Condimentum lacinia quis vel eros donec ac odio tempor. Ac placerat vestibulum lectus mauris ultrices eros. Enim praesent elementum facilisis leo. Enim nulla aliquet porttitor lacus. Auctor elit sed vulputate mi sit amet mauris. Volutpat commodo sed egestas egestas fringilla phasellus faucibus scelerisque eleifend. Gravida arcu ac tortor dignissim convallis. Gravida rutrum quisque non tellus orci ac auctor augue.</p>
<h1>CONTEUDO</h1>
<h2>SUBTITULO</h2>
<p><strong>Lorem</strong> ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quam pellentesque nec nam aliquam sem et tortor consequat. Amet mauris commodo quis imperdiet. Egestas egestas fringilla phasellus faucibus scelerisque eleifend donec pretium. Auctor elit sed vulputate mi sit. Semper viverra nam libero justo. Auctor elit sed vulputate mi. At ultrices mi tempus imperdiet nulla malesuada. Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget. Condimentum lacinia quis vel eros donec ac odio tempor. Ac placerat vestibulum lectus mauris ultrices eros. Enim praesent elementum facilisis leo. Enim nulla aliquet porttitor lacus. Auctor elit sed vulputate mi sit amet mauris. Volutpat commodo sed egestas egestas fringilla phasellus faucibus scelerisque eleifend. Gravida arcu ac tortor dignissim convallis. Gravida rutrum quisque non tellus orci ac auctor augue.</p>
<h3>SUBSUBTITULO</h3>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quam pellentesque nec nam aliquam sem et tortor consequat. Amet mauris commodo quis imperdiet. Egestas egestas fringilla phasellus faucibus scelerisque eleifend donec pretium. Auctor elit sed vulputate mi sit. Semper viverra nam libero justo. Auctor elit sed vulputate mi. At ultrices mi tempus imperdiet nulla malesuada. Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget. Condimentum lacinia quis vel eros donec ac odio tempor. Ac placerat vestibulum lectus mauris ultrices eros. Enim praesent elementum facilisis leo. Enim nulla aliquet porttitor lacus. Auctor elit sed vulputate mi sit amet mauris. Volutpat commodo sed egestas egestas fringilla phasellus faucibus scelerisque eleifend. Gravida arcu ac tortor dignissim convallis. Gravida rutrum quisque non tellus orci ac auctor augue.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quam pellentesque nec nam aliquam sem et tortor consequat. Amet mauris commodo quis imperdiet. Egestas egestas fringilla phasellus faucibus scelerisque eleifend donec pretium. Auctor elit sed vulputate mi sit. Semper viverra nam libero justo. Auctor elit sed vulputate mi. At ultrices mi tempus imperdiet nulla malesuada. Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget. Condimentum lacinia quis vel eros donec ac odio tempor. Ac placerat vestibulum lectus mauris ultrices eros. Enim praesent elementum facilisis leo. Enim nulla aliquet porttitor lacus. Auctor elit sed vulputate mi sit amet mauris. Volutpat commodo sed egestas egestas fringilla phasellus faucibus scelerisque eleifend. Gravida arcu ac tortor dignissim convallis. Gravida rutrum quisque non tellus orci ac auctor augue.</p>
<h1>CONCLUS&Atilde;O</h1>
<ul>
<li>teste</li>
<li>teset1</li>
<li>etstevgfv</li>
</ul>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quam pellentesque nec nam aliquam sem et tortor consequat. Amet mauris commodo quis imperdiet. Egestas egestas fringilla phasellus faucibus scelerisque eleifend donec pretium. Auctor elit sed vulputate mi sit. Semper viverra nam libero justo. Auctor elit sed vulputate mi. At ultrices mi tempus imperdiet nulla malesuada. Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget. Condimentum lacinia quis vel eros donec ac odio tempor. Ac placerat vestibulum lectus mauris ultrices eros. Enim praesent elementum facilisis leo. Enim nulla aliquet porttitor lacus. Auctor elit sed vulputate mi sit amet mauris. Volutpat commodo sed egestas egestas fringilla phasellus faucibus scelerisque eleifend. Gravida arcu ac tortor dignissim convallis. Gravida rutrum quisque non tellus orci ac auctor augue.</p>
<p><img src="TCC Control.png" width="300" height="300" /></p>
<table style="border-collapse: collapse; width: 100%;" border="1">
<tbody>
<tr>
<td style="width: 47.9858%;">Nome</td>
<td style="width: 47.9858%;">Fun&ccedil;&atilde;o</td>
</tr>
<tr>
<td style="width: 47.9858%;">Willian Matiussi</td>
<td style="width: 47.9858%;">Desenvolvedor</td>
</tr>
</tbody>
</table>
"""
            }
        ]
    }

    json2docx(data)
