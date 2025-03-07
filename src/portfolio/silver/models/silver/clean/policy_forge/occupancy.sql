{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_occupancy as (
    select
        occupancy_id,
        occupancy_type_key,
        rental_amount,
        modified,
        cdc_snapshot
    from {{ source('prod', 'occupancy') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        occupancy_id as object_system_id,
        occupancy_type_key as occupancy_key,
        rental_amount,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_occupancy
)

select * from final
