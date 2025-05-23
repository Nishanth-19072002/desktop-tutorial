import math
def execute(inputs):

    avg_flow_m_3_h = round(inputs['Avg_flow(KLD)']/24,3)

    vol_tank_cum = avg_flow_m_3_h*inputs['Detention_time(hrs)']

    area_tank_sqm = round(vol_tank_cum/inputs['Depth_of_the_tank(m)'],2)

    width_m = round(math.sqrt(area_tank_sqm/inputs['L:B(nil)']),3)

    length_m = width_m * inputs['L:B(nil)']



    outputs = {

        'Avg_flow(m3/h)':avg_flow_m_3_h,

        'Volume_of_tank(cum)':vol_tank_cum,

        'Area_of_the_tank(sqm)':area_tank_sqm,

        'Width(m)':width_m,

        'Length(m)':length_m,

    }



    return outputs