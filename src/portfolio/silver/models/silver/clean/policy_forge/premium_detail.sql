{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_premium_detail as (
    select
        premium_detail_id,
        transaction_id,
        base_annual_premium,
        gst,
        stamp_duty,
        gross_annual_premium,
        excess,
        modified,
        cdc_snapshot
    from {{ source('prod', 'premium_detail') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        premium_detail_id as object_system_id,
        transaction_id,
        base_annual_premium,
        gst,
        stamp_duty,
        gross_annual_premium,
        excess,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_premium_detail
)

select * from final
