select
p.policy_number
,p.channel
,p.inception policy_inception
,p.brand
,p.line_of_business
,tt.type_desc transaction_type
,tst.type_desc transaction_status
,t.sequence transaction_sequence
,t.effective term_start
,t.expiration term_end
,pd.base_annual_premium
,round(pd.gross_annual_premium - pd.base_annual_premium * (1 + pd.gst), 2) gst
,round(pd.gross_annual_premium - (base_annual_premium + (pd.gross_annual_premium - pd.base_annual_premium * (1 + pd.gst))), 2) stamp_duty
,pd.gross_annual_premium
from policy p
join transaction t on p.policy_id = t.policy_id
join transaction_type tt on t.transaction_type_key = tt.type_key
join transaction_status_type tst on t.transaction_state_key = tst.type_key
join premium_detail pd on t.transaction_id = pd.transaction_id
order by policy_number, sequence
limit 100;




