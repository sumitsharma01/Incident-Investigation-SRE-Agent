from contextlib import contextmanager
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from app.workspace.tenancy import current


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path=None):
        self.path = Path(path or os.getenv('SRE_WORKSPACE_DB', 'data/workspace.sqlite3'))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY, kind TEXT NOT NULL, incident_id TEXT NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL)')
            columns = {row['name'] for row in db.execute('PRAGMA table_info(records)')}
            if 'tenant' not in columns:
                db.execute("ALTER TABLE records ADD COLUMN tenant TEXT NOT NULL DEFAULT 'local'")
            db.execute('CREATE INDEX IF NOT EXISTS records_parent ON records(incident_id, kind, created_at)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def create(self, kind, payload, incident_id=None):
        identifier = str(uuid4())
        record = dict(payload, id=identifier, created_at=now(), tenant=current.get())
        with self.connect() as db:
            db.execute('INSERT INTO records (id,kind,incident_id,created_at,payload,tenant) VALUES (?, ?, ?, ?, ?, ?)',
                       (identifier, kind, incident_id or identifier, record['created_at'], json.dumps(record, allow_nan=False), current.get()))
        return record

    def get(self, identifier, kind):
        with self.connect() as db:
            row = db.execute('SELECT payload FROM records WHERE id=? AND kind=? AND tenant=?', (identifier, kind, current.get())).fetchone()
        if not row:
            raise KeyError(identifier)
        return json.loads(row['payload'])

    def list(self, kind, incident_id=None):
        with self.connect() as db:
            if incident_id:
                rows = db.execute('SELECT payload FROM records WHERE kind=? AND incident_id=? AND tenant=? ORDER BY created_at DESC LIMIT 200', (kind, incident_id, current.get())).fetchall()
            else:
                rows = db.execute('SELECT payload FROM records WHERE kind=? AND tenant=? ORDER BY created_at DESC LIMIT 200', (kind, current.get())).fetchall()
        return [json.loads(row['payload']) for row in rows]

    def update(self, identifier, payload):
        with self.connect() as db:
            db.execute('UPDATE records SET payload=? WHERE id=? AND tenant=?', (json.dumps(payload, allow_nan=False), identifier, current.get()))

    def interrupt_running(self):
        # Called only at single-process startup, never when creating a Store for a request.
        with self.connect() as db:
            records = [json.loads(row['payload']) for row in db.execute(
                "SELECT payload FROM records WHERE kind='incident' AND json_extract(payload, '$.state')='running'")]
        for record in records:
            if record['state'] == 'running':
                record.update(state='interrupted', finished_at=now(), error='Process stopped before completion; start a new investigation.')
                with self.connect() as db:
                    db.execute('UPDATE records SET payload=? WHERE id=?', (json.dumps(record),record['id']))
