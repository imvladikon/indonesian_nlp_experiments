#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import textract
import pdfminer
import pdfplumber
from PyPDF4 import PdfFileReader, PdfFileWriter
from PyPDF4.pdf import ContentStream
from PyPDF4.generic import TextStringObject, NameObject
from PyPDF4.utils import b_
import PyPDF2
import os
import time
import shutil


def remove_watermark(wmText, inputFile, outputFile):
    # This Function Reads PDF file and Removes the WATERMARK TEXT

    with open(inputFile, "rb") as f:
        source = PdfFileReader(f, "rb")
        output = PdfFileWriter()

        for page in range(source.getNumPages()):
            page = source.pages[page]
            content_object = page["/Contents"].getObject()
            content = ContentStream(content_object, source)

            for operands, operator in content.operations:
                if operator == b_("Tj"):
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
    wmText.append(watermark[x:x + lengthWmText])
    wmText.append(watermark[x + lengthWmText:])
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
    wmText.append(watermark[start:start + lengthWmText])
    wmText.append(watermark[start + lengthWmText:])
    return wmText

def remove_disclaimer(inputFile, outputFile):
    # This Function Reads PDF file and Removes the WATERMARK TEXT

    wmText = get_disclaimer(inputFile)
    with open(inputFile, "rb") as f:
        source = PdfFileReader(f, "rb")
        output = PdfFileWriter()

        for page in range(source.getNumPages()):
            page = source.pages[page]
            content_object = page["/Contents"].getObject()
            content = ContentStream(content_object, source)

            for operands, operator in content.operations:
                if operator == b_("Tj"):
                    text = operands[0]
                    if isinstance(text, str):
                        print(text)


                    if isinstance(text, str):
                        operands[0] = TextStringObject('')

            page.__setitem__(NameObject('/Contents'), content)
            output.addPage(page)

        with open(outputFile, "wb") as outputStream:
            output.write(outputStream)



def preprocess_pdf(input_file, output_file):
    waterMarkTextStarting = 'Mahkamah Agung'
    wm_text = watermark_text(input_file, waterMarkTextStarting)
    remove_watermark(wm_text, input_file, output_file)


def extract_text_from_pdf(input_file, output_file, method='pdfplumber'):
    if method == 'pdfplumber':
        with pdfplumber.open(input_file) as pdf:
            with open(output_file, 'wb') as f:
                for page in pdf.pages:
                    texts = []
                    texts.append(f'\n---page: {page.page_number}')
                    texts.append(page.extract_text())
                    f.write("\n".join(texts).encode('utf-8'))
    else:
        text = textract.process(input_file, method=method)
        with open(output_file, 'wb') as f:
            f.write(text)


extract_text_from_pdf("/media/robert/BC7CA8E37CA899A2/dev/indonesian_nlp_play/data/putusan_229_pk_tun_2022_20230228214708_preprocessed_no_disclaimer.pdf", "/media/robert/BC7CA8E37CA899A2/dev/indonesian_nlp_play/data/putusan_229_pk_tun_2022_20230228214708_preprocessed_no_disclaimer.txt")

