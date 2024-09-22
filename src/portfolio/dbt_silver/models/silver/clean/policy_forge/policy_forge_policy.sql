with

raw_policy_forge_policy as (
    select *
    from {{ source('prod', 'policy_forge_policy') }}
),

final as (
    select * from raw_policy_forge_policy
)

select * from final
