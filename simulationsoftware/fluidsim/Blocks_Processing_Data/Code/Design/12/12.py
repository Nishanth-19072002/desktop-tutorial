def execute(inputs):

    hourly_sewage_flow_cum_h = round(inputs['Avg_Flow(Cum/day)']/24,3)

    volume_tank_cum = hourly_sewage_flow_cum_h*inputs['Assumed_Detention_period(hours)']

    volume_each_tank_cum = round(volume_tank_cum / inputs['No._of_Tanks_Proposed(nil)'],3)

    area_equalization_tank_sqm = round(volume_each_tank_cum/inputs['Assumed_Depth_of_Liquid_column(m)'],3)

    area_each_equalization_tank_sqm = round(area_equalization_tank_sqm/inputs['No._of_Tanks_Proposed(nil)'],3)

    length_tank_m = round(area_each_equalization_tank_sqm/inputs['Breadth_of_the_tank(m)'],3)



    outputs = {

        'Hourly_sewage_flow(cum/h)':hourly_sewage_flow_cum_h,

        'Volume_of_the_Tank(Cum)':volume_tank_cum,

        'Volume_of_each_tank(Cum)':volume_each_tank_cum,

        'Area_required_for_the_equalization_tank(Sq.m)':area_equalization_tank_sqm,

        'area_required_for_each_equalization_tank(Sq.m)':area_each_equalization_tank_sqm,

        'Length_of_the_tank(m)':length_tank_m,

    }



    return outputs