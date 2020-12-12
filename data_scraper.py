from requests_html import HTMLSession
import re

#Helper script to scrape in specific table data from rr pages

session = HTMLSession()

#TODO 1999 is a special case which requires iteration through wikitable sortable selectors to find one with at least 6 table headers
#TODO 2018 on is a special case due to Womens' Royal Rumble -- all that we need to do is same as 1999. Iterate for each case of wikitable sortable with at least 6 table headers
#TODO regex seems to be considering 'and' as a participant in the case of a comma followed by and or &
rs = session.get('https://en.wikipedia.org/wiki/WWE_Greatest_Royal_Rumble')
#https://en.wikipedia.org/wiki/WWE_Greatest_Royal_Rumble -- works!
#https://en.wikipedia.org/wiki/Royal_Rumble_(2018)

#tab = rs.html.find('table')
sel = "table.wikitable.sortable"

table_dataset = rs.html.find(sel)

#Find number of table headers
table_headers = table_dataset[0].find('th')
header_count = len(table_headers)


table_data = table_dataset[0].find('td')
count = 0
six_headers = "Draw | Entrant | Order | Eliminated By | Time | Eliminations\n"
seven_headers = "Draw | Entrant | Brand | Order | Eliminated By | Time | Eliminations\n"
max_col_count = header_count

if header_count > 6:
    print(seven_headers)
else:
    print(six_headers)

multi_elim = ""
row_span_count = 0
entry_line = ""

for td in table_data:
    #print(f"full z: {z.text}")

    #check for rowspan
    if count == (header_count - 3):
        if td.attrs.get('rowspan') is not None:
            multi_elim = td.text
            #row_span_count = int(z.attrs.get('rowspan'))
            #print(z.attrs.get('rowspan'))
        else:
            #check if there are multiple eliminators
            eliminations = td.text
            #print(eliminations)
            if "and" in eliminations or "&" in eliminations or "," in eliminations:
                #print("Found multiples")
                #regex the string and replace "and" or "&" with ","
                eliminations = re.sub("\s+and\s+", ",", eliminations)
                eliminations = re.sub("&", ",", eliminations)
                #print(eliminations)
                #split the string

                elim_split = eliminations.split(",")
                #elim_split = eliminations.split("&")
                print(elim_split)



    if (count == header_count - 3) and (td.text.isnumeric() is True or ":" in td.text):
    #if count == 3 and row_span_count > 0:
        #print('WAS NUMERIC')
        #print("The text: " + z.text)
        max_col_count = header_count - 1
        #row_span_count -= 1
        entry_line += (multi_elim + " | " + td.text + " | ")
    else:
        entry_line += (td.text + " | ")

    count += 1
    if count == max_col_count:
        count = 0
        max_col_count = header_count
        entry_line += "\n"
        print(entry_line)
        entry_line = ""


#print(rs.html.find(sel))
#print(rs.html.absolute_links)
#print(tab)

#print(rs.text)