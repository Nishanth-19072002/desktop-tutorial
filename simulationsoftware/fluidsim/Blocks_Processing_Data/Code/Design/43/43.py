import math



def round_up_to_nearest(x, base):

    return math.ceil(x / base) * base



def execute(inputs):

    flow_capacity_of_pump_reqd_cum = inputs['Average_flow(Cum/day)'] / inputs['Number_of_working_hours(hrs)']



    proposed2_pumps = (inputs['Proposed_pumps_2_numbers(Cum/hr)']/3600)*1000



    raw_hp = (proposed2_pumps * inputs['Head_required(m)']) / (75 * 0.5)

    hp_reqd_for_pump_hp = round_up_to_nearest(raw_hp, 0.5)



    outputs = {

        'Flow_Capacity_of_Pump_required(Cum/hr)': flow_capacity_of_pump_reqd_cum,

        'Proposed_pumps_2_numbers(Cum/hr)': proposed2_pumps,

        'HP_required_for_pump(HP)': hp_reqd_for_pump_hp

    }



    return outputs

    