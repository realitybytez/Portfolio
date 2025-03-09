{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

bridge_party_policy_clean as (
    select
        policy_id,
        party_id,
        source_system,
        event_modified
    from silver_dev.clean.party_policy_association

    {% if is_incremental() %}

        where event_modified > (select coalesce(max(watermark), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        md5(date(event_modified) || policy_id || source_system) as policy_key,
        md5(date(event_modified) || party_id || source_system) as party_key,
        source_system,
        event_modified as watermark,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id -- noqa: TMP
    from bridge_party_policy_clean
)

select *
from final
