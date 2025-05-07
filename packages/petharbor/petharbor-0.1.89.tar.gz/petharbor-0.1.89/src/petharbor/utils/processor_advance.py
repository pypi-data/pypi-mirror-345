from petharbor.utils.logging_setup import get_logger

logger = get_logger()

from transformers import pipeline
from tqdm.contrib.logging import logging_redirect_tqdm
import pandas as pd


class ModelProcessor:
    def __init__(
        self,
        model: str,
        tokenizer: str = None,
        tag_map: dict = None,
        replaced: bool = True,
        text_column: str = "text",
        label_column: str = "predictions",
        device: str = "cpu",
    ):
        self.model = model
        self.tokenizer = tokenizer if tokenizer is not None else model
        self.tag_map = tag_map or {}
        self.replaced = replaced
        self.text_column = text_column
        self.label_column = label_column
        self.device = device

        logger.info("Initializing NER pipeline")
        self.ner_pipeline = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
            device=self.device,
        )

        logger.info(f"Tag map: {self.tag_map}")

    @staticmethod
    def replace_token(text, start, end, replacement):
        """Replace a token in the text with a replacement string."""
        if start < 0 or end > len(text):
            logger.warning(
                f"Start index {start} or end index {end} is out of bounds for text of length {len(text)}"
            )
            raise ValueError("Start and end indices are out of bounds.")
        return text[:start] + replacement + text[end:]

    def _process_batch(self, examples):
        texts = examples[self.text_column]
        texts = [str(text) for text in texts]

        try:
            ner_results = self.ner_pipeline(texts)
        except Exception as e:
            logger.error(f"Error during NER pipeline processing: {e}")
            raise

        anonymized_texts = []
        for i, entities in enumerate(ner_results):
            text = texts[i]
            for entity in sorted(entities, key=lambda x: x["start"], reverse=True):
                tag = self.tag_map.get(entity["entity_group"])
                if tag:
                    text = self.replace_token(text, entity["start"], entity["end"], tag)
            anonymized_texts.append(text)

        if self.replaced == True:
            return {self.text_column: anonymized_texts}
        elif self.replaced == False:
            return {self.label_column: ner_results}
        else:
            return {self.label_column: ner_results, self.text_column: anonymized_texts}

    def anonymise(self, dataset, replace=True):
        """Apply NER-based anonymisation to a dataset.
        
        args:
            dataset (Dataset): The dataset to process.
            replace (bool): Whether to replace the text with anonymised text or not.
        """
        self.replaced = replace
        date_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        with logging_redirect_tqdm():
            processed_dataset = dataset.map(
                self._process_batch,
                batched=True,
                desc=f"[{date_time} |   INFO  | PetHarbor-Advance]",
            )
        logger.info("Predictions obtained and text anonymised successfully")
        return processed_dataset
