import pytest
import polars as pl
from zeolite.registry import ColumnRegistry
from zeolite._types import ColumnNode, Sensitivity

common_params = {
    "sensitivity": Sensitivity.NON_SENSITIVE,
    "schema": "test",
    "stage": "test_stage",
}

base_column_params = {
    "data_type": "string",
    "column_type": "source",
    **common_params,
}

number_column_params = {
    "data_type": "number",
    "column_type": "source",
    **common_params,
}


@pytest.fixture
def sample_columns():
    return [
        ColumnNode(
            id="test::col1",
            name="col1",
            **base_column_params,
        ),
        ColumnNode(
            id="test::col2",
            name="col2",
            data_type="number",
            column_type="derived",
            **common_params,
            expression=pl.col("col1").cast(pl.Int64).alias("col2"),
        ),
    ]


@pytest.fixture
def base_column():
    return ColumnNode(
        id="test::base",
        name="base",
        **base_column_params,
    )


def test_registry_initialization():
    # Test empty initialization
    registry = ColumnRegistry()
    assert len(registry.by_id) == 0
    assert len(registry.by_name) == 0


def test_registry_with_columns(sample_columns):
    # Test initialization with columns
    registry = ColumnRegistry(sample_columns)
    assert len(registry.by_id) == 2
    assert len(registry.by_name) == 2

    # Test column retrieval - comparing relevant attributes instead of direct equality
    col1 = registry.get_by_id("test::col1")
    assert col1.id == sample_columns[0].id
    assert col1.name == sample_columns[0].name
    assert col1.data_type == sample_columns[0].data_type

    col2 = registry.get_by_name("col2")
    assert col2.id == sample_columns[1].id
    assert col2.name == sample_columns[1].name
    assert col2.data_type == sample_columns[1].data_type


def test_registry_append_and_extend(sample_columns):
    registry = ColumnRegistry()

    # Test append
    registry.append(sample_columns[0])
    assert len(registry.by_id) == 1
    col1 = registry.get_by_name("col1")
    assert col1.id == sample_columns[0].id
    assert col1.name == sample_columns[0].name

    # Test extend
    registry.extend([sample_columns[1]])
    assert len(registry.by_id) == 2
    col2 = registry.get_by_id("test::col2")
    assert col2.id == sample_columns[1].id
    assert col2.name == sample_columns[1].name


def test_registry_remove(sample_columns):
    registry = ColumnRegistry(sample_columns)

    # Test remove
    registry.remove(sample_columns[0])
    assert len(registry.by_id) == 1
    assert registry.get_by_id("test::col1") is None
    assert registry.get_by_name("col1") is None


def test_registry_map_parent_ids(sample_columns):
    registry = ColumnRegistry(sample_columns)

    # Test mapping source column names to IDs
    col2 = registry.get_by_id("test::col2")

    # Check that parent_columns was auto-populated from expression
    assert "col1" in col2.parent_columns
    # Check that parent_ids was populated by registry from parent_columns
    assert "test::col1" in col2.parent_ids


def test_registry_catch_duplicate_ids(sample_columns):
    registry = ColumnRegistry(sample_columns)

    # Test duplicate ID
    with pytest.raises(
        AssertionError, match=f"Duplicate column ID: {sample_columns[0].id}"
    ):
        registry.extend([sample_columns[0]])  # Adding duplicate


def test_registry_get_execution_stages(sample_columns):
    registry = ColumnRegistry(sample_columns)

    # Test execution stages
    stages = registry.get_execution_stages()
    assert len(stages) == 1  # Should have 1 stage due to dependency
    assert stages[0][0].id == "test::col2"  # First stage should have col2


def test_column_node_expression_name_mismatch():
    # Test that expression output name must match column name
    with pytest.raises(
        AssertionError,
        match="Column name wrong_name does not match expression output name col2",
    ):
        ColumnNode(
            id="test::col2",
            name="wrong_name",  # Doesn't match expression output
            **number_column_params,
            expression=pl.col("col1").cast(pl.Int64).alias("col2"),
        )


def test_column_node_parent_columns_auto_population():
    # Test that parent_columns are auto-populated from expression
    col = ColumnNode(
        id="test::col2",
        name="col2",
        **number_column_params,
        expression=pl.col("col1").cast(pl.Int64).alias("col2"),
    )
    assert col.parent_columns == frozenset({"col1"})

    # Test that explicit parent_columns are respected
    col_explicit = ColumnNode(
        id="test::col2",
        name="col2",
        **number_column_params,
        expression=pl.col("col1").cast(pl.Int64).alias("col2"),
        parent_columns=frozenset({"explicit_source"}),
    )
    assert col_explicit.parent_columns == frozenset({"explicit_source"})


def test_column_node_with_parent_ids():
    # Test that with_parent_ids creates a new instance with updated parent_ids
    col = ColumnNode(
        id="test::col2",
        name="col2",
        **number_column_params,
        expression=pl.col("col1").cast(pl.Int64).alias("col2"),
    )

    new_col = col.with_parent_ids({"test::col1"})
    assert new_col.parent_ids == frozenset({"test::col1"})
    assert col.parent_ids == frozenset()  # Original should be unchanged


def test_registry_with_missing_parent_columns():
    # Test registry behavior when a column references a non-existent source
    col_with_mixed_sources = ColumnNode(
        id="test::col2",
        name="col2",
        **number_column_params,
        parent_columns=frozenset({"existing_col", "non_existent_col"}),
    )

    existing_col = ColumnNode(
        id="test::existing_col",
        name="existing_col",
        **base_column_params,
    )

    registry = ColumnRegistry([existing_col, col_with_mixed_sources])

    # Source columns should retain both sources
    assert col_with_mixed_sources.parent_columns == frozenset(
        {"existing_col", "non_existent_col"}
    )

    # But parent_ids should only contain the ID of the existing source
    col2 = registry.get_by_id("test::col2")
    assert col2.parent_ids == frozenset({"test::existing_col"})
    assert "test::non_existent_col" not in col2.parent_ids


def test_registry_integrity_unmapped_sources(base_column):
    # Column with unmapped source
    col_unmapped = ColumnNode(
        id="test::unmapped",
        name="unmapped",
        **number_column_params,
        parent_columns=frozenset({"non_existent"}),
    )

    registry = ColumnRegistry([base_column, col_unmapped])
    # Registry should set parent_ids to empty since source doesn't exist
    assert registry.get_by_id("test::unmapped").parent_ids == frozenset()
    with pytest.raises(ValueError, match="Unmapped source columns found"):
        registry.verify_integrity()


def test_registry_integrity_invalid_parent_ids(base_column):
    # Column with source that exists but incorrect ID mapping
    col_with_source = ColumnNode(
        id="test::derived",
        name="derived",
        data_type="number",
        column_type="derived",
        **common_params,
        parent_columns=frozenset({"base"}),
    )

    registry = ColumnRegistry([base_column, col_with_source])
    # Registry should set the correct source_id
    assert registry.get_by_id("test::derived").parent_ids == frozenset({"test::base"})
    assert registry.verify_integrity() is True


def test_registry_integrity_incorrect_mappings(base_column):
    # Column referencing base but with no parent_columns set
    col_incorrect = ColumnNode(
        id="test::incorrect",
        name="incorrect",
        **number_column_params,
        expression=pl.col("base").alias(
            "incorrect"
        ),  # References base but parent_columns will be auto-populated
    )

    registry = ColumnRegistry([base_column, col_incorrect])
    # Check that parent_columns was auto-populated from expression
    assert registry.get_by_id("test::incorrect").parent_columns == frozenset({"base"})
    # Check that parent_ids was properly mapped
    assert registry.get_by_id("test::incorrect").parent_ids == frozenset({"test::base"})
    assert registry.verify_integrity() is True


def test_registry_integrity_multiple_violations(base_column):
    # Column with mix of valid and invalid sources
    col_mixed = ColumnNode(
        id="test::mixed",
        name="mixed",
        **number_column_params,
        parent_columns=frozenset({"base", "non_existent1", "non_existent2"}),
    )

    registry = ColumnRegistry([base_column, col_mixed])
    # Registry should only include the valid source ID
    assert registry.get_by_id("test::mixed").parent_ids == frozenset({"test::base"})
    # But verify should fail due to unmapped sources
    with pytest.raises(ValueError) as exc:
        registry.verify_integrity()

    error_msg = str(exc.value)
    assert "Unmapped source columns found" in error_msg
    assert "non_existent1" in error_msg
    assert "non_existent2" in error_msg


def test_registry_integrity_valid_case(base_column):
    # Test valid case with proper source mapping
    valid_col = ColumnNode(
        id="test::valid",
        name="valid",
        **number_column_params,
        parent_columns=frozenset({"base"}),
    )

    registry = ColumnRegistry([base_column, valid_col])
    # Check that parent_ids was properly set by registry
    assert registry.get_by_id("test::valid").parent_ids == frozenset({"test::base"})
    assert registry.verify_integrity() is True


def test_column_node_expression_validation():
    # Valid case - expression output name matches column name
    valid_col = ColumnNode(
        id="test::col1",
        name="col1",
        **number_column_params,
        expression=pl.col("base").alias("col1"),
    )
    assert valid_col.parent_columns == frozenset({"base"})

    # Valid case - explicit parent_columns are respected even with expression
    valid_explicit = ColumnNode(
        id="test::col1",
        name="col1",
        **number_column_params,
        expression=pl.col("base").alias("col1"),
        parent_columns=frozenset({"explicit_source"}),
    )
    assert valid_explicit.parent_columns == frozenset({"explicit_source"})

    # Invalid case - expression output name doesn't match column name
    with pytest.raises(
        AssertionError,
        match="Column name wrong_name does not match expression output name col1",
    ):
        ColumnNode(
            id="test::wrong",
            name="wrong_name",
            **number_column_params,
            expression=pl.col("base").alias("col1"),
        )

    # Invalid case - expression with no alias
    with pytest.raises(
        AssertionError,
        match="Column name col1 does not match expression output name base",
    ):
        ColumnNode(
            id="test::col1",
            name="col1",
            **number_column_params,
            expression=pl.col("base"),  # No alias set
        )

    # Test chained expression
    chained_col = ColumnNode(
        id="test::col1",
        name="col1",
        data_type="number",
        sensitivity=Sensitivity.NON_SENSITIVE,
        schema="test",
        stage="test_stage",
        expression=pl.col("base").cast(pl.Int64).alias("col1"),
        column_type="derived",
    )
    assert chained_col.parent_columns == frozenset({"base"})

    # Test multiple source columns
    multi_source = ColumnNode(
        id="test::sum",
        name="sum",
        data_type="number",
        sensitivity=Sensitivity.NON_SENSITIVE,
        schema="test",
        stage="test_stage",
        expression=(pl.col("a") + pl.col("b")).alias("sum"),
        column_type="derived",
    )
    assert multi_source.parent_columns == frozenset({"a", "b"})
