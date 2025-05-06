import logging

import polars as pl
from parsomics_core.entities import ProteinAnnotationEntry, ProteinAnnotationFile
from parsomics_core.entities.workflow.source import (
    Source,
    SourceCreate,
    SourceTransactions,
)
from parsomics_core.plugin_utils import search_protein_by_name
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from parsomics_plugin_proteinfer.annotation_type import ProteinferAnnotationType


class ProteinferTsvParser(BaseModel):
    file: ProteinAnnotationFile
    assembly_key: int
    tool_key: int

    def to_dataframe(self) -> pl.DataFrame:
        df = pl.read_csv(
            self.file.path,
            separator="\t",
            null_values=["-"],
        )

        df = df.rename(
            {
                "sequence_name": "protein_name",
                "predicted_label": "accession",
                "confidence": "score",
            }
        )

        df = df.filter(pl.col("accession").is_not_null())
        df = self._remove_go_annotations_from_df(df)

        df = df.with_columns(
            pl.when(pl.col("accession").str.contains("Pfam"))
            .then(pl.lit("PFAM"))
            .otherwise(pl.lit("EC_NUMBER"))
            .alias("annotation_type")
        )

        df = df.with_columns(
            pl.when(pl.col("accession").str.contains(r"^(Pfam:|EC:)"))
            .then(pl.col("accession").str.replace(r"^(Pfam:|EC:)", ""))
            .otherwise(pl.col("accession"))
            .alias("accession")
        )

        return df

    def _remove_go_annotations_from_df(self, df: pl.DataFrame) -> pl.DataFrame:
        df2 = df.filter(~pl.col("accession").str.contains(r"GO:\d+"))

        return df2

    def _add_file_key_to_df(self, df):
        return df.with_columns(pl.lit(self.file.key).alias("file_key"))

    def _add_protein_key_to_mappings(self, mappings):
        protein_name_to_key = {}
        for mapping in mappings:
            protein_name = mapping["protein_name"]
            if protein_name not in protein_name_to_key:
                protein_key = search_protein_by_name(protein_name, self.assembly_key)
                protein_name_to_key[protein_name] = protein_key

            protein_key = protein_name_to_key[protein_name]
            mapping["protein_key"] = protein_key
            mapping.pop("protein_name")

    def _add_empty_details(self, mappings):
        for mapping in mappings:
            mapping["details"] = {}

    def parse(self, engine) -> None:
        df = self.to_dataframe()
        df = self._add_file_key_to_df(df)
        mappings = df.to_dicts()
        self._add_protein_key_to_mappings(mappings)
        self._add_empty_details(mappings)

        for mapping in mappings:
            mapping["annotation_type"] = ProteinferAnnotationType(
                mapping["annotation_type"]
            )

        with Session(engine) as session:
            try:
                session.bulk_insert_mappings(ProteinAnnotationEntry, mappings)
                session.commit()
                logging.info(
                    f"Added ProteInfer entries from {self.file.path} to the database."
                )
            except IntegrityError as e:
                logging.warning(
                    f"Failed to add ProteInfer entries from {self.file.path} to "
                    f"the database. Exception caught: {e}"
                )
