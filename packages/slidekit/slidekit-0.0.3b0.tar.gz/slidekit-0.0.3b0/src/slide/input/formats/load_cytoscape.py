"""
slide/input/formats/load_cytoscape
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import json
import os
import shutil
import zipfile

import pandas as pd

from slide.input.base import Input2D
from slide.input.formats._loader import load_pairs
from slide.input.formats._log_loading import log_network


class LoadCytoscape:
    """Load Cytoscape and Cytoscape JSON files into Input2D objects."""

    def load_cytoscape(self, filepath: str) -> Input2D:
        """
        Automatically detect the structure of a Cytoscape file and load it.

        Args:
            filepath (str): Path to the Cytoscape file.

        Returns:
            Input2D: A 2D Input object.

        Raises:
            IOError: If file can't be read.
            ValueError: If format can't be inferred.
        """
        log_network(filetype="Cytoscape", filepath=filepath)
        return self._load_cytoscape_input(filepath)

    def load_cyjs(self, filepath: str) -> Input2D:
        """
        Automatically detect the structure of a .cyjs file and load it.

        Args:
            filepath (str): Path to the .cyjs file.

        Returns:
            Input2D: A 2D Input object.

        Raises:
            IOError: If file can't be read.
            ValueError: If format can't be inferred.
        """
        log_network(filetype="Cytoscape JSON", filepath=filepath)
        return self._load_cytoscape_input(filepath)

    def _load_cytoscape_input(self, filepath: str) -> Input2D:
        """
        Load a Cytoscape file (either a .cys archive or a Cytoscape JSON file) and return a pairs DataFrame
        with columns for source, target, and weight (defaulting to 1.0 if not provided).

        Args:
            filepath (str): Path to the Cytoscape file.

        Returns:
            Input2D: A 2D Input object.

        Raises:
            IOError: If the file cannot be read.
            ValueError: If the file structure is invalid.
        """
        # Default column names for source, target, and edge values commonly used in Cytoscape files
        source_label = "source"
        target_label = "target"
        value_label = "weight"

        # Try to read the file as a .cys archive
        try:
            with zipfile.ZipFile(filepath, "r") as z:
                namelist = z.namelist()
                # Check if this archive looks like a .cys file (has '/views/' and '/tables/' entries)
                if any("/views/" in f for f in namelist) and any("/tables/" in f for f in namelist):
                    tmp_dir = ".tmp_cytoscape"
                    if not os.path.exists(tmp_dir):
                        os.makedirs(tmp_dir)
                    try:
                        z.extractall(tmp_dir)
                        # Look for the attribute metadata file using expected keywords
                        attribute_metadata_keywords = ["/tables/", "SHARED_ATTRS", "edge.cytable"]
                        attribute_metadata = next(
                            (
                                os.path.join(tmp_dir, cf)
                                for cf in namelist
                                if all(keyword in cf for keyword in attribute_metadata_keywords)
                            ),
                            None,
                        )
                        if not attribute_metadata:
                            raise ValueError("No matching attribute metadata file found.")

                        # Read the attribute metadata file and extract the source and target columns
                        attribute_table = pd.read_csv(
                            attribute_metadata,
                            sep=",",
                            header=None,
                            skiprows=1,
                            dtype=str,
                            engine="c",
                            low_memory=False,
                        )
                        attribute_table.columns = attribute_table.iloc[0]
                        attribute_table = attribute_table.iloc[4:, :]
                        try:
                            attribute_table = attribute_table[[source_label, target_label]]
                        except KeyError as e:
                            missing_keys = [
                                k
                                for k in [source_label, target_label]
                                if k not in attribute_table.columns
                            ]
                            available_columns = ", ".join(attribute_table.columns)
                            raise KeyError(
                                f"The column(s) {missing_keys} do not exist in the table. Available columns are: {available_columns}."
                            ) from e
                        attribute_table = attribute_table.dropna().reset_index(drop=True)
                        if value_label not in attribute_table.columns:
                            attribute_table[value_label] = 1.0
                        df = attribute_table.copy()
                    finally:
                        shutil.rmtree(tmp_dir)

                    return load_pairs(
                        df,
                        source_col=source_label,
                        target_col=target_label,
                        value_col=value_label,
                        fill_value=None,
                    )
                else:
                    # If not a .cys file, assume a Cytoscape JSON structure inside the zip
                    with z.open(namelist[0]) as f:
                        cyjs_data = json.load(f)
        except zipfile.BadZipFile:
            # If not a zip archive, try reading directly as a JSON file
            with open(filepath, "r") as f:
                cyjs_data = json.load(f)

        # Process the Cytoscape JSON structure
        if isinstance(cyjs_data, dict) and "elements" in cyjs_data:
            elements = cyjs_data["elements"]
            if isinstance(elements, dict) and "edges" in elements:
                edge_data = []
                for edge in elements["edges"]:
                    d = edge.get("data", {})
                    if source_label in d and target_label in d:
                        edge_dict = {
                            source_label: d.get("source_original", d.get(source_label)),
                            target_label: d.get("target_original", d.get(target_label)),
                            value_label: d.get(value_label, 1.0),
                        }
                        edge_data.append(edge_dict)
                if not edge_data:
                    raise ValueError("No valid edge data found in Cytoscape file.")
                df = pd.DataFrame(edge_data)
                return load_pairs(
                    df,
                    source_col=source_label,
                    target_col=target_label,
                    value_col=value_label,
                    fill_value=None,
                )
            else:
                raise ValueError("Cytoscape file missing 'edges' in 'elements'.")
        else:
            raise ValueError("Cytoscape file does not contain a valid 'elements' structure.")
