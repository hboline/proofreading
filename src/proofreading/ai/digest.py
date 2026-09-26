import pymupdf
import tkinter as tk
from tkinter import filedialog
import re

def get_filename() -> str:
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select paper",
        filetypes=[("PDF","*.pdf")],
    )
    return file_path

def load_document(filename: str) -> dict[int, str]:
    doc: pymupdf.Document = pymupdf.open(filename=filename)
    pages: dict[int, str] = {
        page_num: re.sub("\n"," ",page.get_text())
        for page_num, page in enumerate(doc.pages(), start=1)
    }
    return pages

