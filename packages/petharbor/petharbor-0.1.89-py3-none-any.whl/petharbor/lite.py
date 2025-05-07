from petharbor.utils.dataset import DatasetProcessor
from petharbor.utils.processor_lite import ModelProcessor
from petharbor.utils.logging_setup import get_logger
from datasets import Dataset
from typing import Optional, Dict, Any
import torch
import logging
import pandas as pd


class Anonymiser:
    """Anonymises text data using a pre-trained model.

    Args:
        dataset (Union[str, Dataset], optional): Path to dataset file (CSV, Arrow, etc.) or a HuggingFace Dataset.
        split (str): Dataset split to use ('train', 'test', etc.). Defaults to 'train'.
        model (str): HuggingFace model path or name. Defaults to 'SAVSNET/PetHarbor'.
        tokenizer (str, optional): Tokenizer path or name. Defaults to model if not provided.
        text_column (str): Column in dataset containing text. Defaults to 'text'.
        cache (bool): Whether to use caching. Defaults to True.
        cache_path (str): Directory to store cache files. Defaults to 'petharbor_cache/'.
        logs (str, optional): Path to save logs. If None, logs to console.
        device (str, optional): Device to use for computation. Defaults to 'cuda' if available else 'cpu'.
        tag_map (Dict[str, str], optional): Entity tag to replacement string mapping.
        output_dir (str, optional): Directory to save output dataset.
    """

    def __init__(
        self,
        dataset: str = None,  # Path to the dataset file (CSV, Arrow, etc.)
        split: str = "train",  # Split of the dataset to use (e.g., 'train', 'test', 'eval')
        hash_table: str = None,  # Path to the hash table file
        salt: str = None,  # Salt for hashing
        use_spacy: bool = False,  # Whether to use spaCy for tokenization
        spacy_model: str = "en_core_web_sm",  # spaCy model to use
        text_column: str = "text",  # Column name in the dataset containing text data
        label_column: str = "labels",  # Column name in the dataset containing labels
        cache: bool = True,  # Whether to use cache
        cache_path: str = "petharbor_cache/",  # Path to save cache files
        logs: Optional[str] = None,  # Path to save logs
        device: Optional[str] = "cuda" if torch.cuda.is_available() else "cpu",
        tag_map: Optional[Dict[str, str]] = {
            "PER": "<<NAME>>",
            "LOC": "<<LOCATION>>",
            "TIME": "<<TIME>>",
            "ORG": "<<ORG>>",
            "MISC": "<<MISC>>",
        },  # Mapping of entity tags to replacement strings
        output_dir: str = None,  # Directory to save the output files
    ):
        self.dataset = dataset
        self.split = split
        self.salt = salt
        self.use_spacy = use_spacy
        self.spacy_model = spacy_model
        self.text_column = text_column
        self.label_column = label_column
        self.cache = cache
        self.cache_path = cache_path
        self.logs = logs
        self.device = device
        self.tag_map = tag_map
        self.output_dir = output_dir

        self.logger = self._setup_logger()
        logger = logging.getLogger(__name__)
        self.dataset_processor = DatasetProcessor(cache_path=self.cache_path)
        self.model_processor = ModelProcessor(
            tag_map=self.tag_map,
            replaced=True,
            text_column=self.text_column,
            label_column=self.label_column,
        )
        self.hash_table = self._read_hash_table(hash_table)
    def __repr__(self):
        return f"<Anonymiser model={self.model} dataset={self.dataset} device={self.device}>"

    def _setup_logger(self) -> Any:
        return (
            get_logger(log_dir=self.logs, method="Lite")
            if self.logs else get_logger(method="Lite")
        )
    
    def _read_hash_table(self, hash_table: str) -> list:
        if hash_table is None:
            error_message = "Hash table path must be provided. Please provide a valid path to `hash_table`."
            self.logger.error(error_message)
            raise ValueError(error_message)
        self.logger.info(f"Reading hash table from {hash_table}")
        hash_list = []
        with open(hash_table, "r") as file:
            for line in file:
                hash_list.append(line.strip())
        return hash_list

    def _print_output(self, input_text: str, output_text: str):
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp} | SUCCESS | PetHarbor-Lite] Input: {input_text}")
        print(f"[{timestamp} | SUCCESS | PetHarbor-Lite] Output: {output_text}")

    def _prepare_single_text(self, text: str) -> Dataset:
        if not isinstance(text, str):
            error_message = "Input text must be a string."
            self.logger.error(error_message)
            raise ValueError(error_message)
        clean_text = text.strip()
        df = pd.DataFrame({self.text_column: [clean_text]})
        return Dataset.from_pandas(df)

    def _prepare_dataset(self) -> Dataset:
        if isinstance(self.dataset, Dataset):
            original_data = self.dataset
        elif isinstance(self.dataset, str):
            original_data = self.dataset_processor.load_dataset_file(
                self.dataset, split=self.split
            )
        else:
            raise ValueError("`dataset` must be a filepath or a HuggingFace Dataset.")

        validated = self.dataset_processor.validate_dataset(
            dataset=original_data, text_column=self.text_column
        )
        cached, _ = self.dataset_processor.load_cache(
            dataset=validated, cache=self.cache
        )
        return cached, validated

    def _run(
        self,
        text: str = None,
        dataset: str = None,
        replace=None,
    ) -> None:
        """Anonymizes the single text data or in a dataset and output/saves the results.

        Args:
        text (str, optional): Text to anonymize
        dataset (str, optional): Path to the dataset file (CSV, Arrow, etc.)

        Raises:
        ValueError: If both text and dataset are provided or neither is provided.

        """
        if text and self.dataset:
            raise ValueError(
                "Please provide either a text string or a dataset path, not both."
            )
        # Prepare input
        if text:  # If text is provided
            self.logger.warning(
                "Anonymising single text input. For bulk processing, use a dataset."
            )
            target_dataset = self._prepare_single_text(text)
        elif dataset:  # If dataset is provided to class
            self.dataset = dataset
            target_dataset, original_data = self._prepare_dataset()
        elif self.dataset:  # If dataset is initialized
            target_dataset, original_data = self._prepare_dataset()
        else:
            raise ValueError("Please provide either a text string or a dataset path.")

        target_dataset = self.model_processor.hash_predict(
            dataset=target_dataset,
            hash_table=self.hash_table,
            text_column=self.text_column,
            salt=self.salt,
            replace=replace,
        )
        
        if self.use_spacy:
            target_dataset = self.model_processor.spacy_predict(
                dataset=target_dataset,
                spacy_model=self.spacy_model,
                text_column=self.text_column,
                replace=replace,
            )
        if text:
            self._print_output(text, target_dataset[0])
        else:
            self.dataset_processor.save_dataset_file(
                original_data=original_data,
                target_dataset=target_dataset,
                cache=self.cache,
                output_dir=self.output_dir,
            )

    def anonymise(
        self,
        text: str = None,
        dataset: str = None) -> Optional[str]:
        self.logger.info("Anonymising text data. n.b 'anonymise' method overwrites the text column.")
        self._run(
            text=text, dataset=dataset, replace=True)