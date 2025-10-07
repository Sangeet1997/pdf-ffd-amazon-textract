import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.colors import green, red
import io

def annotate_pdf_with_bbox(input_pdf_path, geometry_json_path, output_pdf_path):
    with open(geometry_json_path, 'r') as f:
        data = json.load(f)
    
    blocks = data.get('Blocks', [])
    
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    for page_num, page in enumerate(reader.pages):
        # Get page dimensions
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        # Create overlay with bounding boxes
        packet = io.BytesIO()
        overlay_canvas = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        # Draw rectangles for each block
        for block in blocks:
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
        
        overlay_canvas.save()
        
        # Merge overlay with original page
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)
    
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)

if __name__ == "__main__":
    input_pdf = "input_pdf/i20.pdf"
    geometry_json = "geometry_info/filtered_signature_key_value_pairs.json"
    output_pdf = "output_pdf/output_pdf.pdf"
    
    annotate_pdf_with_bbox(input_pdf, geometry_json, output_pdf)
    print(f"Annotated PDF saved as {output_pdf}")

# python3 annotate_pdf.py i20.pdf sample_geometry.json output.pdf