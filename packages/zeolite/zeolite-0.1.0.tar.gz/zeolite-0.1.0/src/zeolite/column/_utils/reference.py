from dataclasses import dataclass, asdict, field
from typing import Optional, TYPE_CHECKING, Union

from polars import Expr, col

from ..._utils.column_id import make_column_id

if TYPE_CHECKING:
    from ...registry import ColumnRegistry
    from ..._types import ColumnNode
    from .._validation import _BaseRowCheck, ColumnCheckType


@dataclass(frozen=True)
class ColumnRef:
    """Reference to a column that can be used to look up actual column names/ids"""

    base_name: str
    stage: Optional[str] = None
    schema: Optional[str] = None

    is_clean: bool = False
    is_derived: bool = False
    is_check: bool = False
    is_meta: bool = False
    is_custom_check: bool = False

    check_name: Optional[str] = None

    # alias_name: Optional[str] = None

    def _chain(self, **kwargs: dict[str, any]) -> "ColumnRef":
        """Create a new instance with some fields replaced"""
        return ColumnRef(**{**asdict(self), **kwargs})

    def clean(self) -> "ColumnRef":
        return self._chain(is_clean=True)

    def check(
        self, validation: Union["ColumnCheckType", type["_BaseRowCheck"], str]
    ) -> "ColumnRef":
        if isinstance(validation, str):
            check_name = validation
        elif isinstance(validation, type):
            check_name = validation.method_id()
        else:
            check_name = validation.method_id()
        return self._chain(is_check=True, check_name=check_name)

    def derived(self) -> "ColumnRef":
        return self._chain(is_derived=True)

    def custom_check(self) -> "ColumnRef":
        return self._chain(is_custom_check=True, is_derived=True)

    def with_schema(self, schema: str, stage: str | None = None) -> "ColumnRef":
        if stage is not None:
            return self._chain(schema=schema, stage=stage)
        else:
            return self._chain(schema=schema)

    # def alias(self, name: str) -> 'ColumnRef':
    #     """Set an alias for this column reference"""
    #     return self._chain(alias_name=name)

    def get_id(
        self,
        *,
        schema: str | None = None,
        stage: str | None = None,
        include_schema_prefix: bool = True,
    ) -> str:
        """Get the ID of the column reference"""
        return make_column_id(
            name=self.base_name,
            schema=schema if schema else self.schema,
            stage=stage if stage else self.stage,
            is_clean=self.is_clean,
            is_derived=self.is_derived,
            is_meta=self.is_meta,
            is_custom_check=self.is_custom_check,
            check_name=self.check_name,
            include_schema_prefix=include_schema_prefix,
        )

    def get_name(self) -> str:
        """Get the name of the column reference"""
        return self.get_id(include_schema_prefix=False).replace("::", "__")

    @property
    def col(self) -> Expr:
        """Get the name of the column reference"""
        return col(self.name)

    @property
    def name(self) -> str:
        """Get the name of the column reference"""
        return self.get_name()

    @property
    def id(self) -> str:
        """Get the ID of the column reference"""
        return self.get_id()

    @classmethod
    def from_id(cls, id: str) -> "ColumnRef":
        """Create a new column reference from an ID"""
        # Split parts
        parts = id.split("::")

        # TODO: This is a mess & doesn't work for "meta" columns yet - need to align/replace parse_column_id
        # Initialize variables
        stage = None
        schema = None
        name = None
        is_clean = False
        is_derived = False
        is_custom_check = False
        check_name = None

        # Parse based on number of parts
        if len(parts) == 1:
            # Simple case: just name
            name = parts[0]

        else:
            # Check if starts with stage
            current_idx = 0
            if len(parts) >= 3 and not parts[0].startswith("derived"):
                stage = parts[0]
                current_idx += 1

            # Check for schema
            if len(parts) >= (2 + current_idx):
                schema = parts[current_idx]
                current_idx += 1

            # Check for derived
            if "derived" in parts[current_idx:]:
                is_derived = True
                derived_idx = parts.index("derived", current_idx)
                current_idx = derived_idx + 1

                # Check for custom check
                if current_idx < len(parts) and parts[current_idx] == "custom_check":
                    check_name = parts[current_idx + 1]
                    return cls(
                        base_name=check_name,
                        schema=schema,
                        stage=stage,
                        is_derived=True,
                        is_custom_check=True,
                    )

            # Get remaining parts
            remaining = parts[current_idx:]

            # Parse remaining parts
            if "clean" in remaining:
                is_clean = True
                clean_idx = remaining.index("clean")
                name = remaining[clean_idx - 1] if clean_idx > 0 else remaining[-1]

                if "check" in remaining[clean_idx:]:
                    check_idx = remaining.index("check", clean_idx)
                    check_name = remaining[check_idx + 1]

            elif "check" in remaining:
                check_idx = remaining.index("check")
                name = remaining[check_idx - 1] if check_idx > 0 else remaining[-1]
                check_name = remaining[check_idx + 1]

            else:
                name = remaining[-1]

        return cls(
            base_name=name,
            schema=schema,
            stage=stage,
            is_clean=is_clean,
            is_derived=is_derived,
            check_name=check_name,
        )

    def resolve(
        self,
        registry: "ColumnRegistry",
        *,
        schema: str | None = None,
        stage: str | None = None,
    ) -> "ColumnNode":
        """Resolve the reference in the registry to an actual column node"""
        col_id = self.get_id(schema=schema, stage=stage)

        node = registry.get_by_id(col_id)
        if not node:
            raise ValueError(f"Could not find column with ID {col_id} in registry")
        return node


@dataclass(frozen=True)
class MetaColumnRef(ColumnRef):
    """Reference to a derived column"""

    is_meta: bool = field(default=True, init=False)


@dataclass(frozen=True)
class DerivedColumnRef(ColumnRef):
    """Reference to a derived column"""

    is_derived: bool = field(default=True, init=False)


@dataclass(frozen=True)
class CustomCheckColumnRef(ColumnRef):
    """Reference to a custom check column"""

    is_custom_check: bool = field(default=True, init=False)
    is_derived: bool = field(default=True, init=False)


def get_column_ref_from_id(col_id: str) -> ColumnRef:
    """Get a column reference from an ID"""
    return ColumnRef.from_id(col_id)
