from bs4 import BeautifulSoup
import re
"""This script uses BeautifulSoup to parse and collect table data from a given html_doc pattern.
Once this is done, it applies some transformations based on the data and spits it out to a 
cleaner version of a Cypher create script for Neo4j hydration"""

#consider list of html_docs
html_doc_1988 = open("rr_data/rr_1990.html", "r")
cypher_data_1988 = open("cypher_setup_data/cypher_setup_1990.txt", "w")

soup = BeautifulSoup(html_doc_1988, 'html.parser')

tables = soup.find_all('table')

event = 'RR1990'
cyper_create_queries = []
cyper_participate_queries = []
cyper_elimination_queries = []
cyper_win_query = []

#print("-- Draw -- | -- Entrant -- | -- Order -- | -- Eliminated By -- | -- Time -- |")

trs = soup.find_all('tr')
count = 0
same_elims = 0
w_eliminated_by = ""
rowspan_true = False

for tr in trs:

    if count != 0:

        table_data = tr.find_all('td')
        w_draw = table_data[0].contents[0].strip() #if table_data[0].span is not None else table_data[0].contents[0].strip()
        w_name = table_data[1].a.contents[0].strip()
        w_order = table_data[2].span.contents[0] if table_data[2].span is not None else table_data[2].contents[0]
        if int(same_elims) > 0:
            rowspan_true = False
            #print("Greater than zero")
            int_same_elims = int(same_elims)
            int_same_elims -= 1
            same_elims = str(int_same_elims)
            #w_time_in = table_data[3].contents[0].strip()
        else:
            same_elims = table_data[3].get('rowspan') if table_data[3].get('rowspan') is not None else "0"
            if int(same_elims) > 0:
                rowspan_true = True
                w_eliminated_by = table_data[3].contents[0].strip()
                w_time_in = table_data[4].contents[0].strip()

        if int(same_elims) <= 0:
            if w_order != '-':
                w_eliminated_by = table_data[3].contents[0].strip()
            else:
                w_eliminated_by = 'WINNER'

        w_time_in = table_data[4].contents[0].strip() if rowspan_true else table_data[4].contents[0].strip()

        if w_order != '-':
            w_order = w_order.strip()
        else:
            w_order = "-"
            w_eliminated_by = "Winner"

        #print(f"-- {w_draw} -- | -- {w_name}"
        #      + f" -- | -- {w_order} -- | -- {w_eliminated_by} -- | -- {w_time_in} -- |")
        alias = w_name.replace(" ", "")
        alias = re.sub("\W*","", alias)
        elim_alias = w_eliminated_by.replace(" ", "")
        cyper_create_queries.append("MERGE ("+alias+":Wrestler {name:'" + w_name + "'})")
        cypher_data_1988.write("MERGE ("+alias+":Wrestler {name:'" + w_name + "'})\n")
        cyper_participate_queries.append("CREATE (" + alias + ")-[:WAS_IN{draw:"+w_draw+"}]->("+event+")")
        elim_query = "CREATE (" + alias + ")-[:ELIMINATED_BY {order:" + str(w_order) + ", time:\"" + str(w_time_in) + "\"}]->(" + elim_alias + ")"
        #print(elim_query)
        cyper_elimination_queries.append(elim_query)
        #print("CREATE (w:Wrestler {name:" + w_name + "})")
    count += 1

#create cypher script here and move on
cypher_data_1988.close()
print(f"//{event}")
print("//creates")
for q in cyper_create_queries:
    print(q)
print("//participants")
for q in cyper_participate_queries:
    print(q)
print("//eliminations")
for q in cyper_elimination_queries:
    print(q)
