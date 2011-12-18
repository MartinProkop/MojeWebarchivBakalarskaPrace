import unittest2

from warctools import ArcRecord
from warctools import ArchiveRecord

class TestSequenceFunctions(unittest2.TestCase):

    def test_arc2warc(self):
        f = 'test_data/IAH-20110605172416-00000-kevin-laptop-9090.arc.gz'
        fh = ArcRecord.open_archive(f, gzip="auto")

        for record in fh:
            self.assertIsNotNone(record.url)
            self.assertIsNotNone(record.date)
            self.assertNotEqual(record.content,'')

    def test_warcvalid(self):
        f = 'test_data/warc.txt.gz'
        fh = ArchiveRecord.open_archive(f, gzip="auto")
        self.assertIsNotNone(fh)

        for (offset, record, errors) in fh.read_records(limit=None):
            self.assertFalse( errors )
            if record is not None:
                self.assertFalse( record.validate() )

suite = unittest2.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
unittest2.TextTestRunner(verbosity=2).run(suite)
