import PyPDF2


def pdf_to_txt(pdf_path):
    text_extracted=''
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        # Create a PDF reader
        reader = PyPDF2.PdfReader(file)

        # Loop through all the pages
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                text_extracted +=  text

        return text_extracted