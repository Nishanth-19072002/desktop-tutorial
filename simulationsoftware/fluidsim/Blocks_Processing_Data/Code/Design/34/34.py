import math


def execute(inputs):
    avg_flow_m3ph = inputs['Avg_flow(KLD)'] / 24 
    volume_of_tank_cum = inputs['Avg_flow(KLD)'] * inputs['Detention_time(sec)'] / 3600 
    area_of_tank_sqm = volume_of_tank_cum / inputs['Depth_of_the_tank(m)']
    width_m = math.sqrt(area_of_tank_sqm / inputs['L:B(m)'])
    length_m = width_m * inputs['L:B(m)']

    outputs= {
        'Avg_flow(m3/h)': avg_flow_m3ph,
        'Volume_of_tank(cum)': volume_of_tank_cum,
        'Area_of_the_tank(sqm)': area_of_tank_sqm,
        'Width(m)': width_m,
        'Length(m)': length_m
    }

    return outputs