import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.colors import green, red
import io

def annotate_pdf_with_bbox(document_name = "i20.pdf"):
    """Annotate a PDF document with bounding boxes from Textract analysis results."""
    input_pdf_path = "input_pdf/" + document_name
    output_pdf_path = "output_pdf/" + document_name.replace(".pdf", "_annotated.pdf")
    geometry_json_path = "geometry_info/" + document_name.replace(".pdf", "_filtered_signature_key_value_pairs.json")

    with open(geometry_json_path, 'r') as f:
        data = json.load(f)
    
    blocks = data.get('Blocks', [])
    
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    for page_num, page in enumerate(reader.pages):
        # Get page dimensions
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # Draw rectangles for each block on this page
        current_page = page_num + 1  # Page numbers are 1-indexed
        has_annotations = False
        
        # Create overlay with bounding boxes
        packet = io.BytesIO()
        overlay_canvas = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        for block in blocks:
            # Only process blocks for the current page
            block_page = block.get('Page', 1)
            if block_page != current_page:
                continue
            
            entity_types = block.get('EntityTypes', [])
            geometry = block.get('Geometry', {})
            bbox = geometry.get('BoundingBox', {})
            
            if not bbox:
                continue
            
            # Convert normalized coordinates to PDF coordinates
            left = bbox['Left'] * page_width
            top = page_height - (bbox['Top'] * page_height)  # PDF coordinates are bottom-up
            width = bbox['Width'] * page_width
            height = bbox['Height'] * page_height
            
            # Set color based on entity type
            if 'KEY' in entity_types:
                overlay_canvas.setStrokeColor(green)
            elif 'VALUE' in entity_types:
                overlay_canvas.setStrokeColor(red)
            else:
                continue  # Skip blocks without KEY or VALUE entity type
            
            overlay_canvas.setLineWidth(2)
            overlay_canvas.rect(left, top - height, width, height, fill=0)
            has_annotations = True
        
        overlay_canvas.save()
        
        # Merge overlay with original page only if there are annotations
        if has_annotations:
            packet.seek(0)
            overlay_pdf = PdfReader(packet)
            page.merge_page(overlay_pdf.pages[0])
        
        writer.add_page(page)
    
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"Annotated PDF saved as {output_file}")
    print("-----------------------------------------------------------")

if __name__ == "__main__":
    input_pdf = "input_pdf/i20.pdf"
    geometry_json = "geometry_info/filtered_signature_key_value_pairs.json"
    output_pdf = "output_pdf/output_pdf.pdf"
    
    annotate_pdf_with_bbox(input_pdf, geometry_json, output_pdf)
    print(f"Annotated PDF saved as {output_pdf}")

# python3 annotate_pdf.py i20.pdf sample_geometry.json output.pdf