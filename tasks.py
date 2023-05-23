from invoke.tasks import task
import os

@task
def spec(c):
    c.run(f"python api/spec/unit/music_spec.py")

@task
def testserver(c):
    c.run("python manage.py runserver")

