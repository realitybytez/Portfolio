{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

transaction_type_helper as (
    select
        *,
        case
            when lag(event_modified) over (partition by join_key order by event_modified) is null then event_modified
            else event_modified
        end as start_effective,
        case
            when lead(event_modified) over (partition by join_key order by event_modified) is null then '9999-12-31 23:59:59.999'
            else lead(event_modified) over (partition by join_key order by event_modified)
        end as end_effective
    from silver_dev.clean.property_types
),

transaction_state_type_helper as (
    select
        *,
        case
            when lag(event_modified) over (partition by join_key order by event_modified) is null then event_modified
            else event_modified
        end as start_effective,
        case
            when lead(event_modified) over (partition by join_key order by event_modified) is null then '9999-12-31 23:59:59.999'
            else lead(event_modified) over (partition by join_key order by event_modified)
        end as end_effective
    from silver_dev.clean.roof_material_type
),

policy_transaction_clean as (
    select
        object_system_id,
        transaction_type,
        transaction_state,
        sequence,
        source_system,
        event_modified
    from silver_dev.clean.transaction

    {% if is_incremental() %}

        where event_modified > (select coalesce(max(watermark), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        md5(date(pt.event_modified) || pt.object_system_id || pt.source_system) as join_key,
        t.description as transaction_type,
        t2.description as transaction_state,
        pt.source_system,
        pt.event_modified as watermark,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id -- noqa: TMP
    from policy_transaction_clean as pt
    left join transaction_type_helper as t
        on
            pt.transaction_type = t.join_key
            and pt.event_modified >= t.start_effective
            and pt.event_modified < t.end_effective
            and pt.source_system = t.source_system
    left join transaction_state_type_helper as t2
        on
            pt.transaction_state = t2.join_key
            and pt.event_modified >= t2.start_effective
            and pt.event_modified < t2.end_effective
            and pt.source_system = t2.source_system
)

select *
from final
