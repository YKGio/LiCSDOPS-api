from invoke.tasks import task
import os

@task
def spec(c):
    c.run(f"python api/spec/unit/music_spec.py")

@task
def rundev(c):
    c.run("python manage.py runserver")

@task
def startremote(c):
    c.run("python manage.py runserver 0.0.0.0:8080")

