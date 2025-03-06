{{
    config(
        materialized='incremental',
        on_schema_change='fail',
    )
}}

with

raw_policy_forge_address_type as (
    select
    type_id
    ,type_key
    ,type_desc
    ,modified
    ,cdc_snapshot
    from {{ source('prod', 'address_type') }}

    {% if is_incremental() %}

    where modified > (select coalesce(max(event_modified),'1900-01-01') from {{ this }} )

    {% endif %}
),

final as (
    select
    type_id object_system_id
    ,type_key join_key
    ,type_desc description
    ,modified event_modified
    ,'Policy Forge' source_system
    ,'{{ invocation_id }}' data_warehouse_dbt_batch_id 
    ,cdc_snapshot data_warehouse_snapshot
    from raw_policy_forge_address_type
)

select * from final
