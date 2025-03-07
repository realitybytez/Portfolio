{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_party_policy_association as (
    select
        party_policy_id,
        policy_id,
        party_id,
        modified,
        cdc_snapshot
    from {{ source('prod', 'party_policy_association') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        party_policy_id as object_system_id,
        policy_id,
        party_id,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_party_policy_association
)

select * from final
