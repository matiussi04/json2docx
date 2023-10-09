from bs4 import BeautifulSoup
from html2json.script import convert
from HTMLtoDocx import HTMLtoDocx
import json
from docxtpl import DocxTemplate
import comtypes.client
import docx
import os


def is_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return bool(soup.find())


def docx2pdf(word_path, pdf_path):
    doc = docx.Document(word_path)

    word = comtypes.client.CreateObject("Word.Application")
    docx_path = os.path.abspath(word_path)
    pdf_path = os.path.abspath(pdf_path)

    pdf_format = 17
    word.Visible = False
    in_file = word.Documents.Open(docx_path)
    in_file.SaveAs(pdf_path, FileFormat=pdf_format)
    in_file.Close()

    word.Quit()


class JsonToDocx:
    def __init__(self, input_path_docx, json_data, output_path_docx, output_path_pdf):
        self.input_path_docx = input_path_docx
        self.json_data = json_data
        self.output_path_docx = output_path_docx
        self.output_path_pdf = output_path_pdf
        self.doc = DocxTemplate(input_path_docx)
        self.html2docx = HTMLtoDocx(self.doc)

    def convert(self):
        context = {}

        for field in self.json_data.get("fields", []):
            key = field.get("key")
            value = field.get("value")

            if key and value:
                if is_html(value):
                    try:
                        json_string = convert(value)
                        items = json.loads(json_string)
                        context[key] = self.html2docx.convert(items)
                    except Exception as e:
                        print(f"Erro ao converter HTML para JSON: {str(e)}")
                else:
                    context[key] = value

        try:
            self.doc.render(context)
            self.doc.save(self.output_path_docx)
            docx2pdf(self.output_path_docx, self.output_path_pdf)
        except Exception as e:
            print(f"Erro ao criar o documento: {str(e)}")
