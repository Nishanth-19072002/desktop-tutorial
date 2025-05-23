import math

def execute(inputs):

    max_hourly_throughput_cum_h = round(inputs["Average_Flow_in_each_tank(cum/day)"]/inputs["Assume_pumping_time(h)"],3)

    design_overflow_rate_cum_h = round(inputs["Design_Overflow_rate(Cum/Sqm/day)"]/24,3)

    crs_sec_area_tank_sqm = round(max_hourly_throughput_cum_h/design_overflow_rate_cum_h,3)

    dim_for_square_tank_dia_m = round(math.sqrt(crs_sec_area_tank_sqm),3)

    solids_load_kg_h = round((max_hourly_throughput_cum_h*1000*3000)/1000000,3)

    weir_length_m = 2*dim_for_square_tank_dia_m

    weir_loading_rate_m3_rm_day = round(inputs["Average_Flow_in_each_tank(cum/day)"]/weir_length_m,3)

    volume_tank_cum = crs_sec_area_tank_sqm*inputs['Depth_of_tank(m)']

    hyd_det_time_h = round((volume_tank_cum*24)/inputs["Average_Flow_in_each_tank(cum/day)"],3)

    breadth = round(crs_sec_area_tank_sqm/inputs['Length(m)'],3)



    outputs = {

        "Max._hourly_throughput(cum/h)" : max_hourly_throughput_cum_h,

        "Design_overflow_rate(Cum/Sqm/h)" : design_overflow_rate_cum_h,

        "Cross-sectional_area_of_the_tank(sqm)" : crs_sec_area_tank_sqm,

        "Dimensions_For_a_square_tank_dia(m)" : dim_for_square_tank_dia_m,

        "Solids_load(kg/h)" : solids_load_kg_h,

        "Weir_Length_For_square_tank(m)" : weir_length_m,

        "Weir_loading_rate_For_circular_tank(m3/RM/day)" : weir_loading_rate_m3_rm_day,

        "Volume_of_tank(cum)" : volume_tank_cum,

        "Hydraulic_Detention_Time(h)" : hyd_det_time_h,

        "Breadth(m)" : breadth

    }

    return outputs