import math

def round_up_to_nearest(x, base):
    return math.ceil(x / base) * base

def execute(inputs):
    operating_flow = inputs['Average_Flow(Cum/day)'] / inputs['Filter_Operating_hours(hrs)']
    area_of_the_filter_reqd = operating_flow / inputs['Filter_Loading_rate(Cum/hr/Sq.m)']
    
    raw_diameter = math.sqrt((area_of_the_filter_reqd * 4) / math.pi)
    
    diameter_of_filter_reqd = round_up_to_nearest(raw_diameter, 0.1)

    outputs = {
        'Operating_flow(Cum/hr)': operating_flow,
        'Area_of_the_Filter_required(Sq.m)': area_of_the_filter_reqd,
        'Diameter_of_the_Filter_Required(m)': diameter_of_filter_reqd
    }

    return outputs