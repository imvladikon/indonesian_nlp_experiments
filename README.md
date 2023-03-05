# Indonesian Simple IE extractors

### Text extractor from PDF file

Just a simple wrapper for pdfplumber/pdfminer/pymupdf with some preprocessing steps
for https://putusan3.mahkamahagung.go.id/ :
* removing watermark
* removing disclaimer

To avoid probable corruption of the PDF file, preprocessing steps are creating a copy of the original file
into file with `_preprocessed` suffix.
```python
from extractors.pdf2text_extractor import Pdf2TextExtractor

input_file = 'putusan_229_pk_tun_2022_20230228214842.pdf'
extractor = Pdf2TextExtractor(backend='pdfplumber')
for page_num, text in extractor(input_file):
    print(text)
```

### Mentions extractor (aka NER)

NER(Roberta) model that was trained on https://huggingface.co/datasets/id_nergrit_corpus
It requires pre-installed sentencepiece tokenizer(since it's Roberta). You can install it with:

```bash
pip install sentencepiece
``` 

Tags:
```
"B-CRD", "B-DAT", "B-EVT", "B-FAC", "B-GPE", "B-LAN", "B-LAW", "B-LOC", "B-MON", "B-NOR", 
"B-ORD", "B-ORG", "B-PER", "B-PRC", "B-PRD", "B-QTY", "B-REG", "B-TIM", "B-WOA",
"I-CRD", "I-DAT", "I-EVT", "I-FAC", "I-GPE", "I-LAN", "I-LAW", "I-LOC", "I-MON", "I-NOR",
"I-ORD", "I-ORG", "I-PER", "I-PRC", "I-PRD", "I-QTY", "I-REG", "I-TIM", "I-WOA", "O",
```

Main class: [mentions_extractor.py](extractors%2Fmentions_extractor.py)

```python
from extractors.mentions_extractor import MentionExtractor

text = """
Demikianlah diputuskan dalam rapat permusyawaratan Majelis Hakim
pada hari Kamis, tanggal 22 Desember 2022, oleh Dr. Irfan Fachruddin, S.H.,
C.N., Hakim Agung yang ditetapkan oleh Ketua Mahkamah Agung sebagai
Ketua Majelis, bersama-sama dengan Dr. Cerah Bangun, S.H., M.H. dan Dr.
H. Yodi Martono Wahyunadi, S.H., M.H., Hakim-Hakim Agung sebagai
Anggota, dan diucapkan dalam sidang terbuka untuk umum pada hari itu
juga oleh Ketua Majelis dengan dihadiri Hakim-Hakim Anggota tersebut, dan
Dewi Asimah, S.H., M.H., Panitera Pengganti tanpa dihadiri oleh para pihak.
Anggota Majelis: Ketua Majelis,
ttd. ttd.
Dr. Cerah Bangun, S.H., M.H. Dr. Irfan Fachruddin, S.H., C.N.
""".strip()
extractor = MentionExtractor()
print(extractor(text))
```


### Relation extractor

A very naive approach to extract relation between two mentions
with using QA pipeline (based on mT5 model with pruned embeddings, original checkpoint is https://huggingface.co/muchad/idt5-qa-qg).
It's possible to run against raw text or against mentions extracted by `MentionExtractor`.
And it's recommended to adapt relations patterns to your use case.

```python
from extractors.relations_extractor import RelationsExtractor

pipeline = RelationsExtractor()
text = "Raja Purnawarman adalah seorang mahasiswa di Universitas Indonesia. Saya tinggal di Jakarta. Saya adalah mahasiswa Universitas Indonesia."
relations = pipeline(text)
print(relations)

```