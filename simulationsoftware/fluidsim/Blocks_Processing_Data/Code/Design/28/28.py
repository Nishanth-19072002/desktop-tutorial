def execute(inputs):

    flow_cap_req_pump_cum_hr = round(inputs['Average_flow(Cum/day)']/inputs['Flow_Capacity_of_Pump_required(Cum/hr)'],3)

    prposed_2_cum_hr = flow_cap_req_pump_cum_hr

    inter = round((prposed_2_cum_hr/3600)*1000,3)



    outputs = {

        "Flow_Capacity_of_Pump_required(Cum/hr)":flow_cap_req_pump_cum_hr,

        "Proposed_pumps_2_numbers_(1W_+_1SB),_flow_per_Pump(Cum/hr)":prposed_2_cum_hr,

    }



    return outputs