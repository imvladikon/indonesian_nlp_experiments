#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from extractors.base_extractor import BaseExtractor


class QAExtractor(BaseExtractor):

    def __init__(self, model_name='bstds/id-mt5-qa', device='cpu', **kwargs):
        super().__init__(**kwargs)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.qg_format = "highlight"
        self.model.to(device)
        assert self.model.__class__.__name__ in ["T5ForConditionalGeneration"]
        self.model_type = "t5"

    def __call__(self, question, context, **kwargs):
        return self._extract(question, context, **kwargs)

    def _prepare_inputs(self, question, context):
        source_text = f"question: {question}  context: {context}"
        source_text = source_text + " </s>"
        return source_text

    @property
    def device(self):
        return self.model.device

    def _extract(self, question, context, **kwargs):
        source_text = self._prepare_inputs(question, context)
        inputs = self._tokenize([source_text], padding=False)

        outs = self.model.generate(
            input_ids=inputs['input_ids'].to(self.device),
            attention_mask=inputs['attention_mask'].to(self.device),
            max_length=80,
        )
        answers = self.tokenizer.decode(outs[0], skip_special_tokens=True)
        flat_answers = list(itertools.chain(*answers))

        if len(flat_answers) == 0:
            return []
        return answers

    def _tokenize(
        self,
        inputs,
        padding=True,
        truncation=True,
        add_special_tokens=True,
        max_length=512,
    ):
        inputs = self.tokenizer.batch_encode_plus(
            inputs,
            max_length=max_length,
            add_special_tokens=add_special_tokens,
            truncation=truncation,
            padding="max_length" if padding else False,
            pad_to_max_length=padding,
            return_tensors="pt",
        )
        return inputs


if __name__ == '__main__':
    context = "Raja Purnawarman mulai memerintah Kerajaan Tarumanegara pada tahun 395 M."
    question = "Siapa pemimpin Kerajaan Tarumanegara?"

    extractor = QAExtractor()
    print(extractor(question, context))
