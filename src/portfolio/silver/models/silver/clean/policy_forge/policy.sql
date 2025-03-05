with

raw_policy_forge_policy as (
    select *
    from {{ source('prod', 'policy') }}
),

final as (
    select * from raw_policy_forge_policy
)

select * from final
