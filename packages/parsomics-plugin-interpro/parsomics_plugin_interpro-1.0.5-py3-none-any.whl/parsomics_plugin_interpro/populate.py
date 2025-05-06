from typing import Sequence

from parsomics_core.globals.database import engine
from parsomics_core.populate import process_files
from timeit_decorator import timeit

from .processor import InterproOutputProcessor


@timeit()
def populate_interpro(
    run_info: dict, assembly_key: int, dereplicated_genomes: Sequence[str]
) -> None:
    def process_interpro_files(
        output_directory, assembly_key, run_key, tool_key, dereplicated_genomes
    ):
        interpro_output_processor = InterproOutputProcessor(
            output_directory=output_directory,
            assembly_key=assembly_key,
            run_key=run_key,
            tool_key=tool_key,
            dereplicated_genomes=dereplicated_genomes,
        )
        interpro_output_processor.process_interpro_tsv_files(engine)

    process_files(
        run_info, assembly_key, dereplicated_genomes, "interpro", process_interpro_files
    )
