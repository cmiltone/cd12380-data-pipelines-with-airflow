from datetime import datetime, timedelta
import pendulum
import os
from airflow.decorators import dag
from airflow.operators.dummy import DummyOperator
from operators import (StageToRedshiftOperator, LoadFactOperator,
                       LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

default_args = {
    'owner': 'udacity',
    'start_date': pendulum.now(),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': pendulum.duration(seconds=300),
    'catchup': False,
    'email_on_failure': False
}

@dag(
    default_args=default_args,
    description='Load and transform data in Redshift with Airflow',
    schedule_interval='0 * * * *'
)
def final_project():

    start_operator = DummyOperator(task_id='Begin_execution')

    stage_events_to_redshift = StageToRedshiftOperator(
        task_id='Stage_events',
        sql = SqlQueries.copy_events_sql
    )

    stage_songs_to_redshift = StageToRedshiftOperator(
        task_id='Stage_songs',
        sql = SqlQueries.copy_songs_sql
    )

    load_songplays_table = LoadFactOperator(
        task_id='Load_songplays_fact_table',
    )

    load_user_dimension_table = LoadDimensionOperator(
        task_id='Load_user_dim_table',
        truncate_sql = SqlQueries.user_truncate_sql,
        insert_sql = SqlQueries.user_insert_sql,
        insert_mode = 'truncate_load'
    )

    load_song_dimension_table = LoadDimensionOperator(
        task_id='Load_song_dim_table',
        truncate_sql = SqlQueries.song_truncate_sql,
        insert_sql = SqlQueries.song_insert_sql,
        insert_mode = 'truncate_load'
    )

    load_artist_dimension_table = LoadDimensionOperator(
        task_id='Load_artist_dim_table',
        truncate_sql = SqlQueries.artist_truncate_sql,
        insert_sql = SqlQueries.artist_insert_sql,
        insert_mode = 'truncate_load'
    )

    load_time_dimension_table = LoadDimensionOperator(
        task_id='Load_time_dim_table',
        truncate_sql = SqlQueries.time_truncate_sql,
        insert_sql = SqlQueries.time_insert_sql,
        insert_mode = 'truncate_load'
    )

    run_quality_checks = DataQualityOperator(
        task_id='Run_data_quality_checks',
    )

final_project_dag = final_project()
