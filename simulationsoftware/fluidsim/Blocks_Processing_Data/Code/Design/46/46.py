def execute(inputs):
    capacity=inputs['Air_scouring_rate(m3/m2)']*inputs['Area_of_the_Filter_required(Sq.m)']

    outputs={
        'Capacity(Cum/hr)':capacity
    }

    return outputs