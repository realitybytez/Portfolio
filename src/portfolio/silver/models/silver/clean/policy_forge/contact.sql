{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_contact as (
    select
        contact_id,
        party_id,
        address_id,
        contact_preference,
        modified,
        cdc_snapshot
    from {{ source('prod', 'contact') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        contact_id as object_system_id,
        party_id,
        address_id,
        contact_preference,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_contact
)

select * from final
