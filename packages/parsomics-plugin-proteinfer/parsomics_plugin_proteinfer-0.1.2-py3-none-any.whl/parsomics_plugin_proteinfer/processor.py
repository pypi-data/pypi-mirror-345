import logging
from typing import Sequence

from parsomics_core.entities.files.protein_annotation.file.models import (
    ProteinAnnotationFile,
    ProteinAnnotationFileDemand,
)
from parsomics_core.entities.files.protein_annotation.file.transactions import (
    ProteinAnnotationFileTransactions,
)
from parsomics_core.processors._helpers import retrieve_genome_key
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session

from .file_factory import ProteinferFileFactory
from .parser import ProteinferTsvParser
from .validated_file import ProteinferValidatedFile


class ProteinferOutputProcessor(BaseModel):
    output_directory: str
    dereplicated_genomes: Sequence[str]
    assembly_key: int
    run_key: int
    tool_key: int

    def process_proteinfer_files(self, engine: Engine):
        proteinfer_file_factory: ProteinferFileFactory = ProteinferFileFactory(
            self.output_directory,
            self.dereplicated_genomes,
        )

        proteinfer_files: list[ProteinferValidatedFile] = (
            proteinfer_file_factory.assemble()
        )
        for f in proteinfer_files:
            genome_key = retrieve_genome_key(engine, f, self.assembly_key)
            run_key = self.run_key

            protein_annotation_file_demand_model = ProteinAnnotationFileDemand(
                path=f.path,
                run_key=run_key,
                genome_key=genome_key,
            )

            with Session(engine) as session:
                protein_annotation_file: ProteinAnnotationFile = (
                    ProteinAnnotationFile.model_validate(
                        ProteinAnnotationFileTransactions().demand(
                            session,
                            protein_annotation_file_demand_model,
                        )
                    )
                )

            proteinfer_parser = ProteinferTsvParser(
                file=protein_annotation_file,
                assembly_key=self.assembly_key,
                tool_key=self.tool_key,
            )
            proteinfer_parser.parse(engine)

        logging.info(
            f"Finished adding all ProteInfer files on {self.output_directory} to the database."
        )
