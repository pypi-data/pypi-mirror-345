from petharbor.utils.logging_setup import get_logger
logger = get_logger()
from tqdm.contrib.logging import logging_redirect_tqdm

import hashlib
from tqdm import tqdm
import pandas as pd

class ModelProcessor:
    def __init__(
        self,
        tag_map: dict = None,
        replaced: bool = True,
        text_column: str = "text",
        label_column: str = "predictions",
        ):
        self.tag_map = tag_map or {}
        self.replaced = replaced
        self.text_column = text_column
        self.label_column = label_column
        self.text = 'text'
        self.label = 'predictions'
        
        logger.info(f"Tag map: {self.tag_map}")

    def _process_hash_batch(self, examples):
        narratives = examples[self.text_column]
        anonymized_narratives = []

        for narrative in narratives:
            words = narrative.split()
            anonymized_words = []

            for word in words:
                clean_word = word.strip(",.?!:").lower()
                hashed_word = self.hash_term(clean_word, self.salt)

                if hashed_word in self.hash_table:
                    anonymized_words.append("<<IDENTIFIER>>")
                else:
                    anonymized_words.append(word)

            anonymized_narratives.append(" ".join(anonymized_words))

        if self.replace:
            return {self.text_column: anonymized_narratives}
        else:
            return {f"anonymized_{self.text_column}": anonymized_narratives}

    def hash_predict(
        self, dataset, hash_table: list, text_column: str, salt: str, replace: bool = True
    ):
        """
        Apply hashing-based anonymization to a Hugging Face dataset.
        """
        self.hash_table = hash_table
        self.text_column = text_column
        self.salt = salt
        self.replace = replace
        logger.info(f"Hashing dataset with salt: {self.salt}")
        date_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        with logging_redirect_tqdm():
            processed_dataset = dataset.map(
                self._process_hash_batch,
                batched=True,
                desc=f"[{date_time} |   INFO  | PetHarbor-Lite]",
            )
        return processed_dataset
    
    def _process_spacy_batch(self, examples):
        texts = examples[self.text_column]
        anonymized_texts = []

        for doc in self.nlp.pipe(texts, batch_size=32):
            anonymized = self.anonymize_text(doc)
            anonymized_texts.append(anonymized)

        if self.replace:
            return {self.text_column: anonymized_texts}
        else:
            return {f"anonymized_{self.text_column}": anonymized_texts}

    def spacy_predict(
        self, dataset, spacy_model: str = "en_core_web_sm", text_column: str = "text", replace=False
    ):
        """
        Apply spaCy-based anonymization to a Hugging Face dataset.
        """
        self.text_column = text_column
        self.replace = replace
        self.nlp = self.import_spacy(spacy_model)
        logger.info(f"Spacy Enabled |Using spaCy model: {spacy_model}")
        date_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        with logging_redirect_tqdm():
            processed_dataset = dataset.map(
                self._process_spacy_batch,
                batched=True,
                desc=f"[{date_time} |   INFO  | PetHarbor-Lite]",
            )
        return processed_dataset
        

    @staticmethod
    def anonymize_text(text: str) -> str:

        entity_map = {
            "PERSON": "<<PER>>",
            "ORG": "<<ORG>>",
            "DATE": "<<DATE>>",
            "TIME": "<<TIME>>",
            "MONEY": "<<COST>>",
            "GPE": "<<LOC>>",
            "LOC": "<<LOC>>",
        }
        try:
            text_string = text.text
        except:
            text_string = text

        if text.ents:
            for entity in text.ents:
                if entity.label_ in entity_map.keys():
                    text_string = text_string.replace(
                        entity.text, entity_map[entity.label_]
                    )
        return text_string

    @staticmethod
    def import_spacy(spacy_model: str = "en_core_web_sm"):
        try:
            import spacy
        except ImportError:
            raise ImportError(
                "spaCy is not installed. Please install it using 'pip install spacy'"
            )
        try:
            nlp = spacy.load(spacy_model)
        except OSError:
            raise ValueError(
                f"spaCy model '{spacy_model}' not found. Please check the model name or ensure it is installed using 'python -m spacy download {spacy_model}'"
            )
        return nlp

    @staticmethod
    def hash_term(term: str, salt: str) -> str:
        """Hash a term with the shared salt."""
        salted_term = term + salt
        hash_object = hashlib.sha256(salted_term.encode("utf-8"))
        return hash_object.hexdigest()
