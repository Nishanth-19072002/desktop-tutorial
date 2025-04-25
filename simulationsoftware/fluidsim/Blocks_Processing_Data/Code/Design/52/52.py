import math

def execute(inputs):
    average_flow = inputs['Avg_flow(KLD)'] / 24

    volume_of_tank = average_flow * inputs['Detention_time(hrs)']

    area_of_tank = volume_of_tank / inputs['Depth_of_the_tank(m)']

    length = math.sqrt(area_of_tank / inputs['B:L(nil)'])
    width = length * inputs['B:L(nil)']

    outputs = {
        'Avg_flow(m3/h)': average_flow,
        'Volume_of_tank(cum)': volume_of_tank,
        'Area_of_the_tank(sqm)': area_of_tank,
        'Length(m)': length,
        'Width(m)': width
    }

    return outputs