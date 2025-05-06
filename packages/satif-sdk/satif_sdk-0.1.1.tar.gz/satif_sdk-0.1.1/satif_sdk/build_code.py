from satif_core import SDIFDatabase
from satif_core.types import Datasource

from satif_sdk.transformers import TransformationSchema


def build_standardization_code(
    datasource: Datasource,
) -> str: ...


def build_adaptation_code(
    sdif: SDIFDatabase,
    transformation_schema: TransformationSchema,
) -> str: ...


def build_transformation_code(
    sdif: SDIFDatabase,
    input_examples: Datasource,
    output_examples: Datasource,
) -> str: ...
