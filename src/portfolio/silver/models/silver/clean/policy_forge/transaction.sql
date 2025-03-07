{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_transaction as (
    select
        transaction_id,
        policy_id,
        transaction_type_key,
        transaction_state_key,
        sequence,
        effective,
        expiration,
        modified,
        cdc_snapshot
    from {{ source('prod', 'transaction') }}

    {% if is_incremental() %}

        where modified > (select coalesce(max(event_modified), '1900-01-01') from {{ this }})

    {% endif %}
),

final as (
    select
        transaction_id as object_system_id,
        policy_id,
        transaction_type_key as transaction_type,
        transaction_state_key as transaction_state,
        sequence,
        effective,
        expiration,
        modified as event_modified,
        'Policy Forge' as source_system,
        '{{ invocation_id }}' as data_warehouse_dbt_batch_id, -- noqa: TMP
        cdc_snapshot as data_warehouse_snapshot
    from raw_policy_forge_transaction
)

select * from final
