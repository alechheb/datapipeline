"""
This module is used to launch the program (Test the link graph generation)
"""

import logging
from os.path import dirname, join, realpath

from datapipeline.handlers.csv import CSVReader
from datapipeline.lib.frame import merge, combine_dict, group_by

FORMAT = "%(filename)s at %(asctime)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

logger = logging.getLogger(__name__)

FIXTURES_DIR = join(dirname(realpath(__file__)), "fixtures")


def _read(filename, **kwargs):
    """Read CSV file"""
    drugs_filepath = join(FIXTURES_DIR, filename)
    return CSVReader.read(drugs_filepath, **kwargs).df


def _merge(drugs_df, other):
    """Return chained operations"""
    return drugs_df.pipe(
        merge, other=other, check_func=lambda s: s.drug.lower() in s.title.lower()
    ).pipe(group_by, by=["drug", "journal"], grouped_cols=["title", "date"])


def calculate():
    """Calculate the link graph"""
    # Read drugs file
    drugs_df = _read("drugs.csv", encoding="utf-8")

    # Read and merge clinical trials file
    trials_df = _read(
        "clinical_trials.csv",
        encoding="utf-8",
        names=["title", "date", "journal"],
        header=0,
    )
    merged_trial_df = _merge(drugs_df, trials_df)

    # Read and merge pubmed file
    pubmed_df = _read(
        "pubmed.csv", encoding="utf-8", names=["title", "date", "journal"], header=0
    )
    merged_pubmed_df = _merge(drugs_df, pubmed_df)

    # Generate link graph
    link_graph = {}
    for drug, group in merged_trial_df.combine(
        merged_pubmed_df, func=combine_dict
    ).groupby(level=0):
        link_graph.update({drug: group.xs(drug).to_dict()})
    logger.info("%d drugs mentioned in papers", len(link_graph))

    return link_graph


if __name__ == "__main__":
    from datapipeline.handlers.json import write

    output_file = join(FIXTURES_DIR, "graph_link.json")
    write(output_file, calculate())
