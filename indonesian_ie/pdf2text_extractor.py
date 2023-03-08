#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

import PyPDF2
import pdfplumber
import textract
from PyPDF4 import PdfFileReader, PdfFileWriter
from PyPDF4.generic import NameObject, TextStringObject
from PyPDF4.pdf import ContentStream
from PyPDF4 import utils as pdf_utils

from indonesian_ie.base_extractor import BaseExtractor


def remove_watermark(wmText, inputFile, outputFile):
    with open(inputFile, "rb") as f:
        source = PdfFileReader(f, "rb")
        output = PdfFileWriter()

        for page in range(source.getNumPages()):
            page = source.pages[page]
            content_object = page["/Contents"].getObject()
            content = ContentStream(content_object, source)

            for operands, operator in content.operations:
                if operator == pdf_utils.b_("Tj"):
                    text = operands[0]

                    for i in wmText:
                        if isinstance(text, str) and text.startswith(i):
                            operands[0] = TextStringObject('')

            page.__setitem__(NameObject('/Contents'), content)
            output.addPage(page)

        with open(outputFile, "wb") as outputStream:
            output.write(outputStream)


def watermark_text(inputFile, waterMarkTextStarting):
    # This Function reads the PDF file and searches for input string and deletes the WaterMark

    wmText = []
    pdfFileObj = open(inputFile, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    page_number = 0
    pageObj = pdfReader.pages[page_number]
    watermark = pageObj.extract_text()
    pdfFileObj.close()
    x = watermark.find(waterMarkTextStarting)
    lengthWmText = len(waterMarkTextStarting)
    wmText.append(watermark[x : x + lengthWmText])
    wmText.append(watermark[x + lengthWmText :])
    return wmText


def get_disclaimer(inputFile):
    anchor_start = 'Disclaimer'
    anchor_end = 'Halaman'
    wmText = []
    pdfFileObj = open(inputFile, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    page_number = 0
    pageObj = pdfReader.pages[page_number]
    watermark = pageObj.extract_text()
    pdfFileObj.close()
    # text between anchor_start and anchor_end
    start = watermark.find(anchor_start)
    end = start + watermark[start:].find(anchor_end)
    text = watermark[start:end]
    lengthWmText = len(text)
    wmText.append(watermark[start : start + lengthWmText])
    wmText.append(watermark[start + lengthWmText :])
    return wmText


def remove_watermark_disclaimer(inputFile, outputFile):
    """
    removing text layer from pdf that contains the disclaimer and watermark
    only works for putusan pdf files
    """

    wmText = get_disclaimer(inputFile)
    with open(inputFile, "rb") as f:
        source = PdfFileReader(f, "rb")
        output = PdfFileWriter()

        for page in range(source.getNumPages()):
            page = source.pages[page]
            content_object = page["/Contents"].getObject()
            content = ContentStream(content_object, source)

            for operands, operator in content.operations:
                if operator == pdf_utils.b_("Tj"):
                    text = operands[0]
                    if isinstance(text, str):
                        operands[0] = TextStringObject('')

            page.__setitem__(NameObject('/Contents'), content)
            output.addPage(page)

        with open(outputFile, "wb") as outputStream:
            output.write(outputStream)


def preprocess_putusan_fn(input_file, output_file):
    waterMarkTextStarting = 'Mahkamah Agung'
    wm_text = watermark_text(input_file, waterMarkTextStarting)
    # remove_watermark(wm_text, input_file, output_file)
    remove_watermark_disclaimer(input_file, output_file)


class Pdf2TextExtractor(BaseExtractor):

    def __init__(
        self, backend: str, preprocess_fn: callable = preprocess_putusan_fn, **kwargs
    ):
        super().__init__(**kwargs)
        self.backend = backend
        self.preprocess_fn = preprocess_fn

        assert self.backend in [
            'pdfminer',
            'pdfplumber',
            'tesseract',
            'pdftotext',
            'pymupdf',
        ]

    def _extract(self, input_file, *args, **kwargs):
        if self.preprocess_fn:
            input_file_preprocessed = (
                Path(input_file).parent / f'{Path(input_file).stem}_preprocessed.pdf'
            )
            self.preprocess_fn(input_file, input_file_preprocessed)
            input_file = input_file_preprocessed
        if self.backend == 'pdfplumber':
            with pdfplumber.open(input_file) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    yield page_num, page.extract_text()
        elif self.backend == 'pymupdf':
            import fitz

            doc = fitz.open(input_file)
            # metadata = doc.metadata
            for page_num, page in enumerate(doc, 1):
                yield page_num, page.get_text()
        else:
            text = textract.process(input_file, method=self.backend)
            yield text.decode('utf-8')

    def get_num_pages(self, input_file):
        if self.backend == 'pdfplumber':
            with pdfplumber.open(input_file) as pdf:
                return len(pdf.pages)
        elif self.backend == 'pymupdf':
            import fitz

            doc = fitz.open(input_file)
            return len(doc)
        else:
            raise NotImplementedError
