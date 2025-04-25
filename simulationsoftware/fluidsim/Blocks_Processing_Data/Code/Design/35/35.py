import math

def execute(inputs):
    avg_flow_m3ph = inputs['Avg_flow(KLD)'] / 24  

    volume_of_tank_cum =avg_flow_m3ph * inputs['Detention_time(h)'] / 60

    area_of_tank_sqm = volume_of_tank_cum / inputs['Depth_of_the_tank(m)'] 

    width_m = math.sqrt(area_of_tank_sqm / inputs['L:W(nil)']) 

    length_m = width_m * inputs['L:W(nil)'] 


    outputs = {
        'Avg_flow(m3/h)': avg_flow_m3ph,
        'Volume_of_tank(cum)': volume_of_tank_cum,
        'Area_of_the_tank(sqm)': area_of_tank_sqm,
        'Width(m)': width_m,
        'Length(m)': length_m
    }

    return outputs