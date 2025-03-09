{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

property_type_helper as (
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

roof_material_type_helper as (
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

wall_material_type_helper as (
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
    from silver_dev.clean.wall_material_type
),

property_clean as (
    select
        object_system_id,
        property_type_key,
        roof_material_key,
        wall_material_key,
        year_of_construction,
        source_system,
        event_modified
    from silver_dev.clean.property

    {% if is_incremental() %}

        where event_modified > (select coalesce(max(watermark), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        md5(date(p.event_modified) || p.object_system_id || p.source_system) as join_key,
        t.description as property_type,
        t2.description as roof_type,
        t3.description as wall_type,
        p.year_of_construction,
        p.source_system,
        p.event_modified as watermark,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id -- noqa: TMP
    from property_clean as p
    left join property_type_helper as t
        on
            p.property_type_key = t.join_key
            and p.event_modified >= t.start_effective
            and p.event_modified < t.end_effective
            and p.source_system = t.source_system
    left join roof_material_type_helper as t2
        on
            p.property_type_key = t2.join_key
            and p.event_modified >= t2.start_effective
            and p.event_modified < t2.end_effective
            and p.source_system = t2.source_system
    left join wall_material_type_helper as t3
        on
            p.property_type_key = t3.join_key
            and p.event_modified >= t3.start_effective
            and p.event_modified < t3.end_effective
            and p.source_system = t3.source_system
)

select *
from final
