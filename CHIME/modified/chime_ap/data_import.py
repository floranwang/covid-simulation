from parameters import Parameters, cast_date, Disposition
from sir import Sir
from datetime import date

import csv

def main(filename):
    parsed_data = data_to_dictionary(filename)
    parameters = create_parameters(parsed_data[0])
    #print(parameters.doubling_time)
    sir = Sir(parameters)
    #print(sir.run_projection(parameters, sir.get_policies(parameters)))
    ##Remember to loop through list of dictionaries (parsed_data)
    #print(sir.raw_df)
    return sir

def data_to_dictionary(filename):
    with open(filename, newline='') as csvfile:
        dataset = csv.DictReader(open(filename), delimiter=',')
        return [x for x in dataset]

def create_parameters(parsed_data):
    hospitalized = Disposition.create(
        days=int(parsed_data['Average days hospitalized']),
        rate=float(parsed_data['Hospitalization rate']),
    )
    icu = Disposition.create(
        days=int(parsed_data['Average ICU days']),
        rate=float(parsed_data['ICU rate']),
    )
    ventilated = Disposition.create(
        days=int(parsed_data['Average ventilation days']),
        rate=float(parsed_data['Ventilation rate']),
    )

   ##remember to cast variables
    #print(parsed_data)
    p = Parameters(**{
    "current_hospitalized": int(parsed_data['Number hospitalized']),
    "current_date": date.today() if parsed_data['Today\'s date'] == '' else cast_date(parsed_data['Today\'s date']), #datetime.datetime.strptime(parsed_data['Date Today'], '%Y-%m-%d'),
    "mitigation_date": None if parsed_data['Intervention start date'] == '' else cast_date(parsed_data['Intervention start date']),
    "doubling_time": int(parsed_data['Doubling time (days)']), #optional
    "infectious_days": int(parsed_data['Latency (days)']),
    "date_first_hospitalized": None if parsed_data['Date of first hospitalization (optional)']== '' else cast_date(parsed_data['Date of first hospitalization (optional)']), #optional
    "market_share": float(parsed_data['Hospital market share']),
    "max_y_axis": None, #optional
    "n_days": 30, #number of days to project (between 1 and 30),
    "population": int(parsed_data['Population Size']),
    "recovered": int(parsed_data['Number recovered']), #parsed_data['Recovered'],
    "region": None, #optional
    "relative_contact_rate": float(parsed_data['Relative Reduction']),
    "ventilated": ventilated,
    "hospitalized": hospitalized,
    "icu": icu,
    "use_log_scale": None #optional
    })
    return p

if __name__ == "__main__":
    main("sample_data_default.csv")