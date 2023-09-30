from bs4 import BeautifulSoup
from html2json.script import convert
from HTMLtoDocx import HTMLtoDocx
import json
from docxtpl import DocxTemplate
import win32com.client
import os


def is_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return bool(soup.find())


def docx2pdf(path_docx, path_pdf):
    word = win32com.client.Dispatch('Word.Application')
    doc = word.Documents.Open(path_docx)
    try:
        doc.SaveAs(path_pdf, FileFormat=17)
    except Exception as e:
        print(f"Erro ao converter para PDF: {str(e)}")
    finally:
        doc.Close()
        word.Quit()

class JsonToDocx:
    def __init__(self, path_docx, json_data, output_file_name):
        self.path_docx = path_docx
        self.json_data = json_data
        self.output_file_name = output_file_name
        self.doc = DocxTemplate(path_docx)

    def convert(self):
        html2docx = HTMLtoDocx(self.doc)
        context = {}

        for field in self.json_data.get("fields", []):
            key = field.get("key")
            value = field.get("value")

            if key and value:
                if is_html(value):
                    try:
                        json_string = convert(value)
                        items = json.loads(json_string)
                        context[key] = html2docx.convert(items)
                    except Exception as e:
                        print(f"Erro ao converter HTML para JSON: {str(e)}")
                else:
                    context[key] = value

        try:
            self.doc.render(context)
            self.doc.save(self.output_file_name + ".docx")
            docx2pdf(os.getcwd() + "/" + self.output_file_name + ".docx", os.getcwd() + "/" + self.output_file_name + ".pdf")
        except Exception as e:
            print(f"Erro ao criar o documento: {str(e)}")
