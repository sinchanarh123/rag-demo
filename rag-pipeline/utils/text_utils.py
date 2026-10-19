import pdfplumber
import io
from langchain.text_splitter import CharacterTextSplitter

class TextUtils:
    @staticmethod
    def convert_to_uppercase(text):
        return text.upper()
    
    
    @staticmethod
    def pdf_to_text(pdf_bytes: bytes) -> str:
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text

    @staticmethod
    def get_chunks(text: str, chunk_size: int = 450, overlap: int = 75):
        
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size,      # Max size of each chunk
            chunk_overlap=overlap,    # Amount of overlap
            separator=" ",    # Primary separator
            length_function=len, # Use character count as length metric
        )
        print("Splitting text into chunks...")

        # Split the text
        chunks = text_splitter.split_text(text)
        return chunks
