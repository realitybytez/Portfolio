{% test is_valid_brand(model, column_name) %}

with validation as (

    select
        {{ column_name }} as field

    from {{ model }}

),

validation_errors as (

    select field

    from validation
    where field <> 'Western Alliance'

)

select *
from validation_errors

{% endtest %}