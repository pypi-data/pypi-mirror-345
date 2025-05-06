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

from .file_factory import InterproTsvFileFactory
from .parser import InterproTsvParser
from .validated_file import InterproTsvValidatedFile


class InterproOutputProcessor(BaseModel):
    output_directory: str
    dereplicated_genomes: Sequence[str]
    assembly_key: int
    run_key: int
    tool_key: int

    def process_interpro_tsv_files(self, engine: Engine):
        interpro_tsv_file_factory: InterproTsvFileFactory = InterproTsvFileFactory(
            self.output_directory,
            self.dereplicated_genomes,
        )

        interpro_tsv_files: list[InterproTsvValidatedFile] = (
            interpro_tsv_file_factory.assemble()
        )
        for f in interpro_tsv_files:
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

            interpro_tsv_parser = InterproTsvParser(
                file=protein_annotation_file,
                assembly_key=self.assembly_key,
                tool_key=self.tool_key,
            )
            interpro_tsv_parser.parse(engine)

        logging.info(
            f"Finished adding all Interpro files on {self.output_directory} to the database."
        )
