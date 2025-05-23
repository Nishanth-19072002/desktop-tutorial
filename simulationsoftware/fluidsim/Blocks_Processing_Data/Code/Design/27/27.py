import math
def execute(inputs):

    cap_pump_cum_hr = inputs['Backwash_rate(m3/hr)'] * inputs['Area_of_the_Filter_required(Sq.m)']

    inter = round((cap_pump_cum_hr/3600)*1000,3)

    hp_pum_req_hp = round(math.ceil((inter*inputs['Head_required(m)'])/(75*0.5)),3)



    outputs = {

        'Capacity_of_pump(Cum/hr)':cap_pump_cum_hr,

        "HP_required_for_pump(HP)":hp_pum_req_hp

    }



    return outputs