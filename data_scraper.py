from requests_html import HTMLSession
import re

# Helper script to scrape in specific table data from rr pages

session = HTMLSession()
regex = "(,)*\s*(&|and)\s+"

def generate_cypher_data(file, info_dict):

    for inf in info_dict:
        alias = inf['wrestler'].replace(" ", "")
        alias = re.sub("\W*", "", alias)
        file.write("MERGE (" + alias + ":Wrestler {name:'" + inf['wrestler'] + "'})\n")

    file.close()

def produce_data(e_title, table_feed, header_count):
    # first we generate the event creation query
    # next, we generate the wrestlers
    # then we generate the participants in the event
    # then, we create the eliminations
    # finally, we add in the winner
    #print(e_title)#
    #regex to strip year out
    year_regex = '[^(](\d+)[^)]'
    current_year_search = re.search(year_regex, e_title)
    #print(current_year.group(0))
    current_year = current_year_search.group(0)
    cypher_doc = open('cypher_setup_data/cypher_data_' + e_title + ".txt", 'w')
    cypher_doc.write("//Event\n")
    cypher_doc.write("CREATE (RR" + current_year + ":Event { name:'" + e_title + "', year:" + current_year + "})\n")
    cypher_doc.write("//Wrestlers\n")

    table_data = table_feed.find('td')
    count = 0
    six_headers = "Draw | Entrant | Order | Eliminated By | Time | Eliminations\n"
    seven_headers = "Draw | Entrant | Brand | Order | Eliminated By | Time | Eliminations\n"
    max_col_count = header_count
    current_wrestler = ""
    draw = ""
    order = ""
    eliminators = ""
    time_in = ""

    if header_count > 6:
        print(seven_headers)
    else:
        print(six_headers)

    multi_elim = ""
    entry_line = ""
    info_dict = []
    current_dict = {}

    for td in table_data:
        # check for rowspan
        if count == 0:
            #draw = td.text
            current_dict['draw'] = td.text
        if count == 1:
            #current_wrestler = td.text
            current_dict['wrestler'] = td.text
        if count == 2 and header_count <= 6: #check for brand split and header_count <= 6
            current_dict['order'] = td.text
            #draw = td.text
        elif count == 2 and header_count >= 7:
            current_dict['brand'] = td.text
        if count == 3 and header_count == 7:
            current_dict['order'] = td.text

        if count == header_count-2:
            current_dict["time_in"] = td.text

        if count == (header_count - 3):
            if td.attrs.get('rowspan') is not None:
                multi_elim = td.text
                current_dict['eliminators'] = multi_elim
            else:
                # check if there are multiple eliminators
                eliminations = td.text
                current_dict['eliminators'] = eliminations
                if "and" in eliminations or "&" in eliminations or "," in eliminations:
                    eliminations = re.sub(regex, ",", eliminations)
                    # split the string
                    elim_split = eliminations.split(",")
                    #print(elim_split)
                    current_dict['eliminators'] = elim_split

        if (count == header_count - 3) and (td.text.isnumeric() is True or ":" in td.text):
            max_col_count = header_count - 1
            entry_line += (multi_elim + " | " + td.text + " | ")
            current_dict['eliminators'] = multi_elim
            #info_dict['time_in'] = td.text
        else:
            entry_line += (td.text + " | ")
            #info_dict['time_in'] = td.text

        count += 1
        if count == max_col_count:
            # reset everything
            count = 0
            max_col_count = header_count
            entry_line += "\n"
            print(entry_line)
            entry_line = ""
            info_dict.append(current_dict)
            current_dict = {}

    generate_cypher_data(cypher_doc, info_dict)


# TODO begin generating cypher queries and dropping them into an aptly named file
# TODO once table_data is done reading, grab data for the next link and keep the ball rolling
host_site = 'https://en.wikipedia.org'
current_page = '/wiki/Royal_Rumble_(1990)'
rs = session.get(host_site + current_page)
#rs = session.get("https://en.wikipedia.org/wiki/Royal_Rumble_(1988)")
# https://en.wikipedia.org/wiki/WWE_Greatest_Royal_Rumble -- works!
# https://en.wikipedia.org/wiki/Royal_Rumble_(2018)
#print(rs)
title = rs.html.find("#firstHeading")
#print(title[0].text)
sel = "table.wikitable.sortable"
#print(rs)

table_dataset = rs.html.find(sel)
#print(table_dataset[0])

for table in table_dataset:
    if len(table.find('th')) >= 6:
        #print(title[0].text)
        produce_data(title[0].text, table, len(table.find('th')))

# print(rs.html.find(sel))
# print(rs.html.absolute_links)
# print(tab)

# print(rs.text)
