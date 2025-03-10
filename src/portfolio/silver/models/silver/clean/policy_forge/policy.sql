{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_policy as (
    select
        policy_id,
        policy_number,
        channel,
        inception,
        brand,
        line_of_business,
        modified,
        cdc_snapshot
    from {{ source('prod', 'policy') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        policy_id as object_system_id,
        policy_number,
        channel,
        inception,
        brand,
        line_of_business,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_policy
)

select * from final
