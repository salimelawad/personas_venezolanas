from app.database import init_db as xyz
from invoke import task

@task
def init_db(c):
    xyz()

@task
def run(c):
    c.run('uv run streamlit run app/main.py')