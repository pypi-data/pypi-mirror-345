import unittest
import os
import shutil
from file_dir_backup.core import backup, FULL_BACKUP, INCREMENTAL_BACKUP, RSYNC_METHOD, SHUTIL_METHOD


class TestFileDirBackup(unittest.TestCase):
    def setUp(self):
        self.source_dir = 'test_source'
        self.destination_dir = 'test_destination'
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.destination_dir, exist_ok=True)
        with open(os.path.join(self.source_dir, 'test_file.txt'), 'w') as f:
            f.write('test content')

    def tearDown(self):
        if os.path.exists(self.source_dir):
            shutil.rmtree(self.source_dir)
        if os.path.exists(self.destination_dir):
            shutil.rmtree(self.destination_dir)

    def test_full_backup_rsync(self):
        backup(self.source_dir, self.destination_dir, FULL_BACKUP, RSYNC_METHOD)
        self.assertTrue(os.path.exists(os.path.join(self.destination_dir, 'test_file.txt')))

    def test_full_backup_shutil(self):
        backup(self.source_dir, self.destination_dir, FULL_BACKUP, SHUTIL_METHOD)
        self.assertTrue(os.path.exists(os.path.join(self.destination_dir, 'test_file.txt')))

    def test_incremental_backup_rsync(self):
        backup(self.source_dir, self.destination_dir, INCREMENTAL_BACKUP, RSYNC_METHOD)
        self.assertTrue(os.path.exists(os.path.join(self.destination_dir, 'test_file.txt')))

    def test_incremental_backup_shutil(self):
        backup(self.source_dir, self.destination_dir, INCREMENTAL_BACKUP, SHUTIL_METHOD)
        self.assertTrue(os.path.exists(os.path.join(self.destination_dir, 'test_file.txt')))


if __name__ == '__main__':
    unittest.main()
