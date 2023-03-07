#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools

from transformers import QuestionAnsweringPipeline, AutoModelForQuestionAnswering, AutoTokenizer

from extractors.base_extractor import BaseExtractor


class ExtractiveQAExtractor(BaseExtractor):

    def __init__(self, model_name='bstds/id-extractive-bert-squad', **kwargs):
        super().__init__(**kwargs)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.qa_pipeline = QuestionAnsweringPipeline(
            model=self.model,
            tokenizer=self.tokenizer
        )

    def __call__(self, question, context, **kwargs):
        return self._extract(question, context, **kwargs)

    def _extract(self, question, context, **kwargs):
        answer = self.qa_pipeline({
            'question': question,
            'context': context
        })
        return answer


if __name__ == '__main__':
    context = "Raja Purnawarman mulai memerintah Kerajaan Tarumanegara pada tahun 395 M."
    question = "Siapa pemimpin Kerajaan Tarumanegara?"

    extractor = ExtractiveQAExtractor()
    print(extractor(question, context))
