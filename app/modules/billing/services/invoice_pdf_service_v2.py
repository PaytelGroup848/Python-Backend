from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


class InvoicePdfServiceV2:

    async def generate(
        self,
        invoice_data
    ):

        buffer = BytesIO()

        pdf = SimpleDocTemplate(
            buffer,
            pagesize = A4,
            topMargin=20,
            bottomMargin=20,
            leftMargin=20,
            rightMargin=20
        )

        styles = (
            getSampleStyleSheet()
        )

        elements = []

        company = (
            invoice_data["company"]
        )

        invoice = (
            invoice_data["invoice"]
        )

        user = (
            invoice_data["user"]
        )

        subscription = (
            invoice_data["subscription"]
        )

        payment = (
            invoice_data["payment"]
        )

        currency_symbol = (

            invoice.currency_symbol

            or company.currency_symbol

            or invoice.currency
        )

        # =====================================
        # COMPANY HEADER
        # =====================================

        elements.append(
            Paragraph(
                f"<b>{company.company_name}</b>",
                styles["Title"]
            )
        )
        elements.append(
             Paragraph(
                "TAX INVOICE",
                styles["Heading1"]
            )
        )

        elements.append(
            Spacer(1, 6)
        )


        elements.append(
            Paragraph(
                company.address_line_1 or "",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                company.address_line_2 or "",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"{company.city or ''}, "
                f"{company.state or ''}, "
                f"{company.country or ''} "
                f"{company.postal_code or ''}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"GSTIN/UIN: {company.gst_number or '-'}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"CIN: {company.cin_number or '-'}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Email: {company.support_email or '-'}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                company.website or "-",
                styles["Normal"]
            )
        )

        elements.append(
            Spacer(1, 6)
        )


        # =====================================
        # BUYER DETAILS
        # =====================================

        elements.append(
            Paragraph(
                "<b>Bill To</b>",
                styles["Heading2"]
            )
        )

        elements.append(
            Paragraph(
                f"""
                {user.name}<br/>
                {user.email}
                """,
                styles["Normal"]
            )
        )

        elements.append(
            Spacer(1, 8)
        )

        # =====================================
        # SERVICE DETAILS
        # =====================================

        elements.append(
            Paragraph(
                "Service Details",
                styles["Heading2"]
            )
        )

        service_table = Table(

            [      
                [
                    "Description",
                    "Qty",
                    "Amount"
                ],

                [
                    (
                        f"{subscription.plan_name} Subscription"
                        if subscription
                        else invoice.invoice_type
                    ),

                    "1",

                    f"{currency_symbol} {invoice.subtotal}"
                ]
            ],

            colWidths=[
                300,
                80,
                120
            ]
        )

        service_table.setStyle(

            TableStyle([

                ("GRID",(0,0),(-1,-1),1,colors.black),

                ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
            ])
        )

        elements.append(
            service_table
        )

        elements.append(
            Spacer(1,6)
        )

        # =====================================
        # TAX SUMMARY
        # =====================================

        elements.append(
            Paragraph(
                "Invoice Summary",
                styles["Heading2"]
            )
        )

        amount_table = Table(

            [

                [
                    "Subtotal",
                    f"{currency_symbol} {invoice.subtotal}"
                ],

                [
                    "GST",
                    f"{currency_symbol} {invoice.tax_amount}"
                ],

                [
                    "TOTAL",
                    f"{currency_symbol} {invoice.amount}"
                ]
            ],

            colWidths=[
                180,
                120
            ]
        )

        amount_table.setStyle(

            TableStyle([

                ("GRID",(0,0),(-1,-1),1,colors.black),

                ("BACKGROUND",(0,2),(-1,2),colors.lightgrey),

                ("FONTNAME",(0,2),(-1,2),"Helvetica-Bold")
            ])
        )

        elements.append(
            amount_table
        )

        elements.append(
            Spacer(1,6)
        )
        # =====================================
        # PAYMENT DETAILS
        # =====================================

        if payment:

            elements.append(
                Paragraph(
                    "Payment Details",
                    styles["Heading2"]
                )
            )

            elements.append(
                Paragraph(
                    f"""
                    <b>Provider:</b> {payment.provider or '-'}<br/>
                    <b>Reference:</b> {payment.payment_reference or '-'}<br/>
                    <b>Status:</b> {payment.status or '-'}
                    """,
                    styles["Normal"]
                )
            )

            elements.append(
                Spacer(1,6)
            )
                

        # =====================================
        # BANK DETAILS
        # =====================================
        
        elements.append(
            Paragraph(
                "Company Bank Details",
                styles["Heading2"]
            )
        )

        elements.append(
            Paragraph(
                f"""
                <b>Account Holder:</b> {company.account_holder_name or '-'}<br/>
                <b>Bank Name:</b> {company.bank_name or '-'}<br/>
                <b>Account Number:</b> {company.account_number or '-'}<br/>
                <b>IFSC:</b> {company.ifsc_code or '-'}
                """,
                styles["Normal"]
            )
        )

        elements.append(
            Spacer(1,6)
        )
        
               

        # =====================================
        # TERMS
        # =====================================

        elements.append(
            Paragraph(
                "Terms & Conditions",
                styles["Heading2"]
            )
        )

        elements.append(
            Paragraph(
                company.terms_and_conditions 
                or "Subscription fees are non-refundable unless required by law.",
                styles["Normal"]
            )
        )

        elements.append(
            Spacer(1,6)
        )

        # =====================================
        # FOOTER
        # =====================================

        elements.append(
            Paragraph(
                company.invoice_footer
                or "This is a System Generated Invoice",
                styles["Italic"]
            )
        )

        pdf.build(
            elements
        )

        buffer.seek(0)

        return buffer


invoice_pdf_service_v2 = (
    InvoicePdfServiceV2()
)