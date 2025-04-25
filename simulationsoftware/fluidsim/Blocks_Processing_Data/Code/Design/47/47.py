import math

def execute(inputs):
    avg_flow=inputs['Avg_flow(KLD)']/24
    volume_of_tank=avg_flow*inputs['Detention_time(hrs)']
    area_of_tank=volume_of_tank/inputs['Depth_of_the_tank(m)']
    width=math.sqrt(area_of_tank/inputs['L:B(nil)'])
    length=width*inputs['L:B(nil)']

    outputs={
        'Avg_flow(m3/h)':avg_flow,
        'Volume_of_tank(cum)':volume_of_tank,
        'Area_of_the_tank(sqm)':area_of_tank,
        'Width(m)':width,
        'length(m)':length
    }

    return outputs