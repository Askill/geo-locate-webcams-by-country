import json
import os
import requests
from lxml import html
import re 
import plotly.express as px
import pandas as pd

def main(url,pages, header_values=None):
    lLinks = []
    for i in pages:
        #time.sleep(random.random()*3)
        try:
            site = requests.get(url+str(i), headers=header_values)
            tree = html.fromstring(site.content)
            links = tree.xpath('//img/@src')
            print(i, links)
            [lLinks.append(ip_from_url(x)) for x in links]
        except:
            print("error with ", url + str(i))
    return lLinks

def ip_from_url(link):
    regex = "((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
    x = re.search(regex, link)
    if x is not None:
        return x.group(), link
    else:
        return None

def save_to_json(save_to, links):
    with open(save_to, 'w') as f:
        f.write(json.dumps(links, indent=4))

def load_content(location):
    with open(location) as json_file:
        return json.load(json_file)
 

def get_locations(cached_at, header_values=None):
    location = "http://ip-api.com/json/"
    ips = load_content(cached_at)
    locs = []
    for ip, stream in ips:
        x = requests.get(location+ip, headers=header_values).content.decode("UTF-8")
        if x != str(""):
            locs.append(json.loads(x))
    return locs

def create_dir_if_not_exists(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

if __name__ == "__main__":

    country = "UA"
    create_dir_if_not_exists(f"./cache/{country}")

    url = f"http://www.insecam.org/en/bycountry/{country}/?page="
    ips_file = f"./{country}/ips.json"

    links = list(set(main(url,range(1,20), header_values={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})))
    links = [l for l in links if l is not None]
    print(links)
    save_to_json(ips_file, links)

    locs = get_locations(ips_file)

    locs_file = f"./{country}/locs.json"
    save_to_json(locs_file, locs)
    locs = load_content(locs_file)


    df = pd.DataFrame.from_dict({"id": [x["query"] for x in locs], "lat": [x["lat"] for x in locs], "lon": [x["lon"] for x in locs]})
    fig = px.scatter_geo(df,lat='lat',lon='lon', hover_name="id", scope="europe", center={"lat": 50.7385,"lon": 25.3198})
    fig.update_layout(title = 'World map', title_x=0.5)
    fig.show()