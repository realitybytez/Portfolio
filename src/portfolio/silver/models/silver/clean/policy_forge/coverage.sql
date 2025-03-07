{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_coverage as (
    select
        coverage_id,
        coverage_type_key,
        transaction_id,
        modified,
        cdc_snapshot
    from {{ source('prod', 'coverage') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        coverage_id as object_system_id,
        coverage_type_key as coverage_key,
        transaction_id,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_coverage
)

select * from final
