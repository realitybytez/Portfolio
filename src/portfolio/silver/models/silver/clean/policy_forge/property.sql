{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_property as (
    select
        property_id,
        coverage_id,
        property_type_key,
        roof_material_key,
        wall_material_key,
        occupancy_id,
        year_of_construction,
        sum_insured,
        modified,
        cdc_snapshot
    from {{ source('prod', 'property') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        property_id as object_system_id,
        coverage_id,
        property_type_key,
        roof_material_key,
        wall_material_key,
        occupancy_id,
        year_of_construction,
        sum_insured,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_property
)

select * from final
