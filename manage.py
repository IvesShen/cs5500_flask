#encoding: utf-8

from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from msd5500_project import app
from exts import db
from models import User, Pet

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()