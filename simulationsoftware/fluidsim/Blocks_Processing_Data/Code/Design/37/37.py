import math



def round_up_to_half(x):

    return math.ceil(x * 2) / 2



def execute(inputs):

    Flow_Capacity_of_Pump_required_cum = inputs['Average_flow(Cum/day)'] / inputs['Number_of_working_hours(hrs)'] 



    Proposed_pumps_2_numbers_per_pump_lps = (inputs['Proposed_pumps_2_numbers _flow_per_Pump(Cum/hr)'] / 3600) * 1000





    HP_required_for_pump_hp = round_up_to_half(

        (Proposed_pumps_2_numbers_per_pump_lps * inputs['Head_required(m)']) / (75 * 0.5)

    )



    return {

        'Flow_Capacity_of_Pump_required(Cum/hr)': Flow_Capacity_of_Pump_required_cum,

        'Proposed_pumps_2_numbers_per_pump(lps)': Proposed_pumps_2_numbers_per_pump_lps,

        'HP_required_for_pump(HP)': HP_required_for_pump_hp,

    }