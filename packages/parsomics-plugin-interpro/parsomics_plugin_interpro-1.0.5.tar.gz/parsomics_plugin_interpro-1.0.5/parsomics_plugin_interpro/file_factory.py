from typing import Sequence

from parsomics_core.factories import FileFactory

from .validated_file import InterproTsvValidatedFile


class InterproTsvFileFactory(FileFactory):
    def __init__(self, path: str, dereplicated_genomes: Sequence[str]):
        return super().__init__(
            validation_class=InterproTsvValidatedFile,
            path=path,
            dereplicated_genomes=dereplicated_genomes,
        )
