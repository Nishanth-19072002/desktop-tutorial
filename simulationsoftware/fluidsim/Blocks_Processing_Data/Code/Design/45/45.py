import math

def round_up_to_nearest(x, base):
    return math.ceil(x / base) * base

def execute(inputs):
    capacity_of_pump = inputs['Backwash_rate(m3/m2)'] * inputs['Area_of_the_Filter_required(Sq.m)']

    capacity_of_pump_lps = (capacity_of_pump * 1000) / 3600

    hp_reqd_pump = round_up_to_nearest((capacity_of_pump_lps * inputs['Head_required(m)']) / (75 * 0.5), 0.5)

    outputs = {
        'Capacity_of_pump(Cum/hr)': capacity_of_pump,
        'Capacity_of_pump(LPS)': capacity_of_pump_lps,
        'HP_required_for_pump(HP)': hp_reqd_pump
    }

    return outputs