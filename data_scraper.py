from requests_html import HTMLSession
import re

#Helper script to scrape in specific table data from rr pages

session = HTMLSession()


def produce_data(table_feed, header_count):
    table_data = table_feed.find('td')
    count = 0
    six_headers = "Draw | Entrant | Order | Eliminated By | Time | Eliminations\n"
    seven_headers = "Draw | Entrant | Brand | Order | Eliminated By | Time | Eliminations\n"
    max_col_count = header_count

    if header_count > 6:
        print(seven_headers)
    else:
        print(six_headers)

    multi_elim = ""
    entry_line = ""

    for td in table_data:
        # check for rowspan
        if count == (header_count - 3):
            if td.attrs.get('rowspan') is not None:
                multi_elim = td.text
            else:
                # check if there are multiple eliminators
                eliminations = td.text
                if "and" in eliminations or "&" in eliminations or "," in eliminations:
                    # TODO regex seems to be considering 'and' as a participant in the case of a comma followed by and or &
                    # regex the string and replace "and" or "&" with ","
                    eliminations = re.sub("\s+and\s+", ",", eliminations)
                    eliminations = re.sub("&", ",", eliminations)
                    # split the string
                    elim_split = eliminations.split(",")
                    print(elim_split)

        if (count == header_count - 3) and (td.text.isnumeric() is True or ":" in td.text):
            max_col_count = header_count - 1
            entry_line += (multi_elim + " | " + td.text + " | ")
        else:
            entry_line += (td.text + " | ")

        count += 1
        if count == max_col_count:
            #reset everything
            count = 0
            max_col_count = header_count
            entry_line += "\n"
            print(entry_line)
            entry_line = ""


#TODO begin generating cypher queries and dropping them into an aptly named file
#TODO once table_data is done reading, grab data for the next link and keep the ball rolling
rs = session.get('https://en.wikipedia.org/wiki/Royal_Rumble_(2018)')
#https://en.wikipedia.org/wiki/WWE_Greatest_Royal_Rumble -- works!
#https://en.wikipedia.org/wiki/Royal_Rumble_(2018)

sel = "table.wikitable.sortable"

table_dataset = rs.html.find(sel)

for table in table_dataset:
    if len(table.find('th')) >= 6:
       produce_data(table, len(table.find('th')))



#print(rs.html.find(sel))
#print(rs.html.absolute_links)
#print(tab)

#print(rs.text)