import math



def round_up_to_half(x):

    return math.ceil(x * 2) / 2



def execute(inputs):

    Hourly_sewage_flow_cum = inputs['Peak_Flow(Cum/day)'] / 24

    Volume_of_the_Tank_cum = Hourly_sewage_flow_cum * inputs['Assumed_Detention_period(hours)']

    Volume_of_each_tank_cum = Volume_of_the_Tank_cum / inputs['No_of_Tanks_Proposed(nil)']

    

    Area_required_for_the_equalization_tank_sqm = Volume_of_the_Tank_cum / inputs['Assumed_Depth_of_Liquid_column(m)']

    area_required_for_each_equalization_tank_sqm = Area_required_for_the_equalization_tank_sqm / inputs['No_of_Tanks_Proposed(nil)']

    

    Breadth_of_the_tank_m = round_up_to_half(math.sqrt(area_required_for_each_equalization_tank_sqm / inputs['Length_to_Breadth_ratio(nil)']))

    Length_of_the_tank_m = Breadth_of_the_tank_m * inputs['Length_to_Breadth_ratio(nil)']

    

    AirBlower_capacity_required_for_each_tank_m3h = inputs['Air_mixing_rate_per_tank_volume(Nm3/h)'] * Volume_of_each_tank_cum

    TotalAir_blower_capacity_required_m3h = AirBlower_capacity_required_for_each_tank_m3h * inputs['No_of_Tanks_Proposed(nil)']

    

    No_of_diffusers_reqd_no = TotalAir_blower_capacity_required_m3h / inputs['Air_Flux_rate(m3/h)']



    outputs = {

        'Hourly_sewage_flow(cum/h)': Hourly_sewage_flow_cum,

        'Volume_of_the_Tank(cum)': Volume_of_the_Tank_cum,

        'Volume_of_each_tank(cum)': Volume_of_each_tank_cum,

        'Area_required_for_equalization_tank(Sq.m)': Area_required_for_the_equalization_tank_sqm,

        'area_required_for_each_equalization_tank(Sq.m)': area_required_for_each_equalization_tank_sqm,

        'Breadth_of_the_tank(m)': Breadth_of_the_tank_m,

        'Length_of_the_tank(m)': Length_of_the_tank_m,

        'AirBlower_capacity_required_for_each_tank(m3/h)': AirBlower_capacity_required_for_each_tank_m3h,

        'TotalAir_blower_capacity_required(m3/h)': TotalAir_blower_capacity_required_m3h,

        'No_of_diffusers_reqd(No)': No_of_diffusers_reqd_no

    }



    return outputs

