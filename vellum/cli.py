"""命令行入口：add / list / search / delete / serve。"""

import argparse
import os
from typing import List, Optional

from .models import Store
from .search import search as do_search


def _default_path() -> str:
    return os.environ.get("VELLUM_PATH") or os.path.join(
        os.path.expanduser("~"), ".vellum", "store.json"
    )


def _store() -> Store:
    return Store(_default_path())


def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(
        prog="vellum", description="本地优先的 Markdown 知识库与 BM25 检索"
    )
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("add", help="新增笔记")
    a.add_argument("title")
    a.add_argument("-c", "--content", default="")
    a.add_argument("-t", "--tags", nargs="*", default=[])

    sub.add_parser("list", help="列出全部笔记")

    s = sub.add_parser("search", help="全文检索")
    s.add_argument("query")
    s.add_argument("-k", "--top", type=int, default=10)

    d = sub.add_parser("delete", help="删除笔记")
    d.add_argument("id")

    sv = sub.add_parser("serve", help="启动 Web UI")
    sv.add_argument("--host", default="127.0.0.1")
    sv.add_argument("--port", type=int, default=8000)

    args = p.parse_args(argv)
    store = _store()

    if args.cmd == "add":
        n = store.add(args.title, args.content, args.tags)
        print(f"已添加笔记 {n.id[:8]}：{n.title}")
    elif args.cmd == "list":
        if not store.all():
            print("（暂无笔记）")
        for n in store.all():
            print(f"{n.id[:8]}  {n.title}  #{','.join(n.tags)}")
    elif args.cmd == "search":
        for r in do_search(store, args.query, args.top):
            print(f"{r['score']:.3f}  {r['title']}  — {r['snippet'][:60]}")
    elif args.cmd == "delete":
        print("已删除" if store.delete(args.id) else "未找到该笔记")
    elif args.cmd == "serve":
        from .server import serve

        serve(store, args.host, args.port)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
