# Importer les modules
import requests
import yaml
from bs4 import BeautifulSoup
from itertools import groupby
# Adresse du site Internet
url = "https://snowcamp2024.sched.com/list/descriptions/"
# Exécuter la requête GET
response = requests.get(url)
# Get Big dates
html = BeautifulSoup(response.text, 'html.parser')
get_sched_dates=html.find_all('div',class_="sched-current-date")

dates_list=list()
for event in get_sched_dates:
    dates_list.append(event.text)
    
for i in range(0,len(dates_list)):
    dates_list[i]=dates_list[i].replace(",","")

res=[]
get_sched_container=html.find_all('div',class_="sched-container")
# print(get_sched_container[0])
for container in get_sched_container:
    # print(container)
    cont_date=container.find('div',class_="sched-event-details-timeandplace")
    cont_date=cont_date.text
    date=cont_date.split(',')[0].replace("\n","")
    
    # print(heure)
    for d in dates_list:

        if d==date:
            obj={}
            obj["event_date"]=date
            salle=cont_date.split(',')[1]
            salle=salle.split('-')[1].split("CET")[1].split("WTC")[0].replace("\n","")
            obj["salle"]=salle
            
            heure=cont_date.split(',')[1]
            #Split on - take the first string then replace line return character with space then split on the second space and take the third string in the strings array
            heure=heure.split('-')[0].replace("\n","").split(" ",2)[2]
            obj["heure"]=heure
            event_name=container.find('a', class_="name")
            tags=container.find("ul",class_="tip-custom-fields")
            tag=tags.find('a')
            
            if tag!=None:
                obj["tags"]=tag.text
            else:
                obj["tags"]='Tag introuvable'
            resume=container.find('div',class_="tip-description")
            
            if resume != None:
                obj["resume"]=resume.text.replace('<br/>',' ')
            else:
                obj["resume"]='Résumé Introuvable'
                
            speaker=container.find('div',class_="sched-person-session")
            
            if speaker != None:
                speaker=speaker.find('h2')
                speaker=speaker.find('a')
                speaker=speaker.text
                
            else:
                speaker='Speaker Introuvable'
                
            obj["speaker"]=speaker
            event_type=container.find("div",class_="sched-event-type")
            event_type=event_type.find("a").text
            obj["event_type"]=event_type
            obj["event"]=event_name.text.replace("\n","").replace("   ","")
            res.append(obj)
# print(res)
res.sort(key=lambda x: (x['event_date'], x['salle']))

# Group the data by 'event_date'
grouped_by_date = groupby(res, key=lambda x: x['event_date'])

# Iterate through groups and print the results
event_list=[]
for date, events_in_date_group in grouped_by_date:
    # Group the events within each date by 'salle'
    grouped_by_salle = groupby(events_in_date_group, key=lambda x: x['salle'])
    # print(date)
    for salle, events_in_salle_group in grouped_by_salle:

        salle_events = []
        
        for event in events_in_salle_group:
            # Create a dictionary for each event
            event_dict = {
                'heure': event['heure'],
                'titre': event['event'].replace("  ",""),
                'tags': event['tags'],
                'resume': event['resume'].replace("\n", "").replace("  ",""),
                'event_type': event["event_type"].replace("\n", ""),
                'speaker': event['speaker']
            }
            
            # Append the event dictionary to the salle_events list
            salle_events.append(event_dict)
        
        # Create a dictionary for the current 'salle' and date
        salle_dict = {
            'salle': salle,
            'events': salle_events
        }
            
        # Append the salle dictionary to the event_list
        event_list.append({
            'date': date,
            'salle_info': salle_dict
        })
# Convert the list of dictionaries to YAML
yaml_data = yaml.dump(event_list, default_flow_style=False, allow_unicode=True)

# Write YAML data to a file
with open("output.yaml", "w", encoding="utf-8") as yaml_file:
    yaml_file.write(yaml_data)