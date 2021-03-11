import datetime
import json
from xml.etree import ElementTree as ET
import time

input_filename = 'feed_sample.xml'
output_filename = 'feed_out.xml'

t0 = time.time()

def areOpen(opening_today, closing_today, opening_tomorrow, time):
    midnight = '00:00'
    if opening_today == midnight:
        opening_earlier = True
    elif opening_today < time or opening_today == time:
        opening_earlier = True
    else:
        opening_earlier = False

    if closing_today == time and opening_tomorrow == 'closed':
        closing_later = False
    elif closing_today == opening_tomorrow:
        closing_later = True
    elif closing_today == midnight:
        closing_later = True
    else:
        if opening_today > closing_today:
            closing_later = time > closing_today
        else:
            closing_later = time < closing_today

    return opening_earlier and closing_later


active_offers = 0
paused_offers = 0

output = open(output_filename, 'w', buffering=12800000, newline='\n', encoding='UTF-8')
output.write('<?xml version="1.0" encoding="UTF-8"?>\n<offers>\n')

now = datetime.datetime.now().strftime('%H:%M')
today = datetime.datetime.today()
current_weekday = today.weekday() + 1
tomorrow = (today + datetime.timedelta(days=1)).weekday() + 1

xml_iter = ET.iterparse(input_filename)
for event, elem in xml_iter:
    for offer in elem.findall('offer'):
        is_active = None
        opening_times = json.loads(offer.find('opening_times').text)
        try:
            opening_today = opening_times[f'{current_weekday}'][0].get('opening')
            closing_today = opening_times[f'{current_weekday}'][0].get('closing')
        except IndexError:
            is_active = False
        except KeyError:
            is_active = False
        try:
            opening_tomorrow = opening_times[f'{tomorrow}'][0].get('opening')
        except IndexError:
            opening_tomorrow = 'closed'
        except KeyError:
            opening_tomorrow = 'closed'

        if is_active is None:
            is_active = areOpen(opening_today, closing_today, opening_tomorrow, now)

        if is_active:
            active_offers += 1
        else:
            paused_offers += 1

        active_tag = ET.Element('is_active')
        active_tag.text = f'{is_active}'.lower()
        offer.append(active_tag)
        offer_string = ET.tostring(offer, encoding="UTF-8")
        output.write(offer_string.decode())


total_active = ET.Element('total_active')
total_active.text = str(active_offers)
total_paused = ET.Element('total_paused')
total_paused.text = str(paused_offers)

output.write(f'\n<total_active>{active_offers}</total_active>\n<total_paused>{paused_offers}</total_paused>\n</offers>')

print(f'Finished in {time.time() - t0} s.')
