def execute(inputs):
    concentration=inputs['Concentration(%)']*10000
    dosing_volume_per_day=inputs['Flow_rate(KLD)']*inputs['Dosage(mg/l)']/concentration
    dosing_capacity=dosing_volume_per_day*1000/inputs['Working_hours_per_day(hrs)']

    outputs={
        'Concentration(mg/l)':concentration,
        'Dosing_volume_per_day(cum/d)':dosing_volume_per_day,
        'Dosing_capacity(LPH)':dosing_capacity

    }
    return outputs