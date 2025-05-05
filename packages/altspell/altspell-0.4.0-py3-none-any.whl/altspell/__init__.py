'''
    Altspell  Flask web app for translating traditional English to respelled
    English and vice versa
    Copyright (C) 2024-2025  Nicholas Johnson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import importlib
import pkgutil
import os
from importlib.metadata import version
from flask import Flask
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from altspell_plugins import PluginBase
from .model import Base


AVAILABLE_PLUGINS = {
    name.removeprefix('altspell_'): importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('altspell_') and name != 'altspell_plugins' # ignore plugins interface
}

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the app instance path
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'altspell.db'),
        # maximum number of characters accepted for translation
        TRANSLATION_LENGTH_LIMIT = 20000,
        # enable all plugins by default
        ENABLED_PLUGINS = AVAILABLE_PLUGINS.keys(),
        # disable CAPTCHA for test purposes
        ENABLE_HCAPTCHA = False
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    with app.app_context():
        from .containers import Container  # pylint: disable=import-outside-toplevel

        # create container for dependency injection
        container = Container()

    app.container = container

    # configure the database
    db = container.db(model_class=Base)
    db.init_app(app)

    # create the cache
    cache = container.cache()
    cache.init_app(app)

    # create the migration
    migrate = container.migrate()
    migrate.init_app(app, db)

    # allow CORS for all domains on all routes
    CORS(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # create the database
    with app.app_context():
        db.create_all()

    app.plugin_instances = {}

    for plugin in app.config['ENABLED_PLUGINS']:
        if plugin in AVAILABLE_PLUGINS:
            plugin_mod = AVAILABLE_PLUGINS[plugin]

            # validate plugin implementation
            if not hasattr(plugin_mod, 'Plugin'):
                app.logger.error(
                    'Enabled plugin excluded for missing "Plugin" attribute: %s', plugin
                )
                continue

            if not issubclass(plugin_mod.Plugin, PluginBase):
                app.logger.error(
                    'Enabled plugin excluded for not being a subclass of PluginBase: %s', plugin
                )
                continue

            # initialize plugin
            app.logger.info('Initializing plugin: %s...', plugin)
            plugin_instance = plugin_mod.Plugin()
            plugin_instance.version = version(plugin_mod.__name__)
            app.plugin_instances[plugin_instance.name] = plugin_instance

            with app.app_context():
                from .utils.populate_spelling_system_table import populate_spelling_system_table  # pylint: disable=import-outside-toplevel
                populate_spelling_system_table(plugin_instance)
        else:
            app.logger.warning('Enabled plugin is not available: %s', plugin)

    # apply the blueprints to the app
    from .blueprints import translation  # pylint: disable=import-outside-toplevel
    app.register_blueprint(translation.bp)

    from .blueprints import spelling_system  # pylint: disable=import-outside-toplevel
    app.register_blueprint(spelling_system.bp)

    return app
