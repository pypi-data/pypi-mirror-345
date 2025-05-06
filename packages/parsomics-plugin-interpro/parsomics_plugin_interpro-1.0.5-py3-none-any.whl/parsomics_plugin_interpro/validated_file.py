from pathlib import Path
from typing import ClassVar

from parsomics_core.entities.files.validated_file import ValidatedFileWithGenome


class InterproTsvValidatedFile(ValidatedFileWithGenome):
    _VALID_FILE_TERMINATIONS: ClassVar[list[str]] = [
        "interpro_out.tsv",
    ]

    @property
    def genome_name(self) -> str:
        path_obj = Path(self.path)
        return "_".join(path_obj.name.split("_")[:-2])
