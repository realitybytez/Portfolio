{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

occupancy_type_helper as (
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
    from silver_dev.clean.occupation_types
),

occupancy_clean as (
    select
        object_system_id,
        occupancy_key,
        source_system,
        event_modified
    from silver_dev.clean.occupancy

    {% if is_incremental() %}

        where event_modified > (select coalesce(max(watermark), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        md5(date(o.event_modified) || o.object_system_id || o.source_system) as join_key,
        t.description as occupancy_type,
        o.source_system,
        o.event_modified as watermark,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id -- noqa: TMP
    from occupancy_clean as o
    left join occupancy_type_helper as t
        on
            o.occupancy_key = t.join_key
            and o.event_modified >= t.start_effective
            and o.event_modified < t.end_effective
            and o.source_system = t.source_system
)

select *
from final
