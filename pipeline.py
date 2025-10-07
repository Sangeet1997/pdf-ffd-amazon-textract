from extract_form_data import extract_form_data
from filter_signature_keys import filter_signature_key_value_pairs
from annotate_pdf import annotate_pdf_with_bbox
import sys
import os

def single_job(document_name = 'i20.pdf', input_path = 'input_pdf/'):
    extract_form_data(document_name=document_name, input_path=input_path)
    filter_signature_key_value_pairs(document_name=document_name)
    annotate_pdf_with_bbox(document_name=document_name, input_path=input_path)

# def job_without_textract(document_name = 'i20.pdf'):
#     filter_signature_key_value_pairs(document_name=document_name)
#     annotate_pdf_with_bbox(document_name=document_name)

def batch_job():
    batch_folder = "batch_input/"
    document_names = [f for f in os.listdir(batch_folder) if f.endswith('.pdf')]
    for document_name in document_names:
        print(f"Processing {document_name}...")
        print("-------------------------------------")
        single_job(document_name=document_name, input_path=batch_folder)

if __name__ == "__main__":
    document_name = sys.argv[1] if len(sys.argv) > 1 else 'i20.pdf'
    # single_job(document_name=document_name)
    batch_job()
    # job_without_textract(document_name=document_name)