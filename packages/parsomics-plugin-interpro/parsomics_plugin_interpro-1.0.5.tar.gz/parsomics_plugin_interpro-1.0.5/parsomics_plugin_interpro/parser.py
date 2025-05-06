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
from sqlmodel import Session, select


class InterproTsvParser(BaseModel):
    file: ProteinAnnotationFile
    assembly_key: int
    tool_key: int

    def to_dataframe(self) -> pl.DataFrame:
        schema: dict[str, pl.PolarsDataType] = {
            "protein_name": pl.String,
            "sequence_hash": pl.String,
            "sequence_length": pl.Int32,
            "source_name": pl.String,
            "signature_accession": pl.String,
            "signature_description": pl.String,
            "coord_start": pl.Int32,
            "coord_stop": pl.Int32,
            "score": pl.Float64,
            "status": pl.String,
            "date": pl.String,
            "interpro_annotation_accession": pl.String,
            "interpro_annotation_description": pl.String,
        }

        df = pl.read_csv(
            self.file.path,
            separator="\t",
            schema=schema,
            infer_schema_length=0,
            has_header=False,
            null_values=["-"],
            quote_char=None,
        )

        df = df.with_columns(pl.col("status").eq("T"))
        df = df.filter(pl.col("status"))

        df = df.with_columns(pl.col("date").str.to_date("%d-%m-%Y"))

        df = df.drop(
            [
                "sequence_hash",
                "sequence_length",
                "status",
                "date",
            ]
        )

        df = df.rename(
            {
                "signature_accession": "accession",
                "signature_description": "description",
            }
        )

        return df

    def _add_source_key_to_df(self, engine, df) -> pl.DataFrame:
        with Session(engine) as session:

            # First, add all sources that are already in the database (and,
            # thus, already have a primary key) to the dictionary that relates
            # source name to primary key
            sources_in_db = session.exec(select(Source)).all()
            source_name_to_key = {source.name: source.key for source in sources_in_db}

        # Then, iterate over the sources in the DataFrame and add them
        # to the database if they are not present in the source_name_to_key
        # dictionary. Add them to the dictionary once they have been added
        # to the database and have a primary key
        source_names_in_df = df.select(pl.col("source_name")).unique().to_series()
        for source_name in source_names_in_df:
            if source_name not in source_name_to_key:
                source_create_model = SourceCreate(
                    name=source_name,
                    tool_key=self.tool_key,
                )
                with Session(engine) as session:
                    source_key = (
                        SourceTransactions()
                        .create(
                            session,
                            source_create_model,
                        )
                        .key
                    )
                source_name_to_key[source_name] = source_key

        # Finally, use source_name_to_key to add source_key to the DataFrame
        df = df.with_columns(
            source_key=pl.col("source_name").replace(
                source_name_to_key,
                default=None,
            )
        )

        df = df.drop("source_name")

        return df

    def _add_file_key_to_df(self, df):
        return df.with_columns(pl.lit(self.file.key).alias("file_key"))

    def _add_details_to_mappings(self, mappings):
        for mapping in mappings:
            mapping["details"] = {}
            for k in [
                "interpro_annotation_accession",
                "interpro_annotation_description",
            ]:
                mapping["details"][k] = mapping[k]
                mapping.pop(k)

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

    def parse(self, engine) -> None:
        df = self.to_dataframe()
        df = self._add_source_key_to_df(engine, df)
        df = self._add_file_key_to_df(df)

        mappings = df.to_dicts()
        self._add_details_to_mappings(mappings)
        self._add_protein_key_to_mappings(mappings)

        with Session(engine) as session:
            try:
                session.bulk_insert_mappings(ProteinAnnotationEntry, mappings)
                session.commit()
                logging.info(
                    f"Added Interpro entries from {self.file.path} to the database."
                )
            except IntegrityError as e:
                logging.warning(
                    f"Failed to add Interpro entries from {self.file.path} to "
                    f"the database. Exception caught: {e}"
                )
