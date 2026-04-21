import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle

def generate_breed_report(prediction_data: dict) -> io.BytesIO:
    """
    Generates a PDF report for a cattle breed prediction.
    prediction_data should contain:
    - breed_name: Predicted breed name
    - confidence: Confidence percentage
    - original_image_path: Path to the uploaded image
    - heatmap_image_path: Path to the Grad-CAM heatmap
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=1, # Center
        fontSize=24,
        spaceAfter=20,
        textColor=colors.HexColor("#16a34a") # Brand green styling
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 12
    normal_style.spaceAfter = 10
    
    story = []
    
    # 1. Header
    story.append(Paragraph("<b>BreedSense AI</b> - Analysis Report", title_style))
    story.append(Spacer(1, 10))
    
    # 2. Date
    date_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    story.append(Paragraph(f"<b>Date of Analysis:</b> {date_str}", normal_style))
    story.append(Spacer(1, 15))
    
    # 3. Prediction Info Table
    data = [
        ["Predicted Breed", prediction_data.get('breed_name', 'Unknown')],
        ["Confidence Score", f"{prediction_data.get('confidence', 0)}%"]
    ]
    t = Table(data, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ('PADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t)
    story.append(Spacer(1, 30))
    
    # 4. Images (Original & Heatmap) side by side
    images_row = []
    
    # helper for resolving actual absolute path if relative to app
    def get_abs_path(path):
        if not path: return None
        return os.path.abspath(path)
        
    orig_path = get_abs_path(prediction_data.get('original_image_path'))
    if orig_path and os.path.exists(orig_path):
        img_orig = Image(orig_path, width=200, height=200, kind='proportional')
        images_row.append(img_orig)
    else:
        images_row.append(Paragraph("<i>Original image unavailable.</i>", normal_style))
        
    heat_path = get_abs_path(prediction_data.get('heatmap_image_path'))
    if heat_path and os.path.exists(heat_path):
        img_heat = Image(heat_path, width=200, height=200, kind='proportional')
        images_row.append(img_heat)
    else:
        images_row.append(Paragraph("<i>Heatmap unavailable.</i>", normal_style))
        
    img_table = Table([[images_row[0], images_row[1]]], colWidths=[250, 250])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(img_table)
    
    # 5. Image Labels
    label_data = [["Original Upload", "Grad-CAM Heatmap"]]
    label_table = Table(label_data, colWidths=[250, 250])
    label_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.darkgrey),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(label_table)
    
    # Footer Note
    story.append(Spacer(1, 40))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=1, textColor=colors.grey, fontSize=9)
    story.append(Paragraph("Generated automatically by BreedSense AI - Cattle Breed Recognition System.", footer_style))
    
    doc.build(story)
    
    # Reset buffer pointer to beginning so it can be read
    buf.seek(0)
    return buf
