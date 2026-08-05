# import fitz

# from .base import DocumentParser
# from .models import ParsedDocument


# class PdfParser(DocumentParser):

#     async def parse(
#         self,
#         content: bytes,
#     ) -> ParsedDocument:

#         pdf = fitz.open(
#             stream=content,
#             filetype="pdf",
#         )

#         pages = []

#         for page in pdf:
#             pages.append(
#                 page.get_text()
#             )

#         metadata = pdf.metadata or {}

#         pdf.close()

#         return ParsedDocument(
#             text="\n".join(pages),
#             page_count=len(pages),
#             metadata=metadata,
#         )
