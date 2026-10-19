import os
import tempfile
import unittest

from vellum.models import Store, Note


class TestStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "store.json")
        self.store = Store(self.path)

    def test_add_and_get(self):
        n = self.store.add("标题A", "内容A", ["x", "y"])
        self.assertEqual(self.store.count(), 1)
        self.assertIsNotNone(self.store.get(n.id))
        self.assertEqual(self.store.get(n.id).title, "标题A")

    def test_persistence(self):
        n = self.store.add("标题B", "内容B")
        reopen = Store(self.path)
        self.assertEqual(reopen.count(), 1)
        self.assertEqual(reopen.get(n.id).title, "标题B")

    def test_update(self):
        n = self.store.add("旧", "旧内容")
        self.store.update(n.id, title="新", content="新内容")
        self.assertEqual(self.store.get(n.id).title, "新")

    def test_delete(self):
        n = self.store.add("待删", "x")
        self.assertTrue(self.store.delete(n.id))
        self.assertIsNone(self.store.get(n.id))
        self.assertFalse(self.store.delete(n.id))


if __name__ == "__main__":
    unittest.main()
