from extract_form_data import extract_form_data
from filter_signature_keys import filter_signature_key_value_pairs
from annotate_pdf import annotate_pdf_with_bbox
import sys

def single_job(document_name = 'i20.pdf'):
    extract_form_data(document_name=document_name)
    filter_signature_key_value_pairs(document_name=document_name)
    annotate_pdf_with_bbox(document_name=document_name)

def job_without_textract(document_name = 'i20.pdf'):
    filter_signature_key_value_pairs(document_name=document_name)
    annotate_pdf_with_bbox(document_name=document_name)

if __name__ == "__main__":
    document_name = sys.argv[1] if len(sys.argv) > 1 else 'i20.pdf'
    # single_job(document_name=document_name)
    job_without_textract(document_name=document_name)