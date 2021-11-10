from bs4 import BeautifulSoup
import requests
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import copy

URL3 = "https://arngren.net/"
all_links = set()
global_links = dict()
matrix = []
ans = []
d = 0


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
    l = []

    items = soup.find_all('a')

    for item in items:
        l.append(item.get("href"))

    return l


def find_link_base(url: str) -> (str, str):
    index = 0
    for i in range(len(url) - 2, 0, -1):
        if url[i] == "/":
            index = i
        elif url[i] == "." and index != 0:
            return url[:index], url[index:len(url)]
    return url, ""


def run_cycle(url_base: str, page: str):
    if url_base[-1] != "/":
        url_base = url_base + "/"
    if page != "" and page[0] == "/":
        page[0] = ""

    html = get_html(url_base + page)
    l = find_links(html)

    for i in range(0, len(l)):
        if len(l[i]) > 4:
            if l[i][:4] == "http" or l[i].find("@") != -1:
                l[i] = ""

    global_links[page] = l.copy()

    try:
        l.remove(page)
    except ValueError:
        pass
    return l


def calculate_pg():
    for page in global_links.keys():
        row = []
        for l in all_links:
            if l in global_links[page]:
                if len(global_links[l]) == 0:
                    row.append(0)
                else:
                    row.append(1 / len(global_links[l]))

        matrix.append(row)

    return jacob(matrix)


def jacob(_matrix):
    x = [1 for _ in range(len(_matrix))]
    prev_x = []
    while True:
        if prev_x != [] and min([x[i]-prev_x[i] for i in range(len(x))]) < 0.001:
            break
        prev_x = x.copy()
        for row in range(len(_matrix)):
            x[row] = 0

            for column in range(len(_matrix[row])):
                x[row] += prev_x[row] * _matrix[row][column]

            x[row] *= d
            x[row] += 1-d

        print(x)
    return x


if __name__ == '__main__':
    url = input("Input url (blank for {0}): ".format(URL3))
    if url == "":
        url = URL3

    d = float(input("Input d: "))

    base, default_page = find_link_base(url)

    links = run_cycle(base, default_page)
    all_links = all_links.union(links)  # for graph building
    flag = False

    unprocessed_links = all_links.copy()

    while True:
        if flag and len(unprocessed_links) == 0:
            break

        new_links = set()

        for link in unprocessed_links:
            links = run_cycle(base, link)
            new_links = new_links.union(set(links).difference(all_links))
            all_links = all_links.union(links)  # for graph building
            flag = True

        unprocessed_links = new_links.copy()

    a = calculate_pg()
    keys = list(global_links.keys())
    for i in range(len(a)):
        print("P({0}) = {1}".format(keys[i], a[i]))

    # graph
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
