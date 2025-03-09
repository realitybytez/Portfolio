{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

address_type_helper as (
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
    from silver_dev.clean.address_types
),

address_clean as (
    select
        object_system_id,
        address_key,
        address_line,
        suburb,
        postcode,
        state,
        country,
        source_system,
        event_modified
    from silver_dev.clean.address

    {% if is_incremental() %}

        where event_modified > (select coalesce(max(watermark), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        md5(date(a.event_modified) || a.object_system_id || a.source_system) as join_key,
        t.description as address_type,
        address_line,
        suburb,
        postcode,
        state,
        country,
        a.source_system,
        a.event_modified as watermark,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id -- noqa: TMP
    from address_clean as a
    left join address_type_helper as t
        on
            a.address_key = t.join_key
            and a.event_modified >= t.start_effective
            and a.event_modified < t.end_effective
            and a.source_system = t.source_system
)

select *
from final
