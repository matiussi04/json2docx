from docx import Document
from bs4 import BeautifulSoup
from html2json.script import convert
import json
from docxtpl import DocxTemplate
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

styles = {
    "p": "paragrafo",
    "h1": "Heading 1",
    "h2": "Heading 2",
    "h3": "Heading 3",
    "h4": "Heading 4",
    "h5": "Heading 5",
}

align = {
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY
}

OPTIONS = {
    "bold": False,
    "italic": False,
    "underline": False,
}


def is_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return bool(soup.find())


def check_styles():
    doc_teste = Document("template.docx")
    styles_in_document = doc_teste.styles

    for style in styles_in_document:
        print(style.name)


def check_sections():
    doc_teste = Document("documento_final.docx")
    sections = doc_teste.sections

    for section in sections:
        print(section)


def data_table(data):
    table_data = data['values'][0]['values']

    matrix = []

    for row in table_data:
        row_values = []
        for cell in row['values']:
            row_values.append(cell['values'])
        matrix.append(row_values)

    return matrix


def render_values(paragraph, item, options=OPTIONS):
    for value in item:
        run = paragraph.add_run()
        if not paragraph.style.name.startswith("Heading"):
            run.italic = options["italic"]
            run.bold = options["bold"]
            run.underline = options["underline"]
        if isinstance(value, str):
            run.add_text(value)
        elif value["tag_name"] == "img":
            width = value["attributes"].get("width", "")
            height = value["attributes"].get("height", "")
            source = value["attributes"]["src"]
            if (width == ""):
                run.add_picture(source)
            else:
                width_in_pixels = float(width)
                height_in_pixels = float(height)
                run.add_picture(source, width=Inches(
                    width_in_pixels * 0.0138889), height=Inches(height_in_pixels * 0.0138889))
            paragraph.style = 'Normal'
        elif value["tag_name"] == "strong":
            run.bold = True
            new_options = {
                "bold": run.bold,
                "italic": run.italic,
                "underline": run.underline,
            }
            render_values(paragraph, value["values"], new_options)
        elif value["tag_name"] == "em":
            run.italic = True
            new_options = {
                "bold": run.bold,
                "italic": run.italic,
                "underline": run.underline,
            }
            render_values(paragraph, value["values"], new_options)
        elif value["tag_name"] == "span":
            run.underline = True
            new_options = {
                "bold": run.bold,
                "italic": run.italic,
                "underline": run.underline,
            }
            render_values(paragraph, value["values"], new_options)


def process_list(subDocument, li):
    for item in li["values"]:
        p = subDocument.add_paragraph("Teste", style="List Paragraph")
        render_values(p, item["values"])


def process_table(subDocument, data):
    table = subDocument.add_table(
        rows=len(data), cols=len(data[0]), style="Table Grid")

    for row_index, row in enumerate(data):
        row_cells = table.rows[row_index].cells
        for index, cell_data in enumerate(row):
            p = row_cells[index].paragraphs[0]
            p.style = 'Normal'

            if isinstance(cell_data[0], str):
                render_values(p, cell_data)
            else:
                for index_item, item in enumerate(cell_data):
                    if index_item == 0:
                        render_values(p, item["values"])
                    else:
                        paragraph = row_cells[index].add_paragraph()
                        paragraph.style = 'Normal'
                        render_values(paragraph, item["values"])


def process_default(subDocument, tag_name, values):
    paragraph = subDocument.add_paragraph()
    paragraph.style = styles[tag_name]
    render_values(paragraph, values)


def process_items(doc, items):
    subDocument = doc.new_subdoc()

    for key in items["keys"]:
        if key["tag_name"] == "ul":
            process_list(subDocument, key)
        elif key["tag_name"] == "table":
            data = data_table(key)
            process_table(subDocument, data)
        else:
            process_default(subDocument, key["tag_name"], key["values"])

    return subDocument


def json2docx(data):
    doc = DocxTemplate("template.docx")

    context = {}

    for field in data["fields"]:
        key = field["key"]
        value = field["value"]

        if type(value) is list:
            print('list')
        elif is_html(value):
            json_string = convert(value)
            items = json.loads(json_string)
            context.update({key: process_items(doc, items)})
        else:
            context[key] = value

    doc.render(context)

    doc.save("documento_final.docx")


if __name__ == '__main__':
    data = {
        "fields": [
            {
                "key": "titulo",
                "value": "TCC CONTROL: UM SISTEMA PARA GERENCIAMENTO DE TCC",
                "type": "string"
            },
            {
                "key": "coordenador",
                "value": "Lucas",
                "type": "string"
            },
            {
                "key": "aluno",
                "value": "Lucas",
                "type": "string"
            },
            {
                "key": "orientador",
                "value": "Felipe Pereira Perez",
                "type": "string"
            },
            {
                "key": "bibliografia",
                "value": [
                    "Bibliografia 1",
                    "Bibliografia 2",
                    "Bibliografia 3"
                ],
                "type": "ref"
            },
            {
                "key": "version",
                "value": [
                    {"created_at": "24/03/2023", "version": "1.0",
                        "description": "blablabla", "author": "Willian"},
                    {"created_at": "25/03/2023", "version": "1.1",
                        "description": "blablabla", "author": "Willian"},
                    {"created_at": "26/03/2023", "version": "1.2",
                        "description": "blablabla", "author": "Willian"},
                ],
                "type": "list_version"
            },
            {
                "key": "content",
                "value": """
                                <table style="border-collapse: collapse; width: 100.028%;" border="1">
<tbody>
<tr>
<td style="width: 18.0499%;">12</td>
<td style="width: 18.0499%;">3</td>
<td style="width: 18.0499%;">4</td>
<td style="width: 18.0499%;">5</td>
<td style="width: 18.0545%;">6</td>
</tr>
<tr>
<td style="width: 18.0499%;">DFDFDF</td>
<td style="width: 18.0499%;">4</td>
<td style="width: 18.0499%;">65</td>
<td style="width: 18.0499%;">65</td>
<td style="width: 18.0545%;">4</td>
</tr>
<tr>
<td style="width: 18.0499%;">54</td>
<td style="width: 18.0499%;">4</td>
<td style="width: 18.0499%;">54</td>
<td style="width: 18.0499%;">5</td>
<td style="width: 18.0545%;">45</td>
</tr>
</tbody>
</table>
<h1>ESCOPO DO SISTEMA</h1>
<h2>Dados Iniciais</h2>
<p><strong>Nome do software: </strong>TCC Control Um sistema de gerenciamento de TCC</p>
<p><strong>Patrocinador:</strong> Willian Matiussi e Lucas Frutuozo Braga</p>
<p><strong>Publico Alvo:&nbsp;</strong></p>
<ul>
<li>Orientando</li>
<li>Orientador</li>
<li>Professor da disciplina&nbsp;</li>
</ul>
<p><strong>Stakeholders:&nbsp;</strong>As partes interessadas representam os alunos da institui&ccedil;&atilde;o Unigran que est&atilde;o cursando a disciplina de TCC I e TCC II de engenharia de software, al&eacute;m dos professores que atuam como orientadores e professores da disciplina.&nbsp;</p>
<p><strong>Equipe B&aacute;sica </strong></p>
<p><strong>Analistas/Desenvolvedores:&nbsp;</strong>Willian Matiussi e Lucas Frutuozo Braga&nbsp;</p>
<p><strong>Orientadores:&nbsp;</strong>Prof. Felipe Perez&nbsp;</p>
<p><strong>Consultor:&nbsp;</strong> Prof. Felipe Perez&nbsp;</p>
<h2>Motiva&ccedil;&atilde;o E Problem&aacute;tica Abordada Pelo Software</h2>
<h3>Defini&ccedil;&atilde;o e import&acirc;ncia</h3>
<p>Segundo o pr&oacute;prio regulamento de trabalho de conclus&atilde;o de curso da institui&ccedil;&atilde;o Unigran: "As disciplinas de Trabalho de Conclus&atilde;o de Curso I e II t&ecirc;m por objetivo 6 proporcionar aos discentes condi&ccedil;&otilde;es complementares de atividades de aprendizagem te&oacute;ricas e pr&aacute;ticas nos diferentes campos de atua&ccedil;&atilde;o profissional da Engenharia de Software.". Referese ao processo pelo qual o discente aplica todo o conhecimento adquirido atrav&eacute;s do curso na execu&ccedil;&atilde;o de um trabalho pr&aacute;tico em forma de produto, que abrange um tema que foi escolhido pelo pr&oacute;prio aluno para ser aprofundado.</p>
<p>Pereira e Silva (2009?) colocam que o TCC &eacute; a primeira produ&ccedil;&atilde;o cient&iacute;fica que o aluno produz ap&oacute;s os anos de experi&ecirc;ncia que ele absorve na gradua&ccedil;&atilde;o, refere-se a uma constru&ccedil;&atilde;o de rigor epistemol&oacute;gico, estrutural e metodol&oacute;gico, regulamentadas por normas de trabalho acad&ecirc;mico que demanda esfor&ccedil;o essencial do aluno de car&aacute;ter cient&iacute;fico, cr&iacute;tico e participativo para a elabora&ccedil;&atilde;o do trabalho. Portanto, s&atilde;o processos, geralmente discursivos e conclusivos, que culminam em informa&ccedil;&otilde;es organizadas sobre uma tem&aacute;tica definida.</p>
<p>Segundo Pereira, o TCC vai al&eacute;m de uma ferramenta avaliativa para o final do curso, trata-se de uma produ&ccedil;&atilde;o de conhecimento e experi&ecirc;ncias formativas, onde o aluno entra em contato com perspectivas diversas e estudos pr&eacute;vios sobre o seu tema de pesquisa.</p>
<p>Tendo vista o rigor t&eacute;cnico-cient&iacute;fico do trabalho &eacute; necess&aacute;rio que o aluno tenha adquirido ao longo do curso saberes pedag&oacute;gicos e epistemol&oacute;gicos que s&atilde;o essenciais para a constru&ccedil;&atilde;o correta e eficaz do intuito que o TCC abrange, tornando, important&iacute;ssimo a escolha do seu tema, bem como o desenvolvimento correto da produ&ccedil;&atilde;o, al&eacute;m da orienta&ccedil;&atilde;o adequada para que o trabalho traga benef&iacute;cios, n&atilde;o s&oacute; para ele, mas para a sociedade em geral.</p>
<p>Al&eacute;m disso, o TCC &eacute; uma oportunidade para que os estudantes possam aprofundar seus conhecimentos em uma &aacute;rea espec&iacute;fica de interesse, al&eacute;m de contribuir para o avan&ccedil;o do conhecimento em determinada &aacute;rea de estudo. &Eacute; importante destacar que o TCC &eacute; um momento de transi&ccedil;&atilde;o para o estudante, que passa a se inserir no mercado de trabalho e se torna um profissional qualificado. Por esse motivo, muitas empresas valorizam o TCC na hora da contrata&ccedil;&atilde;o, pois ele demonstra a capacidade do estudante em desenvolver projetos, trabalhar em equipe e enfrentar desafios complexos. E essa import&acirc;ncia &eacute; falada por Magalh&atilde;es (2010): &ldquo;[...] o TCC tamb&eacute;m pode se tornar um passaporte para o sucesso entre os profissionais que j&aacute; se encontram empregados, facilitando uma efetiva&ccedil;&atilde;o, no caso de estagi&aacute;rios, ou uma promo&ccedil;&atilde;o&rdquo;.</p>
<p>Em resumo, o TCC &eacute; uma atividade fundamental para o desenvolvimento acad&ecirc;mico e profissional dos estudantes de gradua&ccedil;&atilde;o, sendo um momento de aprendizado e crescimento, bem como de demonstra&ccedil;&atilde;o de compet&ecirc;ncias e habilidades essenciais para o sucesso na carreira.</p>
<h3>Contextualiza&ccedil;&atilde;o</h3>
<p>O termo "monografia" teve sua origem no s&eacute;culo XIX como um m&eacute;todo de ci&ecirc;ncias sociais, resultando no trabalho "Monografia da fam&iacute;lia oper&aacute;ria" publicado por Le Play em 1855. Apesar das interpreta&ccedil;&otilde;es variadas no meio acad&ecirc;mico, a caracter&iacute;stica principal da monografia ou TCC consiste em construir um trabalho focado em um &uacute;nico assunto ou problema, mantendo-se fiel &agrave; etimologia da palavra "monos" (um s&oacute;) e "grafhein" (escrever). O TCC tornou-se uma pr&aacute;tica acad&ecirc;mica consolidada no final da d&eacute;cada de 1980, inicialmente exigido em cursos como Direito, Servi&ccedil;o Social e Psicologia, e agora faz parte da maioria dos cursos de gradua&ccedil;&atilde;o. A ABNT estabelece defini&ccedil;&otilde;es claras para trabalhos acad&ecirc;micos, incluindo TCC, TGI, Trabalho de Conclus&atilde;o de Curso de Especializa&ccedil;&atilde;o e/ou Aperfei&ccedil;oamento e outros, que devem expressar conhecimento sobre o assunto escolhido, ser necessariamente vinculados &agrave; disciplina e desenvolvidos sob a orienta&ccedil;&atilde;o de um professor. A produ&ccedil;&atilde;o de um TCC oferece benef&iacute;cios cruciais para o sucesso pessoal e profissional do aluno (Pereira e Silva, 2009?).</p>
<p>Costa e Silva (2019) aborda que o TCC apresenta grandes dificuldades, entre as quais est&aacute; a organiza&ccedil;&atilde;o do cronograma e do tempo, uma vez que &eacute; necess&aacute;rio planejar as atividades, elaborar o referencial te&oacute;rico, realizar a pesquisa bibliogr&aacute;fica e encontrar o orientador adequado para o tema em quest&atilde;o, al&eacute;m de manter uma boa comunica&ccedil;&atilde;o entre orientando e orientador, que pode ser crucial para o desenvolvimento do trabalho. Todos esses pontos e dificuldades podem causar diversos sentimentos negativos para os envolvidos, como o medo de n&atilde;o concluir e a preocupa&ccedil;&atilde;o com prazos, agravando ainda mais a desorganiza&ccedil;&atilde;o.</p>
<p>Segundo a pesquisa realizada por Costa e Silva, um dos principais obst&aacute;culos que os alunos encontram est&aacute; na defini&ccedil;&atilde;o da estrutura do trabalho, ou seja, na constru&ccedil;&atilde;o de elementos como o question&aacute;rio, a an&aacute;lise dos dados e o resumo, seguido da defini&ccedil;&atilde;o do tema. Isso poderia ser melhorado caso houvesse um sistema que auxiliasse na organiza&ccedil;&atilde;o das etapas e indicasse a ordem cronol&oacute;gica das tarefas.</p>
<p>Al&eacute;m da estrutura do projeto, o tempo tamb&eacute;m se demonstra como outra fonte de problema advindo do TCC, uma vez que os alunos se encontram rodeados de v&aacute;rios compromissos cotidianos, que facilmente podem ocasionar atrasos e impedir a conclus&atilde;o do trabalho. Faz-se necess&aacute;rio o controle dos prazos e o gerenciamento das reuni&otilde;es com o orientador de modo a melhorar a organiza&ccedil;&atilde;o do tempo.</p>
<p>Outro ponto em destaque est&aacute; na rela&ccedil;&atilde;o com o orientador, que deve ser um v&iacute;nculo m&uacute;tuo de esfor&ccedil;o e dedica&ccedil;&atilde;o para organizar o tempo, as ideias, os di&aacute;logos e as corre&ccedil;&otilde;es. Essa rela&ccedil;&atilde;o pode ser melhorada com a utiliza&ccedil;&atilde;o de uma aplica&ccedil;&atilde;o capaz de gerenciar as corre&ccedil;&otilde;es e melhorar o modo como os envolvidos podem organizar seu tempo, facilitando a comunica&ccedil;&atilde;o e o acompanhamento do progresso do trabalho.</p>
<h3>O P&uacute;blico-alvo</h3>
<p>O projeto tem como p&uacute;blico-alvo os alunos que est&atilde;o matriculados no curso de engenharia de software e aptos a cursar as disciplinas de TCC I e TCC II, al&eacute;m dos professores que ir&atilde;o atuar como orientadores e do professor que ser&aacute; respons&aacute;vel pela disciplina.</p>
<p>Os alunos poder&atilde;o utilizar o sistema para ter maior controle das entregas e dos prazos, j&aacute; os orientadores poder&atilde;o avaliar melhor o progresso de cada trabalho realizando corre&ccedil;&otilde;es e melhorias, j&aacute; o professor da disciplina, ter&aacute; controle maior de como est&aacute; o andamento da disciplina com rela&ccedil;&atilde;o a cada trabalho.</p>
<h2>Justificativa Do Projeto</h2>
<p>A gest&atilde;o do Trabalho de Conclus&atilde;o de Curso (TCC) pode ser um desafio para os professores orientadores e para os pr&oacute;prios estudantes, pois demanda um grande esfor&ccedil;o para manter o processo organizado e dentro dos prazos estabelecidos. A falta de um sistema para gerenciar o TCC pode causar diversos problemas, como retrabalho, confus&otilde;es e atrasos. E de acordo com Costa e Silva: "Al&eacute;m disso, os licenciandos afirmam a necessidade de administrar o tempo e n&atilde;o deixar para &uacute;ltima hora, por considerarem um trabalho complexo, requer certa organiza&ccedil;&atilde;o."</p>
<p>Com isso surge a necessidade de desenvolver um sistema de controle para gerenciar o processo do TCC, garantindo a efici&ecirc;ncia e a qualidade do trabalho. O objetivo deste trabalho &eacute; apresentar o desenvolvimento de um sistema de controle de TCC, com a finalidade de facilitar a gest&atilde;o do processo e minimizar os problemas causados pela falta de um sistema adequado.</p>
<h2>Entregas Do Projeto</h2>
<ul>
<li>Documento de Requisitos</li>
<li>Sistemacodificado com osrequisitosimplementados</li>
</ul>
<h2>Objetivos Do Sistema</h2>
<p>O objetivo deste trabalho &eacute; desenvolver um sistema para gerenciar a disciplina de TCC, de modo que todos os envolvidos, como orientandos, orientadores e professor da disciplina, possam desfrutar de um fluxo mais organizado, proveniente do sistema que ser&aacute; capaz de controlar prazos por meio de calend&aacute;rios, cronogramas e alertas. Al&eacute;m disso, o sistema tornar&aacute; as entregas mais organizadas, podendo ser facilmente visualizadas na aplica&ccedil;&atilde;o.</p>
<h2>Crit&eacute;riosDeAceita&ccedil;&atilde;o Do Sistema</h2>
<p>Todas as funcionalidades do website devem ser testadas atrav&eacute;s do emprego de:</p>
<ul>
<li>Testes de Usabilidade;</li>
<li>Testes de Software;</li>
</ul>
<h2>Consultor Do Sistema</h2>
<p>Felipe Perez, portador do CPF 000.000.000-00 e telefone +55 67 9 9999-9999, &eacute; desenvolvedor de software s&ecirc;nior e atua na &aacute;rea desde 2008, graduado em Ci&ecirc;ncia da Computa&ccedil;&atilde;o em 2012 pela UEMS em Dourados. Atualmente &eacute; professor da institui&ccedil;&atilde;o Unigran, ministrando aulas sobre as linguagens e tecnologias NodeJS, PHP, jQuery, AJAX, CSS3, HTML5 and Bootstrap, al&eacute;m de gerenciar times de desenvolvimento atrav&eacute;s de metodologias &aacute;geis.</p>
<p>O professor Felipe tamb&eacute;m auxilia os alunos matriculados nas disciplinas de TCC I e II como orientador, e, portanto, reconhece a necessidade do desenvolvimento de um sistema capaz de controlar os processos e facilitar a avalia&ccedil;&atilde;o do trabalho de conclus&atilde;o de curso.</p>
<h2>Entrevista Com O Consultor Do Sistema</h2>
<ul>
<li>Como o sistema deve controlar os usu&aacute;rios? Se o sistema permitir que qualquer pessoa consiga cadastrar uma conta, como ser&aacute; controlado o cargo de cada usu&aacute;rio (Orientando, orientador e professor da disciplina)?</li>
</ul>
<p>R: Cabe a um usu&aacute;rio administrador liberar o acesso dos professores da disciplina, j&aacute; os demais usu&aacute;rios poder&atilde;o criar sua pr&oacute;pria conta na aplica&ccedil;&atilde;o, atribuindo perfil de aluno automaticamente, j&aacute; os orientadores dever&atilde;o ser selecionados pelo professor da disciplina.</p>
<ul>
<li>Como o sistema deve manter o hist&oacute;rico de altera&ccedil;&atilde;o dos arquivos, considerando que a data de uma etapa j&aacute; tenha sido ultrapassada o orientando poder&aacute; editar o arquivo anexado ou ele ter&aacute; que submeter um novo arquivo?</li>
</ul>
<p>R: O sistema ir&aacute; trabalhar com caixas de textos ao inv&eacute;s de submeter arquivos docx ou pdf e ao final do projeto toda formata&ccedil;&atilde;o ABNT ser&aacute; feita de forma autom&aacute;tica. Durante o desenvolvimento da etapa o aluno poder&aacute; alterar o arquivo Normalmente, entretanto ap&oacute;s a conclus&atilde;o do arquivo, caso ele queira fazer uma altera&ccedil;&atilde;o ter&aacute; que solicitar ao professor da disciplina e caso seja feito, o hist&oacute;rico ser&aacute; armazenado.</p>
<ul>
<li>Como o sistema deve reagir se o aluno anexar um trabalho corrigido pelo orientador, mas n&atilde;o comparecer &agrave; apresenta&ccedil;&atilde;o?</li>
</ul>
<p>R: Considerando que as apresenta&ccedil;&otilde;es n&atilde;o podem se repetir, uma vez que &eacute; dif&iacute;cil conseguir um hor&aacute;rio e reunir todos os envolvidos, se o orientando n&atilde;o participar, a atividade simplesmente &eacute; considerada entregue, mas n&atilde;o apresentada. J&aacute; que isso n&atilde;o pode ser bloqueado. O fator bloqueador est&aacute; na entrega ao orientador e na entrega ao classroom para o professor da disciplina.</p>
<ul>
<li>Como o sistema deve reagir se o aluno anexar um trabalho corrigido pelo orientador, mas n&atilde;o enviar ao classroom?</li>
</ul>
<p>R: Com a utiliza&ccedil;&atilde;o do TCC Control, todas as entregas ser&atilde;o gerenciadas pela aplica&ccedil;&atilde;o, eliminando a utiliza&ccedil;&atilde;o do google classroom.</p>
<ul>
<li>Como o sistema deve reagir se o aluno anexou o trabalho na aplica&ccedil;&atilde;o e o orientador n&atilde;o confirmar (Corrigir)?</li>
</ul>
<p>R: Caso o aluno submeta o trabalho na aplica&ccedil;&atilde;o e no classroom, o professor da disciplina ter&aacute; o controle para confirmar a entrega.</p>
<ul>
<li>Como o sistema deve reagir se o aluno n&atilde;o tiver anexado o trabalho na aplica&ccedil;&atilde;o e a data de entrega ao orientador for ultrapassada?</li>
</ul>
<p>R: Isso &eacute; considerado de forma bloqueante para for&ccedil;ar que aluno utilize o sistema, isso significa que n&atilde;o poder&aacute; participar da pr&oacute;xima etapa.</p>
<ul>
<li>Como o sistema deve reagir quando o aluno prop&otilde;e um tema de TCC, por&eacute;m o orientador rejeita?</li>
</ul>
<p>R: Ele dever&aacute; criar uma nova proposta ou editar a proposta com os ajustes solicitados pelo orientador, depois de confirmado as corre&ccedil;&otilde;es o orientador poder&aacute; aprovar o tema.</p>
<ul>
<li>O que acontece se um aluno concluir a disciplina de TCC I no primeiro semestre de 2021 e deixar para concluir o TCC II no segundo semestre de 2022?</li>
</ul>
<p>R: Caso o aluno n&atilde;o termine o TCC II no mesmo ano do TCC I, ele dever&aacute; iniciar a disciplina de TCC II a partir do segundo semestre do pr&oacute;ximo ano letivo, para seguir o cronograma de desenvolvimento das disciplinas de TCC.</p>
<ul>
<li>Quais informa&ccedil;&otilde;es necess&aacute;rias para o cadastro de usu&aacute;rio?</li>
</ul>
<p>R: Nome, RGM, curso e endere&ccedil;o de E-mail.</p>
<ul>
<li>Caso o aluno entregue a atividade antes do prazo ele poder&aacute; ter acesso a pr&oacute;xima atividade? Ou s&oacute; ter&aacute; acesso a atividade ap&oacute;s encerrar o prazo da atividade atual?</li>
</ul>
<p>R: O sistema dever&aacute; for&ccedil;ar que o aluno siga o cronograma e a ordem cronol&oacute;gica das etapas, por&eacute;m ele conseguir&aacute; visualizar todo o cronograma em uma tela e adiantar algumas etapas, no entanto, cada etapa tem sua corre&ccedil;&atilde;o e import&acirc;ncia para as demais, caso uma seja ajustada as pr&oacute;ximas tamb&eacute;m podem ser alteradas, causando retrabalho ao aluno.</p>
<ul>
<li>O TCC ser&aacute; feito apenas por um aluno? Se n&atilde;o qual o n&uacute;mero m&aacute;ximo pode conter um grupo de TCC?</li>
</ul>
<p>R: O TCC pode ser feito individualmente ou em dupla.</p>
<ul>
<li>Se o projeto for em grupo, o que ocorrer&aacute; caso o aluno queira fazer individual no decorrer do projeto?</li>
</ul>
<p>R: O aluno dever&aacute; fazer uma solicita&ccedil;&atilde;o ao professor da disciplina que caso seja aceita o sistema ir&aacute; clonar todo o trabalho e atribuir cada aluno a um &uacute;nico tcc.</p>
<ul>
<li>O que ocorrer&aacute; caso o aluno troque de projeto?</li>
</ul>
<p>R: Deveria recriar todo o fluxo de desenvolvimento novamente.</p>
<ul>
<li>O que ocorrer&aacute; caso o aluno troque de orientador?</li>
</ul>
<p>R: Dever&aacute; solicitar a troca de orientador que dever&aacute; passar por uma aprova&ccedil;&atilde;o do professor da disciplina.</p>
<ul>
<li>O aluno poder&aacute; modificar alguma parte do projeto dele que j&aacute; tenha sido entregue anteriormente? Como por exemplo os requisitos.</li>
</ul>
<p>R: O sistema ir&aacute; controlar todas etapas e caso ele queira editar uma etapa ter&aacute; que solicitar ao professor da disciplina. Caso haja altera&ccedil;&otilde;es, o sistema ir&aacute; manter o hist&oacute;rico.</p>
<h1>REQUISITOS DO SISTEMA</h1>
<p>Neste cap&iacute;tulo, ser&atilde;o apresentados os aspectos t&eacute;cnicos do projeto Website a ser desenvolvido.</p>
<h2>MetodologiaDeLevantamentoDeRequisitos</h2>
<p>O projeto ser&aacute; desenvolvido em junho de 2023, ap&oacute;s a coleta de requisitos, defini&ccedil;&atilde;o dos modelos de caso de uso e DER, organiza&ccedil;&atilde;o do cronograma e prototipa&ccedil;&atilde;o das interfaces. O trabalho ser&aacute; divido em duas etapas:</p>
<p>A primeira etapa &eacute; denominada de Levantamento de Requisitos, onde os analistas levantar&atilde;o os requisitos do sistema, atrav&eacute;s de entrevistas e observa&ccedil;&otilde;es no recinto. Ap&oacute;s a coleta de dados, os analistas ir&atilde;o elaborar uma vers&atilde;o preliminar dos requisitos do sistema (que ser&atilde;o descritos no cap&iacute;tulo 2 desse documento), que ser&aacute; submetido &agrave; valida&ccedil;&atilde;o por parte dos stakeholders.</p>
<h2>Requisitos</h2>
<p>O sistema dever&aacute; prover os seguintes requisitos:</p>
<h3>RequisitosFuncionais</h3>
<ul>
<li>Cria&ccedil;&atilde;o de cronograma: O sistema deve permitir ao professor da disciplina a cria&ccedil;&atilde;o de um cronograma com as atividades e prazos estabelecidos para o projeto atrav&eacute;s de etapas.</li>
<li>Cria&ccedil;&atilde;o de proposta de TCC: O sistema deve permitir que o orientando crie uma proposta de TCC, adicionando informa&ccedil;&otilde;es sobre o tema e seus objetivos, al&eacute;m de solicitar a orienta&ccedil;&atilde;o de um orientador.</li>
<li>Avalia&ccedil;&atilde;o de proposta de TCC: O sistema deve permitir que o orientador avalie a proposta de TCC do orientando, confirmando ou recusando o tema para que o(s) orientando(s) possam seguir com o desenvolvimento ou para que especifiquem um novo tema.</li>
<li>Gerenciamento de etapas: O sistema deve permitir ao professor da disciplina o gerenciamento das atividades do projeto, incluindo a cria&ccedil;&atilde;o, edi&ccedil;&atilde;o e exclus&atilde;o de etapas, al&eacute;m da defini&ccedil;&atilde;o de prazos. Cada etapa ser&aacute; constitu&iacute;da por uma atividade e para a atividade o professor da disciplina dever&aacute; especificar os campos que ser&atilde;o preenchidos, sejam eles do tipo texto, n&uacute;mero, c&oacute;digo, arquivo PNG ou JPG.</li>
<li>Gerenciamento de apresenta&ccedil;&otilde;es: O sistema deve permitir ao professor da disciplina o gerenciamento das apresenta&ccedil;&otilde;es do projeto, incluindo a defini&ccedil;&atilde;o de datas e hor&aacute;rios e o registro da presen&ccedil;a dos envolvidos.</li>
<li>Desenvolvimento de atividades: O sistema deve permitir o acompanhamento do desenvolvimento das atividades do projeto, incluindo a possibilidade de inserir informa&ccedil;&otilde;es sobre o andamento de cada tarefa, como estado de "conclus&atilde;o", "pend&ecirc;ncia", "entregue sem apresenta&ccedil;&atilde;o", &ldquo;entregue ao orientador&rdquo; e "n&atilde;o entregue".</li>
<li>Avalia&ccedil;&atilde;o de atividades: O sistema deve permitir a avalia&ccedil;&atilde;o das atividades do projeto, permitindo que o orientador atribua coment&aacute;rios.</li>
<li>Apresenta&ccedil;&atilde;o da atividade: O sistema deve permitir que o professor da disciplina consiga controlar as apresenta&ccedil;&otilde;es, atrav&eacute;s da confirma&ccedil;&atilde;o de presen&ccedil;a.</li>
<li>Marcar reuni&otilde;es: O sistema deve permitir que os orientandos e orientadores consigam agendar uma reuni&atilde;o, que deve passar por aprova&ccedil;&atilde;o entre todos os envolvidos da reuni&atilde;o.</li>
<li>Notifica&ccedil;&atilde;o: O sistema deve enviar notifica&ccedil;&otilde;es quando reuni&otilde;es forem agendadas, aceitas ou recusadas, al&eacute;m de disparar notifica&ccedil;&otilde;es quando avalia&ccedil;&otilde;es por coment&aacute;rios forem realizadas e quando o aluno submeter o trabalho na aplica&ccedil;&atilde;o. Quando a data de entrega ou apresenta&ccedil;&atilde;o estiver pr&oacute;xima, o sistema automaticamente ir&aacute; disparar notifica&ccedil;&otilde;es para orientandos em caso de trabalho n&atilde;o atribu&iacute;do e para orientadores em caso de trabalhos n&atilde;o avaliados e para alertar quando for a data de uma apresenta&ccedil;&atilde;o.</li>
<li>Gerenciamento de usu&aacute;rios: O sistema dever&aacute; realizar o cadastro de alunos, professores da disciplina e orientadores onde dever&aacute; constar suas informa&ccedil;&otilde;es, como nome completo, endere&ccedil;o de e-mail, registro de matr&iacute;cula (RGM), curso e o devido cargo que varia entre orientando, orientador e professor da disciplina.</li>
</ul>
<h3>RequisitosN&atilde;oFuncionais</h3>
<ul>
<li>Seguran&ccedil;a: O sistema deve garantir a seguran&ccedil;a das informa&ccedil;&otilde;es do projeto, impedindo o acesso n&atilde;o autorizado aos dados.</li>
<li>Usabilidade: O sistema deve ser f&aacute;cil de usar e ter uma interface intuitiva para que o usu&aacute;rio possa realizar suas tarefas de forma eficiente.</li>
<li>Confiabilidade: O sistema deve ser confi&aacute;vel e estar dispon&iacute;vel sempre que necess&aacute;rio, evitando falhas que possam prejudicar o andamento do projeto.</li>
<li>Desempenho: O sistema deve ter um desempenho adequado, sendo capaz de processar as informa&ccedil;&otilde;es e executar as tarefas de forma r&aacute;pida e eficiente.</li>
<li>Manuten&ccedil;&atilde;o: O sistema deve ser f&aacute;cil de manter e atualizar, permitindo a corre&ccedil;&atilde;o de poss&iacute;veis erros e a adi&ccedil;&atilde;o de novas funcionalidades.</li>
<li>Escalabilidade: O sistema deve ser capaz de lidar com um grande n&uacute;mero de usu&aacute;rios e projetos, permitindo o crescimento sem prejudicar o desempenho e a usabilidade. O uso do Django como framework em Python oferece vantagens em termos de escalabilidade, uma vez que &eacute; capaz de lidar com um grande volume de tr&aacute;fego e suportar m&uacute;ltiplas conex&otilde;es simult&acirc;neas.</li>
</ul>
<h2>Materiais E M&eacute;todos (Linguagem E Ferramentas Utilizadas)</h2>
<p>O desenvolvimento do trabalho ser&aacute; dividido em duas se&ccedil;&otilde;es. Inicialmente, ser&atilde;o coletados os requisitos funcionais e n&atilde;o-funcionais do sistema, por meio de entrevistas com o consultor atrav&eacute;s de perguntas. Ap&oacute;s a defini&ccedil;&atilde;o do comportamento do sistema e do seu escopo, ser&aacute; iniciado o processo de modelagem, com a elabora&ccedil;&atilde;o de diagramas de caso de uso (gerais e espec&iacute;ficos) e diagramas de entidade-relacionamento.</p>
<p>Com base na defini&ccedil;&atilde;o dos requisitos e da modelagem do sistema, ser&aacute; iniciado o processo de desenvolvimento, utilizando um ambiente de containers com aux&iacute;lio da ferramenta Docker e Docker Compose para criar uma inst&acirc;ncia da aplica&ccedil;&atilde;o em Python utilizando o framework Django. O sistema ter&aacute; uma arquitetura h&iacute;brida, com endpoints que entregam p&aacute;ginas HTML est&aacute;ticas ao client-side e outros endpoints que representam os estados do sistema, por meio de uma API REST. Para o front-end, ser&atilde;o utilizadas as tecnologias HTML, JS e CSS.</p>
<p>Por meio do ambiente de containers, qualquer usu&aacute;rio com acesso ao c&oacute;digo-fonte poder&aacute; subir uma inst&acirc;ncia local da aplica&ccedil;&atilde;o na m&aacute;quina e realizar altera&ccedil;&otilde;es ou incrementos atrav&eacute;s de um editor de texto, como o VsCode. Para gerenciar o c&oacute;digo-fonte, ser&aacute; utilizado o Git hospedado em um reposit&oacute;rio privado do GitLab, que oferece funcionalidades de code review e pipelines de CI/CD. As esteiras ser&atilde;o utilizadas para garantir a qualidade do c&oacute;digo, 15 com linters e ferramentas de testes (testes unit&aacute;rios e testes de integra&ccedil;&atilde;o), e para realizar o deploy.</p>
<p>As etapas de desenvolvimento ser&atilde;o gerenciadas no aplicativo Jira, com a cria&ccedil;&atilde;o de um backlog contendo as tarefas necess&aacute;rias para o desenvolvimento. Essas atividades ser&atilde;o divididas de forma semelhante ao modelo de est&oacute;rias, para que a cada implementa&ccedil;&atilde;o seja feita uma revis&atilde;o com o consultor, garantindo que o sistema esteja seguindo os requisitos coletados anteriormente e assegurando a qualidade. Antes de iniciar o desenvolvimento, ser&atilde;o criados prot&oacute;tipos de interface para valida&ccedil;&atilde;o, por meio da ferramenta Balsamiq.</p>
<h3>CasosDeUsosGerais</h3>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 100%; text-align: center;">RF1 - Login</td>
</tr>
<tr>
<td style="width: 100%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o usu&aacute;rio fa&ccedil;a login no sistema</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio deve estar cadastrado no sistema</p>
<p>Entrada: Recebe como entrada o E-mail e a senha</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Se tanto o e-mail como a senhaestiveremcorretos o usu&aacute;riopoder&aacute;teracessoaosistema</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF2 &ndash; VisualizarNotifica&ccedil;&otilde;es</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Essecasodeusopermiteaousu&aacute;riochecarsuasnotifica&ccedil;&otilde;es</p>
<p>Prioridade: Desej&aacute;vel</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;riodeveestarlogado no sistema</p>
<p>Entrada: n&atilde;otem</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: As notifica&ccedil;&otilde;ess&atilde;omarcadascomolidas</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF3 &ndash; GerenciamentodeTCC</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o aluno possa criar uma proposta de TCC, iniciar uma atividade e tamb&eacute;m corrigir atividades.</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;riodeveestarlogado no sistemacomoaluno</p>
<p>Entrada: Recebecomoentrada um tema para a propostadeTCCouumaatividade para iniciaroucorrigir</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: A propostadeTCC&eacute;mandada para um orientador para queelepossaanalisar, a atividade&eacute;enviada para o orientador para queelepossasugerircorre&ccedil;&otilde;esoufinalizala</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF4 &ndash; GerenciamentodeReuni&atilde;o</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Essecasodeusopermiteque o orientadoroualunopossamarcar, cancelar, reagendar e aceitarreuni&otilde;es para trataracerca do TCC</p>
<p>Prioridade: Importante</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;riodeveestarlogadocomoorientadoroualuno, e o alunodevepossuir um v&iacute;nculo com o orientador</p>
<p>Entrada: Recebecomoentrada a data queocorrer&aacute; a reuni&atilde;o</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute;sermandadoumanotifica&ccedil;&atilde;o para osparticipantesdareuni&atilde;ojunto com um convite para quepossamconfirmar a realiza&ccedil;&atilde;odareuni&atilde;o</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF5 &ndash; Corre&ccedil;&atilde;odeAtividades</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite ao orientador corrigir as atividades dando sugest&otilde;es.</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;riodever&aacute;estarlogadocomoorientador e tamb&eacute;mestarvinculadoaoaluno no qualir&aacute;corrigir as atividades</p>
<p>Entrada: Recebecomoentradasugest&otilde;esdecorre&ccedil;&otilde;es</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Caso a atividade n&atilde;o esteja certa ser&aacute; enviada ao aluno com as sugest&otilde;es sobre o que corrigir se estiver correto ser&aacute; enviado ao professor</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF6 &ndash; GerenciamentodeApresenta&ccedil;&atilde;o</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Essecasodeusopermiteque o professor possamarcarapresenta&ccedil;&otilde;es, marcar a presen&ccedil;a do aluno e tamb&eacute;mmarcarcomoconclu&iacute;da</p>
<p>Prioridade: Importante</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor</p>
<p>Entrada: Recebecomoentrada a data daapresenta&ccedil;&atilde;o</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute;notificarosalunosquefoimarcadaoualteradauma nova apresenta&ccedil;&atilde;o</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF7 &ndash; GerenciamentodeCronograma</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Essecasodeusopermiteque o professor possacriar e editar um cronograma</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor</p>
<p>Entrada: Recebecomoentrada as datasdasatividades a serementregue no decorrer do ano</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute;vincular o cronogramacriadoaosorientadores e aosalunos</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF8 &ndash; GerenciamentodeAlunos</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Essecasodeusopermiteque o professor possaalterar o login do aluno a um login deorientadorcomotamb&eacute;mexcluir o cadastro do aluno</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor</p>
<p>Entrada: Recebecomoentrada o aluno</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Caso o professor altere o login dealuno para orientadoreleir&aacute;agorater as fun&ccedil;&otilde;esdentro do sistemade um orientador e casoeleexclua do sistemair&aacute;perder o cadastro do aluno</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF9 &ndash; GerenciamentodeOrientadores</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Essecasodeusopermiteque o professor alterar o login do orientador a um login dealunocomotamb&eacute;mexcluir o cadastro do orientador</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor</p>
<p>Entrada: Recebecomoentrada um orientador</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Caso o professor altere o login deorientador para alunoeleir&aacute;agorater as fun&ccedil;&otilde;esdentro do sistemade um aluno e casoeleexclua do sistemair&aacute;perder o cadastro do orientador</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF10 &ndash; GerenciamentodeAtividades</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Essecasodeusopermite o professor criar, editar e excluiratividades</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor</p>
<p>Entrada: Recebecomoentrada o conte&uacute;dodaatividadeassimcomo a data deentrega</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute;notificarosalunosacercadasatividades</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<h3>Atoresenvolvidos</h3>
<p>Neste sistema, h&aacute; tr&ecirc;s atores que ir&atilde;o usar diretamente este sistema proposto:</p>
<ul>
<li>Professor: &eacute; o usu&aacute;rio respons&aacute;vel por todo o planejamento do TCC.</li>
<li>Orientador: &eacute; o usu&aacute;rio respons&aacute;vel pela parte da orienta&ccedil;&atilde;o e corre&ccedil;&atilde;o das atividades dos alunos.</li>
<li>Aluno: &eacute; o usu&aacute;rio comum que ir&aacute; desenvolver o TCC.</li>
</ul>
<p>&nbsp;</p>
<h2>CasosdeusoEspec&iacute;ficos</h2>
<h3>VisualizarNotifica&ccedil;&atilde;o</h3>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF1 &ndash; ChecarNotifica&ccedil;&otilde;es</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Essecasodeusopermitevisualizar as notifica&ccedil;&otilde;es</p>
<p>Prioridade: Desej&aacute;vel</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;riodever&aacute;estarlogado</p>
<p>Entrada: n&atilde;otem</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute;deixar as notifica&ccedil;&otilde;escomovisualizadas</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<h3>GerenciamentodeTCC</h3>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF1 &ndash; Criar Proposta de TCC</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o aluno crie uma proposta para o TCC</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como aluno</p>
<p>Entrada: Recebe como entrada o tema no qual ir&aacute; tratar seu TCC</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; enviar ao orientador escolhido para que ele possa analisar sua proposta</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%; height: 39.1666px;" border="1">
<tbody>
<tr style="height: 19.5833px;">
<td style="width: 97.8656%; text-align: center; height: 19.5833px;">RF2 &ndash; Inicia uma atividade</td>
</tr>
<tr style="height: 19.5833px;">
<td style="width: 97.8656%; height: 19.5833px;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o aluno inicie uma atividade</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como aluno e dever&aacute; ser disponibilizado a atividade para que ele.</p>
<p>Entrada: Recebe como entrada o conte&uacute;do da atividade</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; enviar ao orientador para que ele possa analisar e corrigir caso necess&aacute;rio.</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF3 &ndash; Corrigir atividade</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o aluno corrija uma atividade utilizando das sugest&otilde;es do orientador</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como aluno, dever&aacute; ser disponibilizado a atividade para que ele e o orientador dever&aacute; ter analisado e enviado sugest&otilde;es de altera&ccedil;&otilde;es para o aluno.</p>
<p>Entrada: Recebe como entrada o conte&uacute;do da atividade</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; enviar ao orientador para que ele possa analisar e corrigir caso necess&aacute;rio.</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF4 &ndash; Enviar ao orientador</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso envia a atividade feita pelo aluno ao seu orientador</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como aluno, dever&aacute; ser disponibilizado a atividade para que ele.</p>
<p>Entrada: Recebe como entrada a atividade resolvida.</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar ao orientador sobre o termino da atividade.</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF5 &ndash; Notificar Orientador</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso notifica a atividade feita pelo aluno ao seu orientador</p>
<p>Prioridade: Essencial</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: A atividade dever&aacute; ter sido finalizada.</p>
<p>Entrada: Recebe como entrada a atividade finalizada.</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: N&atilde;o tem</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<h3>Gerenciamento de reuni&atilde;o</h3>
<p>&nbsp;</p>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF1 &ndash; Marcar Reuni&atilde;o</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite tanto o aluno como orientador agendar uma reuni&atilde;o</p>
<p>Prioridade: Importante</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como aluno ou orientador</p>
<p>Entrada: Recebe como entrada a data da reuni&atilde;o</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; enviar uma notifica&ccedil;&atilde;o aos participantes da reuni&atilde;o para confirma&ccedil;&atilde;o</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF2 &ndash; Cancelar Reuni&atilde;o</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite tanto o aluno como orientador cancelar uma reuni&atilde;o agendada</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como aluno ou orientador e uma reuni&atilde;o dever&aacute; ter sido agendada anteriormente.</p>
<p>Entrada: Recebe como entrada a reuni&atilde;o</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; enviar uma notifica&ccedil;&atilde;o aos participantes da reuni&atilde;o sobre o cancelamento</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%; height: 39.1666px;" border="1">
<tbody>
<tr style="height: 19.5833px;">
<td style="width: 97.8656%; text-align: center; height: 19.5833px;">RF3 &ndash; Aceitar Reuni&atilde;o</td>
</tr>
<tr style="height: 19.5833px;">
<td style="width: 97.8656%; height: 19.5833px;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite tanto o aluno como orientador aceitar uma reuni&atilde;o agendada</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como aluno ou orientador e uma reuni&atilde;o dever&aacute; ter sido agendada anteriormente.</p>
<p>Entrada: Recebe como entrada a reuni&atilde;o</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; enviar uma notifica&ccedil;&atilde;o ao criador da reuni&atilde;o sobre a confirma&ccedil;&atilde;o</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF4 &ndash; Reagendar Reuni&atilde;o</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite tanto o aluno como orientador reagendar uma reuni&atilde;o agendada</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como aluno ou orientador e uma reuni&atilde;o dever&aacute; ter sido agendada anteriormente.</p>
<p>Entrada: Recebe como entrada a reuni&atilde;o e a nova data da reuni&atilde;o</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; enviar uma notifica&ccedil;&atilde;o aos participantes da reuni&atilde;o sobre o reagendamento e o pedido de confirma&ccedil;&atilde;o.</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<h3>Corre&ccedil;&atilde;o de Atividades</h3>
<p>&nbsp;</p>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF1 &ndash; Selecionar Atividade n&atilde;o corrigida</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o orientador possa selecionar uma atividade ainda n&atilde;o analisada.</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como orientador.</p>
<p>Entrada: Recebe como entrada uma atividade</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; ap&oacute;s isso poder&aacute; marcar como corrigida ou ent&atilde;o sugerir corre&ccedil;&otilde;es</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF2 &ndash; Marcar como corrigida</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o orientador possa selecionar uma atividade ainda n&atilde;o analisada.</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como orientador.</p>
<p>Entrada: Recebe como entrada uma atividade</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; ap&oacute;s isso poder&aacute; marcar como corrigida ou ent&atilde;o sugerir corre&ccedil;&otilde;es</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF2 &ndash; Marcar como corrigida</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o orientador possa marcar a atividade selecionada como corrigida.</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como orientador e ter selecionado uma atividade anteriormente.</p>
<p>Entrada: n&atilde;o tem</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar o aluno que a atividade foi corrigida e ir&aacute; disponibilizar a pr&oacute;xima atividade</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF3 &ndash; Sugerir Corre&ccedil;&otilde;es</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o orientador sugira corre&ccedil;&otilde;es para o aluno.</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como orientador e ter selecionado uma atividade anteriormente.</p>
<p>Entrada: Corre&ccedil;&otilde;es a serem feitas.</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar o aluno que a atividade n&atilde;o est&aacute; certa e ir&aacute; disponibilizar a as sugest&otilde;es de corre&ccedil;&atilde;o</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<h3>Gerenciamento de Apresenta&ccedil;&atilde;o</h3>
<p>&nbsp;</p>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF1 &ndash; Marcar Apresenta&ccedil;&atilde;o</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa marcar apresenta&ccedil;&otilde;es.</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor.</p>
<p>Entrada: Receber&aacute; como entrada uma data.</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar o aluno sobre a apresenta&ccedil;&atilde;o marcada.</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.013%;" border="1">
<tbody>
<tr>
<td style="width: 97.8656%; text-align: center;">RF2 &ndash; Marcar como concluida</td>
</tr>
<tr>
<td style="width: 97.8656%;">
<p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa marcar a apresenta&ccedil;&atilde;o como concluida.</p>
<p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor e dever&aacute; ter selecionado uma apresenta&ccedil;&atilde;o.</p>
<p>Entrada: Receber&aacute; como entrada uma apresenta&ccedil;&atilde;o.</p>
<p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; concluir a apresenta&ccedil;&atilde;o</p>
</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
<p>&nbsp;</p>
<table style="border-collapse: collapse; width: 100.028%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.9062%; text-align: center;">RF3 &ndash; Marcar presen&ccedil;a de aluno</td>
    </tr>
    <tr>
    <td style="width: 97.9062%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa marcar a presen&ccedil;a do aluno presente na apresenta&ccedil;&atilde;o.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor e dever&aacute; ter selecionado uma apresenta&ccedil;&atilde;o.</p>
    <p>Entrada: Receber&aacute; como entrada uma apresenta&ccedil;&atilde;o e o aluno.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; registrar a presen&ccedil;a do aluno</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <h3>Gerenciamento de cronograma</h3>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF1 &ndash; Criar Cronograma</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa criar um novo cronograma onde ir&aacute; conter o planejamento do ano.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor.</p>
    <p>Entrada: Receber&aacute; como entrada as datas das atividades a serem entregues.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; poder vincular aos alunos e professores a qual esse cronograma far&aacute; parte.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF2 &ndash; Vincular Aluno</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa vincular o cronograma criado aos alunos.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor e criado um cronograma.</p>
    <p>Entrada: Receber&aacute; como entrada o cronograma e os alunos.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar e apresentar os alunos sobre o cronograma criado.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF3 &ndash; Vincular Orientador</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa vincular o cronograma criado aos orientadores.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor e criado um cronograma.</p>
    <p>Entrada: Receber&aacute; como entrada o cronograma e os orientadores.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar e apresentar os orientadores sobre o cronograma criado.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF4 &ndash; Editar Cronograma</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa editar as datas postas no cronograma.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor e criado um cronograma.</p>
    <p>Entrada: Receber&aacute; como entrada o cronograma e as datas.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; alterar o cronograma existente.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <h3>Gerenciamento de Alunos</h3>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF1 &ndash; Colocar aluno como orientador</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa alterar o login do aluno para de orientador.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor.</p>
    <p>Entrada: Receber&aacute; como entrada o aluno.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar o ent&atilde;o novo orientador.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF2 &ndash; Excluir aluno</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa excluir o aluno do sistema</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor.</p>
    <p>Entrada: Receber&aacute; como entrada o aluno.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; retirar o aluno do sistema.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF3 &ndash; Vincular aluno a orientador</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa vincular um aluno ao orientador.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor.</p>
    <p>Entrada: Receber&aacute; como entrada o aluno e um orientador.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; vincular um aluno a um orientador.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <h3>Gerenciamento de Orientadores</h3>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF1 &ndash; Colocar orientador como aluno</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa alterar o login do orientador para de aluno.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor.</p>
    <p>Entrada: Receber&aacute; como entrada o orientador.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar o ent&atilde;o novo aluno.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF2 &ndash; Excluir aluno</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa excluir o orientador do sistema</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor.</p>
    <p>Entrada: Receber&aacute; como entrada o orientador.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; retirar o orientador do sistema.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <h3>Gerenciamento de Atividades</h3>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF1 &ndash; Criar Atividade</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa criar novas atividades.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor.</p>
    <p>Entrada: Receber&aacute; como entrada o conte&uacute;do da atividade.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar o aluno sobre a atividade criada.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF2 &ndash; Editar Atividade</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa editar atividades.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor e ter uma atividade selecionada para editar.</p>
    <p>Entrada: Receber&aacute; como entrada a atividade.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; notificar o aluno sobre a atividade alterada.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p>&nbsp;</p>
    <table style="border-collapse: collapse; width: 100.013%;" border="1">
    <tbody>
    <tr>
    <td style="width: 97.8656%; text-align: center;">RF3 &ndash; Criar Atividade</td>
    </tr>
    <tr>
    <td style="width: 97.8656%;">
    <p>Descri&ccedil;&atilde;o: Esse caso de uso permite que o Professor possa excluir atividades.</p>
    <p>Pr&eacute;-condi&ccedil;&otilde;es: O usu&aacute;rio dever&aacute; estar logado como professor e ter uma atividade selecionada para excluir.</p>
    <p>Entrada: Receber&aacute; como entrada a atividade.</p>
    <p>Sa&iacute;da e p&oacute;s-condi&ccedil;&otilde;es: Ir&aacute; excluir a atividade do sistema.</p>
    </td>
    </tr>
    </tbody>
    </table>
    <p><img src="TCC Control.png" width="300" height="200"></img></p>
"""
            }
        ]
    }

    json2docx(data)
