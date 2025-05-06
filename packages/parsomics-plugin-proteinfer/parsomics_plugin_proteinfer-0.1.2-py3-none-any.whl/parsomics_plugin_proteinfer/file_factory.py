from typing import Sequence

from parsomics_core.factories import FileFactory

from .validated_file import ProteinferValidatedFile


class ProteinferFileFactory(FileFactory):
    def __init__(self, path: str, dereplicated_genomes: Sequence[str]):
        return super().__init__(
            validation_class=ProteinferValidatedFile,
            path=path,
            dereplicated_genomes=dereplicated_genomes,
        )
