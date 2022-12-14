import pandas as pd
import requests
import os

#raceID_house = pd.read_csv('raceID_house.csv', encoding='utf_8_sig', dtype=object)
#raceID_senate = pd.read_csv('raceID_senate.csv', encoding='utf_8_sig', dtype=object)

APIKEY = os.environ.get('APAPIKEY')

# Senate
ELECTIONDATE ='2022-12-06'
OFFICEID = 'S'
res = requests.get(
    f'https://api.ap.org/v3/elections/{ELECTIONDATE}?apikey={APIKEY}&officeID={OFFICEID}&resultstype=l&format=json')

races = res.json()['races']
#races = [race for race in races if race['raceID'] in raceID_senate.raceID.to_list()]

for race in races:
    race['statePostal'] = race['reportingUnits'][0]['statePostal']
    candidates = race['reportingUnits'][0]['candidates']
    #race['voteCount_Total'] = sum([c['voteCount'] for c in candidates])
    if len([c for c in candidates if c['party']=='GOP'])==1 and len([c for c in candidates if c['party']=='Dem'])==1:
        candidate_GOP = [c for c in candidates if c['party']=='GOP'][0]
        candidate_Dem = [c for c in candidates if c['party']=='Dem'][0]
        # race['candidate_GOP'] = candidate_GOP['first'] + ' ' + candidate_GOP['last']
        # race['candidate_Dem'] = candidate_Dem['first'] + ' ' + candidate_Dem['last']
        race['voteCount_GOP'] = candidate_GOP['voteCount']
        race['voteCount_Dem'] = candidate_Dem['voteCount']
        race['voteCount_Total'] = sum([c['voteCount'] for c in candidates])
        
result = pd.DataFrame(races)
result['votePct_GOP'] = result['voteCount_GOP'] / result['voteCount_Total'] * 100
result['votePct_Dem'] = result['voteCount_Dem'] / result['voteCount_Total'] * 100
#result['votePct_Others'] = 100 - result.votePct_GOP - result.votePct_Dem
# result = result[(result.raceCallStatus=='Too Early to Call')|(result.statePostal=='GA')]
#result = result[~result.voteCount_GOP.isna()]

df = result[['statePostal', 'votePct_Dem', 'votePct_GOP', 'eevp']].reset_index(drop=True)

states = pd.read_csv('states.csv')

df.statePostal = df.statePostal.map(states.set_index('statePostal')['州名'].to_dict())

df.columns = df.columns.map(
    {'statePostal':'州', 'votePct_Dem':'民主党', 'votePct_GOP':'共和党', 'eevp':'開票率'})

df = df.set_index('州').round(1)

df.to_csv('Flourish/votePct_senate_GA.csv', encoding='utf_8_sig')
