"""
slide/annotation/io
~~~~~~~~~~~~~~~~~~~
"""

import json
from collections.abc import Iterable
from functools import partial
from typing import Dict, List

import pandas as pd

from slide.annotation.base import Annotation
from slide.log import log_loading

log_annotation = partial(log_loading, header="Loading Annotation", log_level="info")


class AnnotationIO:
    """
    Handles loading and filtering of annotation for the SLIDE project.

    Supports loading annotation data from multiple formats including JSON, Excel, TSV, CSV,
    dictionary, and pandas DataFrame. All loaded annotations are filtered to ensure that only
    terms with a sufficient number of labels are retained.
    """

    def load_annotation_json(
        self,
        filepath: str,
        min_labels_per_term: int = 2,
        max_labels_per_term: int = 1000,
    ) -> Annotation:
        """
        Load and filter annotations from a JSON file.

        Args:
            filepath (str): Path to the JSON file containing annotations.
            min_labels_per_term (int, optional): Minimum number of labels required per annotation term.
                Defaults to 2.
            max_labels_per_term (int, optional): Maximum number of labels allowed per annotation term.
                Defaults to 1000.

        Returns:
            Annotation: Annotation object containing the filtered annotation.

        Raises:
            ValueError: If no annotation terms remain after filtering.
            TypeError: If any term's labels are not a list-like iterable (e.g., string).
        """
        log_annotation(filetype="JSON", filepath=filepath)
        with open(filepath, "r", encoding="utf-8") as file:
            annotation_input = json.load(file)

        return self._load_annotation_dict(
            annotation_input, min_labels_per_term, max_labels_per_term
        )

    def load_annotation_excel(
        self,
        filepath: str,
        terms_colname: str,
        labels_colname: str,
        sheet_name: str = "Sheet1",
        labels_delimiter: str = ";",
        min_labels_per_term: int = 2,
        max_labels_per_term: int = 1000,
    ) -> Annotation:
        """
        Load and filter annotations from an Excel file.

        Args:
            filepath (str): Path to the Excel file containing annotations.
            terms_colname (str): Column name for annotation terms.
            labels_colname (str): Column name for annotation labels.
            sheet_name (str): Name of the Excel sheet to read. Defaults to "Sheet1".
            labels_delimiter (str, optional): Delimiter used to split labels. Defaults to ";".
            min_labels_per_term (int, optional): Minimum number of labels required per annotation term.
                Defaults to 2.
            max_labels_per_term (int, optional): Maximum number of labels allowed per annotation term.
                Defaults to 1000.

        Returns:
            Annotation: Annotation object containing the filtered annotation data.

        Raises:
            ValueError: If no annotation terms remain after filtering.
            TypeError: If any term's labels are not a list-like iterable (e.g., string).
        """
        log_annotation(filetype="Excel", filepath=filepath)
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        annotation_dict = self._dataframe_to_dict(
            df, terms_colname, labels_colname, labels_delimiter
        )
        return self._load_annotation_dict(annotation_dict, min_labels_per_term, max_labels_per_term)

    def load_annotation_tsv(
        self,
        filepath: str,
        terms_colname: str,
        labels_colname: str,
        labels_delimiter: str = ";",
        min_labels_per_term: int = 2,
        max_labels_per_term: int = 1000,
    ) -> Annotation:
        """
        Load and filter annotations from a TSV file.

        Args:
            filepath (str): Path to the TSV file containing annotations.
            terms_colname (str): Column name for annotation terms.
            labels_colname (str): Column name for annotation labels.
            labels_delimiter (str, optional): Delimiter used to split labels. Defaults to ";".
            min_labels_per_term (int, optional): Minimum number of labels required per annotation term.
                Defaults to 2.
            max_labels_per_term (int, optional): Maximum number of labels allowed per annotation term.
                Defaults to 1000.

        Returns:
            Annotation: Annotation object containing the filtered annotation data.

        Raises:
            ValueError: If no annotation terms remain after filtering.
            TypeError: If any term's labels are not a list-like iterable (e.g., string).
        """
        log_annotation(filetype="TSV", filepath=filepath)
        df = pd.read_csv(filepath, sep="\t")
        annotation_dict = self._dataframe_to_dict(
            df, terms_colname, labels_colname, labels_delimiter
        )
        return self._load_annotation_dict(annotation_dict, min_labels_per_term, max_labels_per_term)

    def load_annotation_csv(
        self,
        filepath: str,
        terms_colname: str,
        labels_colname: str,
        labels_delimiter: str = ";",
        min_labels_per_term: int = 2,
        max_labels_per_term: int = 1000,
    ) -> Annotation:
        """
        Load and filter annotations from a CSV file.

        Args:
            filepath (str): Path to the CSV file containing annotations.
            terms_colname (str): Column name for annotation terms.
            labels_colname (str): Column name for annotation labels.
            labels_delimiter (str, optional): Delimiter used to split labels. Defaults to ";".
            min_labels_per_term (int, optional): Minimum number of labels required per annotation term.
                Defaults to 2.
            max_labels_per_term (int, optional): Maximum number of labels allowed per annotation term.
                Defaults to 1000.

        Returns:
            Annotation: Annotation object containing the filtered annotation data.

        Raises:
            ValueError: If no annotation terms remain after filtering.
            TypeError: If any term's labels are not a list-like iterable (e.g., string).
        """
        log_annotation(filetype="CSV", filepath=filepath)
        df = pd.read_csv(filepath)
        annotation_dict = self._dataframe_to_dict(
            df, terms_colname, labels_colname, labels_delimiter
        )
        return self._load_annotation_dict(annotation_dict, min_labels_per_term, max_labels_per_term)

    def load_annotation_dataframe(
        self,
        df: pd.DataFrame,
        terms_colname: str,
        labels_colname: str,
        labels_delimiter: str = ";",
        min_labels_per_term: int = 2,
        max_labels_per_term: int = 1000,
    ) -> Annotation:
        """
        Load and filter annotations from a pandas DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing annotations.
            terms_colname (str): Column name for annotation terms.
            labels_colname (str): Column name for annotation labels.
            labels_delimiter (str, optional): Delimiter used to split labels. Defaults to ";".
            min_labels_per_term (int, optional): Minimum number of labels required per annotation term.
                Defaults to 2.
            max_labels_per_term (int, optional): Maximum number of labels allowed per annotation term.
                Defaults to 1000.

        Returns:
            Annotation: Annotation object containing the filtered annotation data.

        Raises:
            ValueError: If no annotation terms remain after filtering.
            TypeError: If any term's labels are not a list-like iterable (e.g., string).
        """
        log_annotation(filetype="DataFrame")
        annotation_dict = self._dataframe_to_dict(
            df, terms_colname, labels_colname, labels_delimiter
        )
        return self._load_annotation_dict(annotation_dict, min_labels_per_term, max_labels_per_term)

    def load_annotation_dict(
        self,
        annotation_dict: Dict[str, List],
        min_labels_per_term: int = 2,
        max_labels_per_term: int = 1000,
    ) -> Annotation:
        """
        Load and filter annotations from a dictionary.

        Args:
            annotation_dict (Dict[str, List]): Dictionary containing annotations.
            min_labels_per_term (int, optional): Minimum number of labels required per annotation term.
                Defaults to 2.
            max_labels_per_term (int, optional): Maximum number of labels allowed per annotation term.
                Defaults to 1000.

        Returns:
            Annotation: Annotation object containing the filtered annotation data.

        Raises:
            ValueError: If no annotation terms remain after filtering.
            TypeError: If any term's labels are not a list-like iterable (e.g., string).
        """
        log_annotation(filetype="Dictionary")
        return self._load_annotation_dict(annotation_dict, min_labels_per_term, max_labels_per_term)

    def _dataframe_to_dict(
        self,
        df: pd.DataFrame,
        terms_colname: str,
        labels_colname: str,
        labels_delimiter: str = ";",
    ) -> Dict[str, List]:
        """
        Convert a DataFrame to a dictionary mapping annotation terms to labels.

        Args:
            df (pd.DataFrame): DataFrame containing annotations.
            terms_colname (str): Column name for annotation terms.
            labels_colname (str): Column name for annotation labels.
            labels_delimiter (str, optional): Delimiter used to split labels in the DataFrame. Defaults to ";".

        Returns:
            Dict[str, List]: Dictionary mapping annotation terms to lists of labels.
        """
        return {
            str(row[terms_colname]): [
                str(x) for x in str(row[labels_colname]).split(labels_delimiter)
            ]
            for _, row in df.iterrows()
        }

    def _load_annotation_dict(
        self,
        annotation_dict: Dict[str, List],
        min_labels_per_term: int = 2,
        max_labels_per_term: int = 1000,
    ) -> Annotation:
        """
        Load and filter annotations from an existing dictionary.

        Args:
            annotation_dict (Dict[str, List]): Dictionary containing annotations.
            min_labels_per_term (int, optional): Minimum number of labels required per annotation term.
                Defaults to 2.

        Returns:
            Annotation: Annotation object containing the filtered annotation data.

        Raises:
            ValueError: If no annotation terms remain after filtering.
            TypeError: If any term's labels are not a list-like iterable (e.g., string).
        """
        self._validate_annotation_dict_like(annotation_dict)
        return Annotation(annotation_dict, min_labels_per_term, max_labels_per_term)

    def _validate_annotation_dict_like(self, annotation_input: Dict) -> None:
        """
        Validate that annotation input is a dictionary mapping to iterable (non-str) label collections.

        Args:
            annotation_input (Dict): Dictionary mapping annotation terms to labels.

        Raises:
            TypeError: If any term's labels are not a list-like iterable (e.g., string).
        """
        for term, labels in annotation_input.items():
            if isinstance(labels, str) or not isinstance(labels, Iterable):
                raise TypeError(
                    f"Each term's labels must be a list-like iterable (not a string). Term '{term}' is invalid."
                )
