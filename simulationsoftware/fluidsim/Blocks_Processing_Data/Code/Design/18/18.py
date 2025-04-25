import math
def execute(inputs):
    oper_flow_cum_hr = round(inputs['Average_Flow(Cum/day)']/inputs['Filter_Operating_hours(hrs)'],3)

    area_filter_sqm = round(oper_flow_cum_hr/inputs['Filter_Loading_rate(Cum/hr/Sq.m)'],3)

    diameter_filter_m = round(math.ceil(math.sqrt(((area_filter_sqm*4)/math.pi))),3)



    outputs = {

        "Operating_flow(Cum/hr)":oper_flow_cum_hr,

        "Area_of_the_Filter_required(Sq.m)":area_filter_sqm,

        "Diameter_of_the_Filter_Required(m)":diameter_filter_m

    }



    return outputs