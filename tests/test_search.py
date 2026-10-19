import os
import tempfile
import unittest

from vellum.models import Store
from vellum.search import search


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.store = Store(os.path.join(self.tmp, "store.json"))
        self.store.add("如何学 Python", "从变量到函数的入门路径", ["编程", "python"])
        self.store.add("BM25 原理", "一种经典的全文检索排序算法", ["检索", "算法"])
        self.store.add("Java 后端面试", "常见八股与项目经验", ["java", "面试"])

    def test_chinese_query(self):
        res = search(self.store, "检索", top_k=5)
        self.assertTrue(any("BM25" in r["title"] for r in res))

    def test_english_query(self):
        res = search(self.store, "python", top_k=5)
        self.assertTrue(any("Python" in r["title"] for r in res))

    def test_no_result(self):
        self.assertEqual(search(self.store, "量子计算"), [])

    def test_snippet_present(self):
        res = search(self.store, "八股")
        self.assertTrue(res and "snippet" in res[0])


if __name__ == "__main__":
    unittest.main()
