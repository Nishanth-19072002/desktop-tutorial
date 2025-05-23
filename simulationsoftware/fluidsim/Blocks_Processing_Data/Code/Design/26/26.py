import math

def execute(inputs):

    flow_cap_pump_req_cum_hr = round(inputs['Average_flow(Cum/day)']/inputs['Number_of_working_hours(hrs)'],3)

    proposed_2_cum_hr = flow_cap_pump_req_cum_hr

    inter = round((proposed_2_cum_hr/3600)*1000)

    hp_req_pump_hp = round(math.ceil((inter*inputs['Head_required(m)'])/(75*0.5)),3)



    outputs = {

        "Flow_Capacity_of_Pump_required(Cum/hr)":flow_cap_pump_req_cum_hr,

        "Proposed_pumps_2_numbers_(1W_+_1SB),_flow_per_Pump(Cum/hr)":proposed_2_cum_hr,

        "HP_required_for_pump(HP)":hp_req_pump_hp

    }



    return outputs

