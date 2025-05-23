

import math



def execute(inputs):

    concentration_mgl = inputs['Concentration(%)'] * 10000

    dosing_volume_per_day_cum = (inputs['Flow_rate(KLD)'] * inputs['Dosage(mg/l)']) / concentration_mgl

    dosing_capacity_lph = (dosing_volume_per_day_cum * 1000) / inputs['Working_hours_per_day(hrs)']



    outputs = {

        'Concentration (mg/l)': concentration_mgl,

        'Dosing volume per day (cum/day)': dosing_volume_per_day_cum,

        'Dosing capacity (LPH)': dosing_capacity_lph

    }



    return outputs