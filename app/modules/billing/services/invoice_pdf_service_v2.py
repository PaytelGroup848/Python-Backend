from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)

def number_to_words_indian(num: int) -> str:
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    if num == 0:
        return "Zero"
    
    def convert_below_thousand(n):
        if n == 0:
            return ""
        elif n < 20:
            return units[n]
        elif n < 100:
            return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        else:
            return units[n // 100] + " Hundred" + (" " + convert_below_thousand(n % 100) if n % 100 != 0 else "")

    res = ""
    crore = num // 10000000
    num %= 10000000
    if crore > 0:
        res += convert_below_thousand(crore) + " Crore "
        
    lakh = num // 100000
    num %= 100000
    if lakh > 0:
        res += convert_below_thousand(lakh) + " Lakh "
        
    thousand = num // 1000
    num %= 1000
    if thousand > 0:
        res += convert_below_thousand(thousand) + " Thousand "
        
    if num > 0:
        res += convert_below_thousand(num)
        
    return res.strip()

def amount_to_words_inr(amount: float) -> str:
    amount = round(float(amount), 2)
    rupees = int(amount)
    paise = int(round((amount - rupees) * 100))
    
    rupees_str = number_to_words_indian(rupees) + " Rupees" if rupees > 0 else "Zero Rupees"
    if paise > 0:
        paise_str = " And " + number_to_words_indian(paise) + " Paise Only"
    else:
        paise_str = " Only"
    return rupees_str + paise_str


class InvoicePdfServiceV2: 

    async def generate(self, invoice_data):
        buffer = BytesIO()

        # A4 page width = 595.27 pt, height = 841.89 pt
        # Margins = 20 pt left/right/top/bottom -> printable width = 555.27 pt
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20,
            bottomMargin=20,
            leftMargin=20,
            rightMargin=20
        )

        base_styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=1, # Centered
            textColor=colors.black
        )

        comp_title_style = ParagraphStyle(
            'CompTitle',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.black
        )

        normal_style = ParagraphStyle(
            'CompNormal',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.black
        )

        bold_style = ParagraphStyle(
            'CompBold',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.black
        )

        tbl_hdr_style = ParagraphStyle(
            'TblHdr',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            alignment=1, # Centered
            textColor=colors.black
        )

        tbl_cell_style = ParagraphStyle(
            'TblCell',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            alignment=0, # Left
            textColor=colors.black
        )

        tbl_cell_center = ParagraphStyle(
            'TblCellCenter',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            alignment=1, # Center
            textColor=colors.black
        )

        tbl_cell_right = ParagraphStyle(
            'TblCellRight',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            alignment=2, # Right
            textColor=colors.black
        )

        footer_style = ParagraphStyle(
            'FooterText',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            alignment=1, # Centered
            textColor=colors.black
        )

        footer_italic = ParagraphStyle(
            'FooterItalic',
            parent=base_styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=10,
            alignment=1, # Centered
            textColor=colors.black
        )

        elements = []

        company = invoice_data.get("company")
        invoice = invoice_data.get("invoice")
        user = invoice_data.get("user")
        subscription = invoice_data.get("subscription")
        payment = invoice_data.get("payment")

        # Fallback objects if None
        class Dummy:
            pass

        if not company:
            company = Dummy()
            company.company_name = "PayTel Terminal Pvt Ltd.(Delhi)"
            company.address_line_1 = "A-212, 1st Floor, Phase-3"
            company.address_line_2 = "Okhla Industrial Area"
            company.city = "New Delhi"
            company.postal_code = "110020"
            company.gst_number = "07AAMCP1524F1ZK"
            company.state = "Delhi"
            company.state_code = "07"
            company.cin_number = "U74999DL2020PTC367460"
            company.support_email = "customercare@cloudedata.com"
            company.website = "www.cloudedata.com"
            company.account_holder_name = "PAYTEL TERMINAL PRIVATE LIMITED"
            company.bank_name = "ICICI Bank"
            company.account_number = "002105029512"
            company.ifsc_code = "Defence Colony, Delhi-110020 ICIC0006300"

        company_name = getattr(company, 'company_name', None) or "PayTel Terminal Pvt Ltd.(Delhi)"
        address1 = getattr(company, 'address_line_1', None) or "A-212, 1st Floor, Phase-3"
        address2 = getattr(company, 'address_line_2', None) or "Okhla Industrial Area"
        city_pin = f"{getattr(company, 'city', '') or 'New Delhi'}-{getattr(company, 'postal_code', '') or '110020'}"
        gstin = getattr(company, 'gst_number', None) or "07AAMCP1524F1ZK"
        state_name = getattr(company, 'state', None) or "Delhi"
        state_code = getattr(company, 'state_code', None) or "07"
        cin = getattr(company, 'cin_number', None) or "U74999DL2020PTC367460"
        email = getattr(company, 'support_email', None) or "customercare@cloudedata.com"
        website = getattr(company, 'website', None) or "www.cloudedata.com"

        bank_holder = getattr(company, 'account_holder_name', None) or "PAYTEL TERMINAL PRIVATE LIMITED"
        bank_name = getattr(company, 'bank_name', None) or "ICICI Bank"
        bank_acc = getattr(company, 'account_number', None) or "002105029512"
        bank_ifsc = getattr(company, 'ifsc_code', None) or "Defence Colony, Delhi-110020 ICIC0006300"

        # Dynamic Invoice & Date details from Database
        invoice_num = getattr(invoice, 'invoice_number', None) or (f"INV-{getattr(invoice, 'id', 1):06d}")
        created_dt = getattr(invoice, 'created_at', None)
        if isinstance(created_dt, datetime):
            inv_date = created_dt.strftime('%Y-%m-%d')
        elif created_dt:
            inv_date = str(created_dt)[:10]
        else:
            inv_date = datetime.now().strftime('%Y-%m-%d')

        # Dynamic User / Buyer Information from Database
        buyer_name = getattr(user, 'full_name', None) or getattr(user, 'name', None) or getattr(user, 'username', None) or (getattr(user, 'email', '').split('@')[0] if getattr(user, 'email', None) else "Customer")
        buyer_email = getattr(user, 'email', None) or "-"
        buyer_contact = getattr(user, 'phone', None) or getattr(user, 'phone_number', None) or "-"

        # Dynamic Invoice Amounts from Database
        subtotal = float(getattr(invoice, 'subtotal', 0.0) or 0.0)
        tax_amount = float(getattr(invoice, 'tax_amount', 0.0) or 0.0)
        total_amount = float(getattr(invoice, 'amount', 0.0) or (subtotal + tax_amount))
        hsn_code = "998315"

        # Dynamic Subscription / Service Plan Description from Database
        raw_plan = getattr(subscription, 'plan_name', None) or getattr(invoice, 'notes', None) or getattr(invoice, 'invoice_type', 'Subscription Plan')
        plan_desc = str(raw_plan)
        if "Service" not in plan_desc and "Subscription" not in plan_desc:
            plan_desc += " Subscription - Service"


        # 1. TAX INVOICE Title
        elements.append(Paragraph("Tax Invoice", title_style))
        elements.append(Spacer(1, 10))

        # 2. Company Info + Invoice Details Top Box
        left_info = f"""
        <b>{company_name}</b><br/>
        {address1}<br/>
        {address2}<br/>
        {city_pin}<br/>
        <b>GSTIN/UIN:</b> {gstin}<br/>
        <b>State Name:</b> {state_name}, <b>Code:</b> {state_code}<br/>
        <b>CIN:</b> {cin}<br/>
        <b>E-Mail:</b> {email}<br/>
        {website}
        """

        right_info = f"""
        <b>Invoice No.</b><br/>
        {invoice_num}<br/><br/>
        <b>Dated</b><br/>
        {inv_date}
        """

        top_table = Table(
            [[Paragraph(left_info, normal_style), Paragraph(right_info, normal_style)]],
            colWidths=[370, 185]
        )
        top_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(top_table)
        elements.append(Spacer(1, 12))

        # 3. Buyer (Bill to)
        buyer_html = f"""
        <b>Buyer (Bill to)</b><br/>
        <b>{buyer_name}</b><br/>
        Contact : {buyer_contact}<br/>
        E-Mail : {buyer_email}
        """
        elements.append(Paragraph(buyer_html, normal_style))
        elements.append(Spacer(1, 10))

        # 4. Service Details Table
        # Columns: Sl No | Description of Services | HSN/SAC | Quantity | Rate per | Rate (Incl. of Tax) | Amount
        # Total width = 555 pt
        service_table_data = [
            [
                Paragraph("Sl No", tbl_hdr_style),
                Paragraph("Description of Services", tbl_hdr_style),
                Paragraph("HSN/SAC", tbl_hdr_style),
                Paragraph("Quantity", tbl_hdr_style),
                Paragraph("Rate per", tbl_hdr_style),
                Paragraph("Rate (Incl. of Tax)", tbl_hdr_style),
                Paragraph("Amount", tbl_hdr_style),
            ],
            [
                Paragraph("1", tbl_cell_center),
                Paragraph(plan_desc, tbl_cell_style),
                Paragraph(hsn_code, tbl_cell_center),
                Paragraph("1 No.", tbl_cell_center),
                Paragraph(f"{subtotal:.2f}", tbl_cell_right),
                Paragraph(f"{total_amount:.2f}", tbl_cell_right),
                Paragraph(f"{subtotal:.2f}", tbl_cell_right),
            ]
        ]
        service_table = Table(service_table_data, colWidths=[35, 185, 60, 55, 70, 80, 70])
        service_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F2F2F2')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(service_table)
        elements.append(Spacer(1, 8))

        # 5. Tax Breakdown Title & Amount Chargable in words
        elements.append(Paragraph(f"<b>CGST+SGST Output-18% ({state_name})</b>", bold_style))
        elements.append(Spacer(1, 4))
        words_total = amount_to_words_inr(total_amount)
        elements.append(Paragraph(f"<b>Amount Chargable (in words)</b><br/><b>{words_total}</b>", normal_style))
        elements.append(Spacer(1, 8))

        # 6. HSN/SAC Tax Summary Table
        # Columns: HSN/SAC | Taxable Value | GST Value | Total Amount
        hsn_table_data = [
            [
                Paragraph("HSN/SAC", tbl_hdr_style),
                Paragraph("Taxable Value", tbl_hdr_style),
                Paragraph("GST Value", tbl_hdr_style),
                Paragraph("Total Amount", tbl_hdr_style),
            ],
            [
                Paragraph(hsn_code, tbl_cell_center),
                Paragraph(f"{subtotal:.2f}", tbl_cell_right),
                Paragraph(f"{tax_amount:.2f}", tbl_cell_right),
                Paragraph(f"{total_amount:.2f}", tbl_cell_right),
            ]
        ]
        hsn_table = Table(hsn_table_data, colWidths=[140, 140, 135, 140])
        hsn_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F2F2F2')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(hsn_table)
        elements.append(Spacer(1, 6))

        # 7. Tax Amount in words
        words_tax = amount_to_words_inr(tax_amount)
        elements.append(Paragraph(f"<b>Tax Amount (in words) : {words_tax}</b>", bold_style))
        elements.append(Spacer(1, 10))

        # 8. Company Bank Details
        bank_html = f"""
        <b>Company's Bank Details</b><br/>
        Account Holder's Name : {bank_holder}<br/>
        Bank Name : {bank_name}<br/>
        Account Number : {bank_acc}<br/>
        Branch & IFSC Code : {bank_ifsc}
        """
        elements.append(Paragraph(bank_html, normal_style))
        elements.append(Spacer(1, 10))

        # 9. Declaration & Terms & Conditions
        terms_html = f"""
        <b>Declaration</b><br/>
        <b>Terms & Conditions:</b><br/>
        • Support Other Than Cloud Services will not be Provided.<br/>
        • For Software related query, Kindly Contact to the respected Software Company only.<br/><br/>
        <i>This Agreement shall be governed by the laws of India, and any disputes shall fall under the exclusive jurisdiction of the courts at New Delhi.</i>
        """
        elements.append(Paragraph(terms_html, normal_style))
        elements.append(Spacer(1, 15))

        # 10. Signatory
        signatory_html = f"<b>{company_name}</b>"
        sign_table = Table([[Paragraph(signatory_html, tbl_cell_right)]], colWidths=[555])
        sign_table.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(sign_table)
        elements.append(Spacer(1, 20))

        # 11. Footer Line & Jurisdiction
        elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceBefore=5, spaceAfter=5))
        elements.append(Paragraph("SUBJECT TO DELHI JURISDICTION", footer_style))
        elements.append(Paragraph("This is a System Generated Invoice", footer_italic))

        pdf.build(elements)
        buffer.seek(0)
        return buffer


invoice_pdf_service_v2 = InvoicePdfServiceV2()