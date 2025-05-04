#
#  Copyright 2024 Tabs Data Inc.
#

import logging
from abc import ABC
from enum import Enum
from typing import Any, Optional, Type

import polars as pl

# noinspection PyProtectedMember
import tabsdata.utils.tableframe._constants as td_constants

# noinspection PyProtectedMember
import tabsdata.utils.tableframe._generators as td_generators
from tabsdata.extensions.features.api.features import Feature, FeaturesManager
from tabsdata.extensions.tableframe.api.api import Extension
from tabsdata.extensions.tableframe.version import version

logger = logging.getLogger(__name__)


def _src_default() -> pl.Expr:
    return pl.lit([], pl.List(pl.String))


def _src(_old_value: Optional[pl.List(pl.String)]) -> pl.List(pl.String):
    # noinspection PyProtectedMember
    return []


def _src_random() -> pl.List(pl.String):
    # noinspection PyProtectedMember
    return [td_generators._id()]


class ExtendedSystemColumns(Enum):
    TD_PROVENANCE = "$td.src"


class ExtendedSystemColumnsMetadata(Enum):
    TD_PROVENANCE = {
        td_constants.TD_COL_DTYPE: pl.List(pl.String),
        td_constants.TD_COL_DEFAULT: _src_default,
        td_constants.TD_COL_GENERATOR: _src,
    }


class SystemColumns(Enum):
    TD_IDENTIFIER = td_constants.StandardSystemColumns.TD_IDENTIFIER.value
    TD_PROVENANCE = ExtendedSystemColumns.TD_PROVENANCE.value


class RequiredColumns(Enum):
    TD_IDENTIFIER = td_constants.StandardSystemColumns.TD_IDENTIFIER.value
    TD_PROVENANCE = ExtendedSystemColumns.TD_PROVENANCE.value


_s_id_metadata = td_constants.StandardSystemColumnsMetadata.TD_IDENTIFIER.value
_s_src_metadata = ExtendedSystemColumnsMetadata.TD_PROVENANCE.value

SYSTEM_COLUMNS_METADATA = {
    SystemColumns.TD_IDENTIFIER.value: _s_id_metadata,
    SystemColumns.TD_PROVENANCE.value: _s_src_metadata,
}

_r_id_metadata = td_constants.StandardSystemColumnsMetadata.TD_IDENTIFIER.value
_r_src_metadata = ExtendedSystemColumnsMetadata.TD_PROVENANCE.value

REQUIRED_COLUMNS_METADATA = {
    RequiredColumns.TD_IDENTIFIER.value: _r_id_metadata,
    RequiredColumns.TD_PROVENANCE.value: _r_src_metadata,
}


class TableFrameExtension(Extension, ABC):
    name = "TableFrame Extension (Enterprise)"
    version = version()

    def __init__(self) -> None:
        FeaturesManager.instance().enable(Feature.ENTERPRISE)
        logger.info(
            f"Single instance of {Extension.__name__}: {TableFrameExtension.name} -"
            f" {TableFrameExtension.version}"
        )

    @classmethod
    def instance(cls) -> "TableFrameExtension":
        return instance

    @property
    def summary(self) -> str:
        return "Enterprise"

    @property
    def standard_system_columns(self) -> Type[Enum]:
        return td_constants.StandardSystemColumns

    @property
    def extended_system_columns(self) -> Type[Enum]:
        return ExtendedSystemColumns

    @property
    def system_columns(self) -> Type[Enum]:
        return SystemColumns

    @property
    def system_columns_metadata(self) -> dict[str, Any]:
        return SYSTEM_COLUMNS_METADATA

    @property
    def required_columns(self) -> Type[Enum]:
        return RequiredColumns

    @property
    def required_columns_metadata(self) -> dict[str, Any]:
        return REQUIRED_COLUMNS_METADATA

    def assemble_columns(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        id_cols = [
            col
            for col in lf.collect_schema().names()
            if col.startswith(td_constants.StandardSystemColumns.TD_IDENTIFIER.value)
        ]
        src_cols = [
            col
            for col in lf.collect_schema().names()
            if col.startswith(ExtendedSystemColumns.TD_PROVENANCE.value)
        ]
        source_columns = id_cols + src_cols
        lf = lf.with_columns(
            [pl.concat_list([pl.col(c)]).alias(f"{c}_") for c in id_cols]
        )
        lf = lf.with_columns(
            pl.concat_list([pl.col(c) for c in source_columns])
            .list.unique()
            .list.sort()
            .alias(ExtendedSystemColumns.TD_PROVENANCE.value)
        )
        target_cols = [
            td_constants.StandardSystemColumns.TD_IDENTIFIER.value,
            ExtendedSystemColumns.TD_PROVENANCE.value,
        ] + [
            c
            for c in lf.collect_schema().names()
            if not c.startswith(td_constants.TD_COLUMN_PREFIX)
        ]
        lf = lf.select(target_cols)
        return lf


instance = TableFrameExtension()
