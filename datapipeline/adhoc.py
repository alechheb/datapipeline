"""
This module is used to calculate the most common paper that mentions the most different drugs
"""
import logging
from os.path import dirname, join, realpath

FORMAT = "%(asctime)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


def get_max_paper(link_graph: dict):
    """
    Get the most common paper that mentions the most different drugs
    :param link_graph: Dictionary containing drugs in the first level and papers on the second level
    :return: most common paper name
    """
    papers = []
    for k, v in link_graph.items():
        papers.extend(v.keys())
    return max(papers, key=papers.count)


if __name__ == "__main__":
    import json

    FIXTURES_DIR = join(dirname(realpath(__file__)), "fixtures")

    with open(join(FIXTURES_DIR, "graph_link.json")) as lg_f:
        common_paper = get_max_paper(json.load(lg_f))

    logging.info(
        "The most common paper that mentions the most different drugs is: %s",
        common_paper,
    )
