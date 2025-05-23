import math

def execute(inputs):
    volume=inputs['Flow(Cum/h)']*inputs['Detention_time(min)']/60
    area=volume/inputs['Depth(m)']
    forsquare_tank_length=math.sqrt(area)


    outputs={
        'Volume(cum)':volume,
        'Area(m2)':area,
        'For_square_tank_Length(m)':forsquare_tank_length
    }

    return outputs
    