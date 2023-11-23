import time
import mathpix_f as mf
import openai_f as oaf

# set file name
filename = 'test'
headers = mf.headers
paper_field = oaf.paper_field

# OCR
response = mf.call_api(filename, headers)
pdf_id = mf.get_pdf_id(response)
mf.make_md(pdf_id, headers) # make md file

# translate markdown file
chunks, ntokens = oaf.make_chunks(pdf_id)
chunks = oaf.group_chunks(chunks, ntokens)

oaf.make_translated_markdown(chunks, filename, paper_field)


if __name__ == '__main__':
    print("Translate done")