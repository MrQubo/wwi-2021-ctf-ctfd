import datetime
import shutil

from flask_migrate import MigrateCommand
from flask_script import Manager

from CTFd import create_app
from CTFd.utils import get_config as get_config_util
from CTFd.utils import set_config as set_config_util
from CTFd.utils.config import ctf_name
from CTFd.utils.exports import export_ctf as export_ctf_util
from CTFd.utils.exports import import_ctf as import_ctf_util

app = create_app()

manager = Manager(app)
manager.add_command("db", MigrateCommand)


def jsenums():
    from CTFd.constants import JS_ENUMS
    import json
    import os

    path = os.path.join(app.root_path, "themes/core/assets/js/constants.js")

    with open(path, "w+") as f:
        for k, v in JS_ENUMS.items():
            f.write("const {} = Object.freeze({});".format(k, json.dumps(v)))


BUILD_COMMANDS = {"jsenums": jsenums}


@manager.command
def get_config(key):
    with app.app_context():
        print(get_config_util(key))


@manager.command
def set_config(key, value):
    with app.app_context():
        print(set_config_util(key, value).value)


@manager.command
def build(cmd):
    with app.app_context():
        cmd = BUILD_COMMANDS.get(cmd)
        cmd()


@manager.command
def export_ctf(path=None):
    with app.app_context():
        backup = export_ctf_util()

        if path:
            with open(path, "wb") as target:
                shutil.copyfileobj(backup, target)
        else:
            name = ctf_name()
            day = datetime.datetime.now().strftime("%Y-%m-%d_%T")
            full_name = f"{name}.{day}.zip"

            with open(full_name, "wb") as target:
                shutil.copyfileobj(backup, target)

            print(f"Exported {full_name}")


@manager.command
def import_ctf(path):
    with app.app_context():
        import_ctf_util(path)


# TODO: Add commands to add and remove challenges.
#  @manager.command
#  def push_task(path):
#      from CTFd.models import Challenges, db
#
#      path = Path(path)
#      config = read_yml(path / 'task.yml')
#
#      data = {
#          'name': config['title'],
#          'description': config['desc'],
#      }
#
#      with app.app_context():
#          challenge = Challenges.query.filter_by(task_id=path.name).one()
#          if challenge:
#              for k, v in data.items():
#                  setattr(challenge, k, v)
#          else:
#              challenge = Challenges(**data)
#              db.session.add(challenge)
#          db.session.commit()


if __name__ == "__main__":
    manager.run()
