import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import logging

logger = logging.getLogger("uvicorn")

class PDFReportService:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
        self.reports_dir = os.path.join(project_root, "backend", "generated", "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_report(self, report_id, patient, scan, prediction, image_path, gradcam_path=None):
        filename = f"Radiology_Report_{patient['patientId']}_{report_id}.pdf"
        file_path = os.path.join(self.reports_dir, filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1E293B'), alignment=1, spaceAfter=4)
        subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=14)
        h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#6C4CF5'), spaceAfter=8, spaceBefore=10)
        normal_style = styles["Normal"]
        disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Italic'], fontSize=8, textColor=colors.HexColor('#64748B'), spaceBefore=15)

        Story = []

        # Header Title
        Story.append(Paragraph("<b>AI-POWERED DIAGNOSIS SUPPORT</b>", title_style))
        Story.append(Paragraph("<b>MEDICAL IMAGING REPORT</b>", subtitle_style))
        
        now = datetime.utcnow()
        report_details_data = [
            ["Report ID:", report_id, "Generated Date:", now.strftime('%Y-%m-%d')],
            ["Patient ID:", patient['patientId'], "Generated Time:", now.strftime('%H:%M:%S UTC')]
        ]
        t_rep = Table(report_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        t_rep.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4)
        ]))
        Story.append(t_rep)
        Story.append(Spacer(1, 10))

        # 1. Patient Details
        Story.append(Paragraph("<b>PATIENT DETAILS</b>", h2_style))
        patient_data = [
            ["Patient ID:", patient['patientId'], "Age:", str(patient['age'])],
            ["Patient Name:", patient['patientName'], "Gender:", str(patient['gender']).capitalize()],
            ["Case Type:", scan.get('caseType', 'NORMAL').upper(), "", ""]
        ]
        t_patient = Table(patient_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        t_patient.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3)
        ]))
        Story.append(t_patient)
        Story.append(Spacer(1, 10))

        # 2. Scan Details
        Story.append(Paragraph("<b>SCAN DETAILS</b>", h2_style))
        img_val = prediction.get('imageValidation', {})
        val_status = "Valid" if img_val.get('imageValid', True) else "Invalid"
        quality_status = img_val.get('qualityStatus', 'Acceptable')
        
        upload_date_str = scan['uploadedAt'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(scan['uploadedAt'], datetime) else str(scan['uploadedAt'])
        
        scan_data = [
            ["Scan Type:", scan['scanType'], "File Name:", scan['fileName']],
            ["Upload Date:", upload_date_str, "Image Validation:", val_status],
            ["Image Quality:", quality_status, "", ""]
        ]
        t_scan = Table(scan_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        t_scan.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3)
        ]))
        Story.append(t_scan)
        Story.append(Spacer(1, 10))

        # 3. Medical Images (Original Scan & Grad-CAM)
        Story.append(Paragraph("<b>ORIGINAL SCAN & EXPLAINABLE AI</b>", h2_style))
        
        images_row = []
        if os.path.exists(image_path):
            try:
                img = Image(image_path, width=2.6*inch, height=2.6*inch, kind='proportional')
                images_row.append(img)
            except Exception as e:
                logger.error(f"Failed to add original image to PDF: {e}")
                images_row.append(Paragraph("Original Image Unavailable", normal_style))
        else:
            images_row.append(Paragraph("Original Image Unavailable", normal_style))

        if gradcam_path and os.path.exists(gradcam_path):
            try:
                gc_img = Image(gradcam_path, width=2.6*inch, height=2.6*inch, kind='proportional')
                images_row.append(gc_img)
            except Exception as e:
                logger.error(f"Failed to add Grad-CAM image to PDF: {e}")
                images_row.append(Paragraph("Grad-CAM Heatmap Unavailable", normal_style))
        else:
            images_row.append(Paragraph("Grad-CAM Heatmap Unavailable", normal_style))

        img_table = Table([images_row], colWidths=[3.5*inch, 3.5*inch])
        Story.append(img_table)
        
        caption_table = Table([["Original Scan", "AI Heatmap (Grad-CAM Visualization)"]], colWidths=[3.5*inch, 3.5*inch])
        caption_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#64748B')),
            ('FONTSIZE', (0,0), (-1,-1), 8)
        ]))
        Story.append(caption_table)
        Story.append(Spacer(1, 10))

        # 4. AI Analysis
        Story.append(Paragraph("<b>AI ANALYSIS</b>", h2_style))
        conf_pct_str = f"{(prediction['confidence'] * 100):.2f}%"
        analysis_data = [
            ["Model Used:", prediction['model']],
            ["Possible Finding:", prediction['possibleFinding']],
            ["Confidence Score:", conf_pct_str],
            ["Confidence Level:", prediction['confidenceLevel']]
        ]
        t_analysis = Table(analysis_data, colWidths=[2*inch, 5*inch])
        t_analysis.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3)
        ]))
        Story.append(t_analysis)
        Story.append(Spacer(1, 10))

        # 5. AI Analysis Reason
        Story.append(Paragraph("<b>AI ANALYSIS REASON</b>", h2_style))
        cause_p = Paragraph(prediction.get('possibleCause', 'N/A'), normal_style)
        t_cause = Table([[cause_p]], colWidths=[7*inch])
        t_cause.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        Story.append(t_cause)
        Story.append(Spacer(1, 10))

        # 6. Doctor Review
        Story.append(Paragraph("<b>DOCTOR REVIEW</b>", h2_style))
        review_data = [
            ["Review Status:", prediction.get('reviewStatus', 'Pending Radiologist Review')],
            ["Doctor Name:", prediction.get('reviewedBy', 'Pending Radiologist Review')],
            ["Doctor Notes:", prediction.get('doctorNotes', 'No notes added yet.')]
        ]
        t_review = Table(review_data, colWidths=[2*inch, 5*inch])
        t_review.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3)
        ]))
        Story.append(t_review)
        Story.append(Spacer(1, 15))

        # 7. Disclaimer
        Story.append(Paragraph(
            "<b>DISCLAIMER:</b> This AI analysis is intended for educational and clinical decision support research only. It does not represent a final medical diagnosis. Final interpretation must be performed by a qualified healthcare professional.", 
            disclaimer_style
        ))

        # Build PDF
        try:
            doc.build(Story)
            return f"/api/static/reports/{filename}"
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            return None

pdf_report_service = PDFReportService()
