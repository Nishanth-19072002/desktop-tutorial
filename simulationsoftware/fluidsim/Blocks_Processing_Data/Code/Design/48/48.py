import math

def execute(inputs):
    flow_capacity_of_pump_reqd = inputs['Average_flow(Cum/day)'] / inputs['Number_of_working_hours(hrs)']
    
    proposed_pumps_lps = inputs['Proposed_pumps_2_numbers(Cum/hr)'] * (1000 / 3600)

    hp_raw = (proposed_pumps_lps * inputs['Head_required(m)']) / (75 * 0.5)

    hp_reqd = math.ceil(hp_raw * 2) / 2

    outputs = {
        'Flow_Capacity_of_Pump_required(Cum/hr)': round(flow_capacity_of_pump_reqd, 2),
        'Proposed_pumps_2_numbers_perpump(lps)': round(proposed_pumps_lps, 2),
        'HP_required_for_pump(HP)': hp_reqd
    }

    return outputs