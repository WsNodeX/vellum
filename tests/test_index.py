import unittest

from vellum.index import BM25, tokenize


class TestTokenize(unittest.TestCase):
    def test_english(self):
        self.assertEqual(tokenize("Hello World!"), ["hello", "world"])

    def test_chinese_bigram(self):
        toks = tokenize("知识库检索")
        self.assertIn("知识", toks)
        self.assertIn("检索", toks)
        # 单字不再单独出现
        self.assertNotIn("知", toks)
        self.assertNotIn("库", toks)

    def test_mixed(self):
        toks = tokenize("BM25 检索 engine")
        self.assertIn("bm25", toks)
        self.assertIn("engine", toks)
        self.assertIn("检索", toks)
        self.assertNotIn("检", toks)


class TestBM25(unittest.TestCase):
    def test_ranking(self):
        idx = BM25()
        idx.add("1", "python 编程 入门 教程")
        idx.add("2", "python 数据分析 进阶")
        idx.add("3", "java 后端 开发")
        idx.build()
        hits = idx.search("python", top_k=3)
        ids = [h[0] for h in hits]
        self.assertIn("1", ids)
        self.assertIn("2", ids)
        self.assertNotIn("3", ids)

    def test_empty_query(self):
        idx = BM25()
        idx.add("1", "hello world")
        idx.build()
        self.assertEqual(idx.search(""), [])


if __name__ == "__main__":
    unittest.main()
