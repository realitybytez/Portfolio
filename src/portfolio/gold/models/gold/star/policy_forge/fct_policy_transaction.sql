{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

policy_transaction_clean as (
    select
        object_system_id,
        policy_id,
        effective,
        expiration,
        source_system,
        event_modified
    from silver_dev.clean.transaction

    {% if is_incremental() %}

        where event_modified > (select coalesce(max(watermark), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        md5(date(t.event_modified) || policy_id || t.source_system) as policy_key,
        md5(date(t.event_modified) || c.object_system_id || t.source_system) as coverage_key,
        md5(date(t.event_modified) || p.object_system_id || t.source_system) as property_key,
        effective as transaction_effective,
        expiration as transaction_expiration,
        d.base_annual_premium,
        d.base_annual_premium * d.gst as gst,
        d.base_annual_premium * d.stamp_duty as stamp_duty,
        d.gross_annual_premium,
        d.excess,
        t.source_system,
        t.event_modified as watermark,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id -- noqa: TMP
    from policy_transaction_clean as t
    left join silver_dev.clean.coverage as c
        on
            t.object_system_id = c.transaction_id
            and t.source_system = c.source_system
            and t.event_modified = c.event_modified

    left join silver_dev.clean.property as p
        on
            c.object_system_id = p.coverage_id
            and c.source_system = p.source_system
            and c.event_modified = p.event_modified

    left join silver_dev.clean.premium_detail as d
        on
            t.object_system_id = d.transaction_id
            and t.source_system = d.source_system
            and t.event_modified = d.event_modified
)

select *
from final
