"""
Basic examples of using the Zeolite data validation framework.
This file demonstrates how to create schemas and define column validations.
"""

import zeolite as z

# ---------------------------------------------------------------------------------
# Example 1: Basic Schema Definition
# ---------------------------------------------------------------------------------
simple_schema = z.schema("basic").columns(
    z.col("id").validations(z.check_is_value_empty(), z.check_is_value_duplicated()),
    z.col("age").data_type("integer"),
    z.str_col("name").aliases("full_name", "person_name"),
    z.date_col("birthdate"),
)

# ---------------------------------------------------------------------------------
# Example 2: Specialized Column Types with Validations
# ---------------------------------------------------------------------------------
detailed_schema = z.schema("detailed").columns(
    # ID column with validations
    z.col("id")
    .data_type("id")
    .required()
    .validations(z.check_is_value_empty(), z.check_is_value_duplicated()),
    # String column
    z.str_col("name")
    .sensitivity(z.Sensitivity.IDENTIFIABLE)
    .validations(z.check_is_value_empty()),
    # Integer column
    z.int_col("age").validations(z.check_is_value_empty()),
    # Date column
    z.date_col("enrollment_date")
    .aliases("date_enrolled", "enrollment")
    .validations(z.check_is_value_invalid_date(check_on_cleaned=False)),
    # Boolean column
    z.bool_col("is_active"),
    # Float column
    z.float_col("balance"),
)

# ---------------------------------------------------------------------------------
# Example 3: Column parsing/cleaning
# ---------------------------------------------------------------------------------

cleaned_schema = z.schema("cleaned_individual").columns(
    z.str_col("id")
    .clean(to="id", prefix="ORG_X::")
    .validations(
        z.check_is_value_empty(warning="any", error=0.1, reject=0.01),
        z.check_is_value_duplicated(check_on_cleaned=True, reject="any"),
    ),
    z.str_col("birthdate")
    .clean(to="date")
    .validations(z.check_is_value_invalid_date()),
    z.str_col("gender").clean(
        to="enum",
        enum_map={"m": "Male", "f": "Female", "female": "Female", "male": "Male"},
    ),
    z.str_col("is_active").clean(
        to="boolean", true_values={"yes", "active"}, false_values={"no", "inactive"}
    ),
    z.str_col("ethnicity").clean(to="sanitised_string"),
    z.str_col("ethnicity_2").clean(to="sanitised_string"),
    z.derived_col(
        "is_maori",
        function=(
            z.ref("ethnicity").clean().col.eq("maori")
            | z.ref("ethnicity_2").clean().col.eq("maori")
        ),
        data_type="boolean",
    ),
)

# ---------------------------------------------------------------------------------
# Example 4: Custom Validations
# ---------------------------------------------------------------------------------
schema_with_custom_check = z.schema("custom_checks").columns(
    z.int_col("score"),
    # Custom validation: ensure score is between 0 and 100
    z.derived_custom_check(
        name="valid_score_range",
        function=(z.ref("score").col.lt(0) & z.ref("score").col.gt(100)),
        message="Score must be between 0 and 100",
        thresholds=z.Threshold(reject=0.01),  # Reject if more than 1% fail
    ),
)
