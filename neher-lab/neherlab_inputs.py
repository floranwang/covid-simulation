import json
import pandas as pd
import math

input_data = pd.read_csv('../Simulator - Test Sheet - Sample Data.csv')
# print(input_data)
json_input = {}

with open('ageDistribution.json') as f:
  ageDistribution = json.load(f)

with open('scenarios.json') as f:
  scenarios = json.load(f)

with open('severityDistributions.json') as f:
  severityDistributions = json.load(f)

with open('c19s.params.json') as f:
  example = json.load(f)

def getDefault(country, json_dict):
    for data_dict in json_dict['all']:
        if data_dict['name'] == country:
            return data_dict
    return {}

def customizeAgeDistribution(input_row, ageDistribution):
    customAgeDist = [input_row['Age 0-9'], input_row['Age 10-19'], input_row['Age 20-29'], input_row['Age 30-39'],
                    input_row['Age 40-49'], input_row['Age 50-59'], input_row['Age 60-69'], input_row['Age 70-79'], 
                    input_row['Age 80+']]
    for i in range(len(ageDistribution['data'])):
        if not math.isnan(customAgeDist[i]):
            ageDistribution['data'][i]['population'] = customAgeDist[i]
    return ageDistribution

def customizeEpi(input_row, epi_dict):
    if not math.isnan(input_row['Average days hospitalized']):
        epi_dict['hospitalStayDays'] = input_row['Average days hospitalized']
    if not math.isnan(input_row['Average ICU days']):
        epi_dict['hospitalStayDays'] = input_row['Average ICU days']
    if not math.isnan(input_row['Infectious period (days)']):
        epi_dict['infectiousPeriodDays'] = input_row['Infectious period (days)']
    if not math.isnan(input_row['Latency (days)']):
        epi_dict['latencyDays'] = input_row['Latency (days)']
    if not math.isnan(input_row['R0']):
        epi_dict['r0'] = {'begin': input_row['R0']-0.4, 'end':input_row['R0']+0.4}
    return epi_dict

def customizeMit(input_row, mit_dict):
    if not pd.isnull(input_row['Intervention start date']):
        mit_dict['timeRange']['begin'] = input_row['Intervention start date']
    if not pd.isnull(input_row['Intervention end date']):
        mit_dict['timeRange']['end'] = input_row['Intervention end date']
    if not math.isnan(input_row['Intervention efficacy min']):
        mit_dict['transmissionReduction']['begin'] = input_row['Intervention efficacy min']
    if not math.isnan(input_row['Intervention efficacy max']):
        mit_dict['transmissionReduction']['end'] = input_row['Intervention efficacy max']
    return mit_dict

def customizePop(input_row, pop_dict):
    if not math.isnan(input_row['# hospital beds']):
        pop_dict['hospitalBeds'] = input_row['# hospital beds']
    if not math.isnan(input_row['# ICU beds']):
        pop_dict['icuBeds'] = input_row['# ICU beds']
    if not math.isnan(input_row['Imports per day']):
        pop_dict['icuBeds'] = input_row['# ICU beds']
    if not math.isnan(input_row['Initial number of cases']):
        pop_dict['initialNumberOfCases'] = input_row['Initial number of cases']
    if not math.isnan(input_row['Population Size']):
        pop_dict['populationServed'] = input_row['Population Size']
    return pop_dict

def customizeSim(input_row, sim_dict):
    if not pd.isnull(input_row['Simulation time range- beginning']):
        sim_dict['simulationTimeRange']['begin'] = input_row['Simulation time range- beginning']
    if not pd.isnull(input_row['Simulation time range- end']):
        # print(input_row['Simulation time range- end'])
        # print(len(input_row['Simulation time range- end']))
        sim_dict['simulationTimeRange']['end'] = input_row['Simulation time range- end']
    return sim_dict

for idx, row in input_data.iterrows():
    # print(row)
    country = row['Country']
    if country == 'USA':
        country = 'United States of America'
    json_input['ageDistributionData'] = getDefault(country, ageDistribution)
    json_input['ageDistributionData'] = customizeAgeDistribution(row, json_input['ageDistributionData'])

    json_input['scenarioData'] = getDefault(country, scenarios)
    json_input['scenarioData']['data']['epidemiological'] = customizeEpi(row, json_input['scenarioData']['data']['epidemiological'])
    json_input['scenarioData']['data']['mitigation']['mitigationIntervals'][0] = customizeMit(row, json_input['scenarioData']['data']['mitigation']['mitigationIntervals'][0])
    json_input['scenarioData']['data']['population'] = customizePop(row, json_input['scenarioData']['data']['population'])
    json_input['scenarioData']['data']['simulation'] = customizeSim(row, json_input['scenarioData']['data']['simulation'])
    

    json_input['schemaVer'] = '2.0.0'

    json_input['severityDistributionData'] = example['severityDistributionData']

    with open(country + '.json', 'w') as json_file:
        json.dump(json_input, json_file)

print(json_input)
# print()
# print()

