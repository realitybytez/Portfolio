{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

coverage_type_helper as (
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
    from silver_dev.clean.coverage_types
),

coverage_clean as (
    select
        object_system_id,
        coverage_key,
        source_system,
        event_modified
    from silver_dev.clean.coverage

    {% if is_incremental() %}

        where event_modified > (select coalesce(max(watermark), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        md5(date(c.event_modified) || c.object_system_id || c.source_system) as join_key,
        t.description as coverage_type,
        c.source_system,
        c.event_modified as watermark,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id -- noqa: TMP
    from coverage_clean as c
    left join coverage_type_helper as t
        on
            c.coverage_key = t.join_key
            and c.event_modified >= t.start_effective
            and c.event_modified < t.end_effective
            and c.source_system = t.source_system
)

select *
from final
