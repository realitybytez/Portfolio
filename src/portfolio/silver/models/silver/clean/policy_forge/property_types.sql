{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_property_type as (
    select
        type_id,
        type_key,
        type_desc,
        modified,
        cdc_snapshot
    from {{ source('prod', 'property_type') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        type_id as object_system_id,
        type_key as join_key,
        type_desc as description,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_property_type
)

select * from final
