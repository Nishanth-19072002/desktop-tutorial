import math

def execute(inputs):

    avg_m3h = round(inputs['Avg_flow(KLD)']/24,3)

    volume_tank_cum = round((inputs['Avg_flow(KLD)'] * inputs['Detention_time(sec)'])/3600,3)

    area_tank_sqm = volume_tank_cum * inputs['Depth_of_the_tank(m)']

    width_m = round(math.sqrt((area_tank_sqm/inputs['L_B(m)'])),3)

    length_m = width_m * inputs['L_B(m)']

    outputs = {

        'Avg_flow(m3/h)':avg_m3h,

        'Volume_of_tank(cum)':volume_tank_cum,

        'Area_of_the_tank(sqm)':area_tank_sqm,

        'Width(m)':width_m,

        'Length(m)':length_m,

    }



    return outputs