from typing import Sequence

from parsomics_core.globals.database import engine
from parsomics_core.populate import process_files
from timeit_decorator import timeit

from .processor import ProteinferOutputProcessor


@timeit()
def populate_proteinfer(
    run_info: dict, assembly_key: int, dereplicated_genomes: Sequence[str]
) -> None:
    def process_proteinfer_files(
        output_directory, assembly_key, run_key, tool_key, dereplicated_genomes
    ):
        proteinfer_output_processor = ProteinferOutputProcessor(
            output_directory=output_directory,
            assembly_key=assembly_key,
            run_key=run_key,
            tool_key=tool_key,
            dereplicated_genomes=dereplicated_genomes,
        )
        proteinfer_output_processor.process_proteinfer_files(engine)

    process_files(
        run_info,
        assembly_key,
        dereplicated_genomes,
        "proteinfer",
        process_proteinfer_files,
    )
