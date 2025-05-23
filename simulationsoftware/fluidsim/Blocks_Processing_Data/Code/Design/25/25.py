import math
def execute(inputs):
    returned_sludge_pump_cum_day = round(((inputs['Assumed_return_flow(%)']/100)*inputs['Average_Sewage_flow_entering_the_treatment_plant(KLD)'])/inputs['No._of_pumps(nil)'],3)
    pump_cap_req_cum_hr = round(returned_sludge_pump_cum_day/inputs['Operating_hours(hrs)'],3)
    inter = pump_cap_req_cum_hr * 0.277777777777778
    power_req_pump = round(math.ceil((inter*inputs['Head_required(m)'])/((75*0.5))),3)

    outputs = {
        "Return_sludge_Pumps(Cum/day)":returned_sludge_pump_cum_day,
        "Capacity_of_pump_required(Cum/hr)": pump_cap_req_cum_hr,
        "Power_requirement_for_the_Pump(Hp)":power_req_pump
    }
    
    return outputs