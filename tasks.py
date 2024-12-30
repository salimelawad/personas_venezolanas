from invoke import task

@task
def run(c):
    c.run('uv run streamlit run app/main.py')