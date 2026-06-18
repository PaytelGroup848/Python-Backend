from io import BytesIO

from reportlab.lib import colors

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


class InvoicePdfService:

    def generate_invoice_pdf(
        self,
        invoice
    ):

        buffer = BytesIO()

        pdf = SimpleDocTemplate(
            buffer
        )

        styles = (
            getSampleStyleSheet()
        )

        elements = []

        elements.append(
            Paragraph(
                f"Invoice #{invoice.invoice_number}",
                styles["Title"]
            )
        )

        elements.append(
            Spacer(1, 20)
        )

        data = [

            ["Invoice Number", invoice.invoice_number],

            ["Invoice Type", invoice.invoice_type],

            ["Amount", str(invoice.amount)],

            ["Currency", invoice.currency],

            ["Status", invoice.status],

            ["Due Date", str(invoice.due_date)],

            ["Created", str(invoice.created_at)]
        ]

        table = Table(data)

        table.setStyle(
            TableStyle([

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    1,
                    colors.black
                ),

                (
                    "BACKGROUND",
                    (0,0),
                    (0,-1),
                    colors.lightgrey
                )
            ])
        )

        elements.append(
            table
        )

        pdf.build(
            elements
        )

        buffer.seek(0)

        return buffer


invoice_pdf_service = (
    InvoicePdfService()
)