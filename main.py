from bs4 import BeautifulSoup
import requests
import networkx as nx
import matplotlib.pyplot as plt

BASE_URL = "https://overthewire.org/wargames/"
URL2 = "https://www.miauk.com/"
URL3 = "https://arngren.net/"
all_links = set()
global_links = dict()


def get_html(url: str) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    try:
        resp = requests.get(url, headers=headers)
    except Exception:
        print("Failed connection to {}".format(url))
        return bytes()
    return resp.content


def find_links(html: bytes) -> [str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []

    items = soup.find_all('a')

    for item in items:
        links.append(item.get("href"))

    return links


def find_link_base(url: str) -> (str, str):
    index = 0
    for i in range(len(url) - 2, 0, -1):
        if url[i] == "/":
            index = i
        elif url[i] == "." and index != 0:
            return url[:index], url[index:len(url)]
    return url, ""


def run_cycle(base: str, page: str):
    if page != "" and page[0] != "/":
        page = "/" + page
    html = get_html(base + page)
    links = find_links(html)

    try:
        links.remove(page)
    except ValueError:
        pass

    for i in range(0, len(links)):
        if len(links[i]) > 4:
            if links[i][:4] == "http" or links[i].find("email-protection") != -1:
                links[i] = ""
    return links


if __name__ == '__main__':
    base, default_page = find_link_base(URL3)

    new_links = set()

    links = run_cycle(base, default_page)
    all_links = all_links.union(links)  # for graph building
    global_links[default_page] = links

    flag = False

    unprocessed_links = all_links.copy()

    while True:
        if flag and len(new_links) == 0:
            break

        for link in unprocessed_links:
            links = run_cycle(base, link)
            new_links = set(links).difference(all_links)
            all_links = all_links.union(links)  # for graph building
            global_links[link] = links
            flag = True

        unprocessed_links = new_links.copy()

    graph = nx.Graph()
    edges = []

    for key in global_links.keys():
        for link in global_links[key]:
            edges.append((key, link))

    graph.add_edges_from(edges)

    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos, cmap=plt.get_cmap('jet'))
    nx.draw_networkx_labels(graph, pos)
    nx.draw_networkx_edges(graph, pos, edgelist=edges, arrows=True)
    plt.show()
