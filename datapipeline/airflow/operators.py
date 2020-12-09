import logging
import tempfile
from abc import ABCMeta
from os.path import dirname, join, realpath

import pandas as pd
from airflow.models import BaseOperator, Variable

from datapipeline.handlers.csv import CSVReader
from datapipeline.lib.frame import combine_dict, merge, group_by


FORMAT = "%(filename)s at %(asctime)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

FIXTURES_DIR = join(dirname(realpath(__file__)), "fixtures")

XCOM_KEY = "returned_dataframe"


class WorkflowOperator(BaseOperator, metaclass=ABCMeta):
    """
    This operator manage dataframe serialization and deserialization from XCOM
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conf = None  # To be instantiated just before task execution

    def pre_execute(self, context):
        """
        Get configuration for airflow variable
        """
        self.conf = Variable.get("dag_conf", deserialize_json=True)

    def serialize_and_push(self, task_instance, df: pd.Dataframe):
        """
        Serialize and compress the dataframe before pushing it to the next task using XCOM
        The compress format and method are fetched from the config(Airflow variable)
        We can use any format HDF, pickle, msgpack.... and it will be done automatically
        This format will be used to call the method "to_{format}" of the dataframe
        For example to_pickle, to_hdf...
        """
        method = self.conf.get("serialization_method", "hdf")
        compression = self.conf.get("serialization_compression", "infer")
        func = getattr(df, f"to_{method}")
        with tempfile.NamedTemporaryFile() as ntf:
            task_instance.xcom_push(key=XCOM_KEY, value=func(ntf.name, compression))

    def pull_and_deserialize(self, task_instance) -> pd.DataFrame:
        """
        Deserialize and decompress the dataframe fetched from XCOM
        We use the same principle as the serialize_and_push method but in this case we will call pd.read_{method}
        """
        content = task_instance.xcom_pull(key=XCOM_KEY, task_ids=self.upstream_task_ids)
        method = self.conf.get("serialization_method", "hdf")
        compression = self.conf.get("serialization_compression", "infer")
        func = getattr(pd, f"read_{method}")
        return func(content, compression)


class DrugsOperator(WorkflowOperator):
    """
    Create the drugs dataframe from the csv file and push it to the next operator
    """

    def __init__(self, *args, filename: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def execute(self, context):
        self.serialize_and_push(
            task_instance=context["ti"], df=CSVReader.read(self.filename)
        )


class PubMedTrialsOperator(WorkflowOperator):
    """
    Deserialize dataframe pushed by the DrugsOperator task, merge it with the trial/pubmed dataframe
    and push the result dataframe to the GraphOperator task
    """

    def __init__(self, *args, filename: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def execute(self, context):
        task_instance = context["ti"]
        upstream_df = self.pull_and_deserialize(task_instance)
        df = CSVReader.read(self.filename, names=["title", "date", "journal"], header=0)
        merged_df = upstream_df.pipe(
            merge, other=df, check_func=lambda s: s.drug.lower() in s.title.lower()
        ).pipe(group_by, by=["drug", "journal"], grouped_cols=["title", "date"])
        self.serialize_and_push(task_instance, df=merged_df)


class GraphOperator(WorkflowOperator):
    """
    Generate the graph link
    """

    def execute(self, context):
        task_instance = context["ti"]
        upstream_df_1, upstream_df_2 = self.pull_and_deserialize(task_instance)
        link_graph = {}
        for drug, group in upstream_df_1.combine(
            upstream_df_2, func=combine_dict
        ).groupby(level=0):
            link_graph.update({drug: group.xs(drug).to_dict()})
        logging.info("The graph link is: %s", link_graph)

        return link_graph
