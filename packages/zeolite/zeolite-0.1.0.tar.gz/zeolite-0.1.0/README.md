# ⚗️ Zeolite

---

Zeolite is a Python library that uses a simple configuration approach to define a table/schema structure. Raw
data can normalised, cleaned, and validated against the schema in a performant and standardised way. 

The final datasets are guaranteed to be in the correct format and can be easily exported to a variety of formats. 
In addition, Zeolite captures errors and warnings during the processing of the data, which can be used to improve 
the quality of the data.



### Example

```python
import zeolite as z

individual_schema = z.schema("individual").columns(
    z.str_col("id")
    .clean(to="id", prefix="ORG_X::")
    .validations(
        z.check_is_value_empty(warning="any", error=0.1, reject=0.01, treat_empty_strings_as_null=True),
        z.check_is_value_duplicated(check_on_cleaned=True, reject="any"),
    ),
    
    z.str_col("birthdate")
    .clean(to="date")
    .validations(z.check_is_value_invalid_date(reject="all")),
    
    z.str_col("gender").clean(
        to="enum",
        sanitize="lowercase",
        enum_map={
            "m": "Male", "male": "Male",
            "f": "Female", "female": "Female",  
            "d":"Gender Diverse", "diverse": "Gender Diverse"
        },
    ),
    
    z.str_col("is_active").clean(
        to="boolean", 
        true_values={"yes", "active"}, false_values={"no", "inactive"}
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


```