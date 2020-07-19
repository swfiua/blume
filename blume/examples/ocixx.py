"""
Ottawa c19

Data thanks to open ottawa

https://open.ottawa.ca/datasets/covid-19-source-of-infection/geoservice
"""
from matplotlib import pyplot as plt
import requests
import json


URL = "https://opendata.arcgis.com/datasets/de83f9e01278463e916f14121d5980d1_0/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"



if __name__ == '__main__':

    from pprint import pprint
    
    resp = requests.get(URL)

    data = resp.content

    print(len(data))

    data = json.loads(data)

    print(len(data['features']))

    print(data.keys())

    print(data['exceededTransferLimit'])

    results = [x['attributes'] for x in data['features']]

    pprint(results[0])
    pprint(results[-1])

    keys =[
        '%_No_Known_Source_for_Cases_with_non-institutional__source_of_infection_over_the_last_14_days',
        'No_Information_Available',
        'No_Known_Source_of_Infection',
        'Outbreak_or_Close_Contact_with_a_Case',
        #'Sum_of_Non-institutional_Source_of_Infection_Over_the_Last_14_Days',
        'Travel']
           
    for key in keys:
        plt.plot([x[key] for x in results], label=key)

        plt.legend(loc=0)
    plt.show()

    
