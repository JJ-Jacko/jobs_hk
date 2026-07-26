from unittest import TestCase


from jobs_hk import context
from jobs_hk.db import DB
from jobs_hk.exceptions import DatabaseReadOnlyError

class TestDatabase(TestCase):    
    def test_readonly_mode_work(self):
        db = DB(context.DATA_BASE_FILE, read_only=True)

        with self.assertRaises(DatabaseReadOnlyError):
            db.save_company("TEST Company", "TEST")
