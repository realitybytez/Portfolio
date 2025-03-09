{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

policy_clean as (
    select
        object_system_id,
        policy_number,
        channel,
        brand,
        line_of_business,
        source_system,
        event_modified
    from silver_dev.clean.policy

    {% if is_incremental() %}

        where event_modified > (select coalesce(max(watermark), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        md5(date(event_modified) || object_system_id || source_system) as join_key,
        policy_number,
        channel,
        brand,
        line_of_business,
        source_system,
        event_modified as watermark,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id -- noqa: TMP
    from policy_clean
)

select *
from final
