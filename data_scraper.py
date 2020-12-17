from requests_html import HTMLSession
import re
from unidecode import unidecode as ud
from datetime import datetime as dt

# Helper script to scrape in specific table data from rr pages

session = HTMLSession()
regex = "(,)*\s*(&|and)\s+"

def clean_time_string(time_string):
    time_regex = "[0-9]{0,2}:[0-9]{0,2}:[0-9]{0,2}|[0-9]{0,2}:[0-9]{0,2}"
    match = re.match(time_regex, time_string)
    #print(match)
    if match is not None:
        matched_time_str = match.group(0)
        time_convert_format = "%M:%S"
        if matched_time_str is None:
            print("WAS NA")
            return 0
        else:
            match_split = matched_time_str.split(":")
            #print(match_split)
            if len(match_split) > 2:
                time_convert_format = "%H:%M:%S"
            return dt.strptime(matched_time_str, time_convert_format) #<-- TODO use regex to clean the string and define tokens
    #time_string

def generate_cypher_data(file, info_dict, cur_year):

    cypher_create_wrestlers = []
    cypher_create_participants = []
    cypher_create_elims = []

    for inf in info_dict:
        #print(inf)

        time_val = clean_time_string(inf['time_in'])
        #time_val.second
        time_val_2 = time_val - dt(1900, 1, 1)
        #print(time_val_2.total_seconds())
        #print(time_val)
        normalized = ud(inf['wrestler'])
        alias = normalized.replace(" ", "")
        alias = re.sub("\W*", "", alias)
        cypher_create_wrestlers.append("MERGE (" + alias + ":Wrestler {name:'" + normalized + "'})\n")
        if 'brand' in inf:
            cypher_create_participants.append("CREATE (" + alias + ")-[:WAS_IN{draw:" + inf['draw'] + ", brand:" + inf['brand'] + "}]->(RR" + cur_year + ")\n")
        else:
            cypher_create_participants.append("CREATE (" + alias + ")-[:WAS_IN{draw:" + inf['draw'] + "}]->(RR" + cur_year + ")\n")
        #print("time in: " + inf['time_in'])
        if type(inf['eliminators']) is list:
            for elim in inf['eliminators']:
                cypher_create_elims.append("CREATE (" + alias + ")-[:ELIMINATED_BY {order:" + inf['order'] + ", time:\"" + str(time_val_2.total_seconds()) + "\"}]->(" + elim + ")\n")
        else:
            cypher_create_elims.append("CREATE (" + alias + ")-[:ELIMINATED_BY {order:" + inf['order'] + ", time:\"" + str(time_val_2.total_seconds()) + "\"}]->(" + inf['eliminators'] + ")\n")

    for ccw in cypher_create_wrestlers:
        file.write(ccw)
    file.write("//Participations\n")
    for ccp in cypher_create_participants:
        file.write(ccp)
    file.write("//Eliminations\n")
    for cce in cypher_create_elims:
        file.write(cce)
    file.close()

def produce_data(e_title, table_feed, header_count):
    # first we generate the event creation query
    # next, we generate the wrestlers
    # then we generate the participants in the event
    # then, we create the eliminations
    # finally, we add in the winner
    #regex to strip year out
    year_regex = '[^(](\d+)[^)]'
    current_year_search = re.search(year_regex, e_title)
    current_year = current_year_search.group(0)
    cypher_doc = open('cypher_setup_data/cypher_data_' + e_title + ".txt", 'w', encoding="utf-8")
    cypher_doc.write("//Event\n")
    cypher_doc.write("CREATE (RR" + current_year + ":Event { name:'" + e_title + "', year:" + current_year + "})\n")
    cypher_doc.write("//Wrestlers\n")

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

        # if count == 5 and header_count == 7:
        #     current_dict["time_in"] = td.text
        # elif count == 4 and header_count == 6:
        #     current_dict["time_in"] = td.text

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

        if (count == header_count - 3) and (":" in td.text):
            max_col_count = header_count - 1
            #print("time_in weird")
            entry_line += (multi_elim + " | " + td.text + " | ")
            current_dict['eliminators'] = multi_elim
            #print(current_dict['eliminators'])
            current_dict['time_in'] = td.text
            #print(current_dict['time_in'])
        elif (count == header_count - 2) and (":" in td.text or 'N/A' == td.text):
            current_dict["time_in"] = td.text
            entry_line += (td.text + " | ")
        else:
            entry_line += (td.text + " | ")
            # current_dict['time_in'] = td.text
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

    generate_cypher_data(cypher_doc, info_dict, current_year)


#TODO replace elimator's name with elim alias in cypher elim queries
#TODO convert time to seconds <-- this should be dynamically pulled out and converted for ease of time calculations at the DB level
host_site = 'https://en.wikipedia.org'
current_page = '/wiki/Royal_Rumble_(1988)'

has_next = True
while has_next:
    rs = session.get(host_site + current_page)
    next_sel = "table.infobox"
    link = rs.html.find(next_sel)
    href_links = link[0].find('a')

    next_sel = "table.infobox"
    link = rs.html.find(next_sel)
    href_links = link[0].find('a')
    for href in href_links:
        if re.match('[/]+wiki[/]+Royal_Rumble_[(]+(\d+)[)]+', href.attrs.get('href')):
            has_next = True
            current_page = href.attrs.get('href')
        else:
            has_next = False


    title = rs.html.find("#firstHeading")
    sel = "table.wikitable.sortable"
    table_dataset = rs.html.find(sel)

    for table in table_dataset:
        if len(table.find('th')) >= 6:
            produce_data(title[0].text, table, len(table.find('th')))
