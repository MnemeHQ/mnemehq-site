"""Explicit preview-only migration job entry point; never runs on web startup."""
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from app.preview import require_preview_database, MIGRATOR_USER, PREVIEW_DATABASE


def main():
    try:
        url = require_preview_database(MIGRATOR_USER)
        config = Config('alembic.ini')
        if sys.argv[1:] == ['--sql']:
            command.upgrade(config, 'head', sql=True)
            return 0
        if sys.argv[1:]:
            raise ValueError('Unsupported migration argument')
        engine = create_engine(url.set(drivername='postgresql+psycopg2'))
        try:
            with engine.connect() as connection:
                if connection.execute(text('SELECT current_database()')).scalar_one() != PREVIEW_DATABASE:
                    raise RuntimeError('Unexpected database')
            command.upgrade(config, 'head')
            command.current(config)
        finally:
            engine.dispose()
        return 0
    except Exception:
        # Connection/parser errors can contain secrets. Do not emit traceback.
        print('Preview migration failed. Verify the isolated credential, grants and migration state.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
