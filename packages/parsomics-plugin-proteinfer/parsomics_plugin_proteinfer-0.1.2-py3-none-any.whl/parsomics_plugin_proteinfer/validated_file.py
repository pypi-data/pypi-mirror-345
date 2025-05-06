from pathlib import Path
from typing import ClassVar

from parsomics_core.entities.files.validated_file import ValidatedFileWithGenome


class ProteinferValidatedFile(ValidatedFileWithGenome):
    _VALID_FILE_TERMINATIONS: ClassVar[list[str]] = ["_ProteInfer_out.tsv", ".tsv"]

    @property
    def genome_name(self) -> str:
        path_obj = Path(self.path)
        return path_obj.name.replace("_ProteInfer_out.tsv", "").replace(".tsv", "")
