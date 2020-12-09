"""
This dag parse drugs, trials, and publication csv files and generate the publication link graph
"""
from airflow import DAG, configuration
from airflow.models import Variable

from datapipeline.airflow.operators import (
    DrugsOperator,
    PubMedTrialsOperator,
    GraphOperator,
)


with DAG(
    dag_id="link_graph",
    description="Generate publication link graph",
    # .....
    default_args={
        "email": "collaborators@toto.titi",
    },
    tags=["DRUGS", "TRIALS", "PUBMED"],
) as dag:
    dag.doc_md = __doc__

    # If we want to use a specific queue we can fetch it from airflow Variables
    queue = Variable.get(f"{dag.dag_id.upper()}_QUEUE", configuration.conf.get("celery", "default_queue"))

    feed_drugs_operator = DrugsOperator(task_id="feed_drugs", queue=queue, filename="drugs.csv")
    # TrialsOperator and PubmedOperator can use the same operator
    feed_trials_operator = PubMedTrialsOperator(task_id="feed_trials", queue=queue, filename="clinical_trials.csv")
    feed_pubmed_operator = PubMedTrialsOperator(task_id="feed_pubmed", queue=queue, filename="pubmed.csv")
    generate_graph_operator = GraphOperator(task_id="generate_graph", queue=queue)

    dag >> feed_drugs_operator >> [feed_trials_operator, feed_pubmed_operator] >> generate_graph_operator
