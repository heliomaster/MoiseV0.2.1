from docxtpl import DocxTemplate


class docxTemplateCreation():

    def create_docx_document(self, filename):
        doc = DocxTemplate(filename)
        context = {'company_name': "World company", 'my_name': "Marc Morgand"}
        doc.render(context)
        doc.save("template_generated_doc.docx")


if __name__ == '__main__':
    p = docxTemplateCreation()
    p.create_docx_document("template_try.docx")

# doc = DocxTemplate("template_try.docx")
# # context = { 'company_name' : "World company" }
# context = {'company_name': "World company"}
# doc.render(context)
# doc.save("template_generated_doc.docx")
