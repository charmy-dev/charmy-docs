"""从包源码自动生成 Sphinx API 文档 (.rst)。

用法（在仓库根目录运行）:
    python source/api/gen_api.py            # 只补缺失文件
    python source/api/gen_api.py --force    # 全量覆盖重写
    python source/api/gen_api.py --dry-run  # 只打印计划，不落盘

模板与 source/api 下现有文件一致：
    模块页  = 标题 + autoclasstree(:full: :strict:) + automodule(:members:)
    包 index = 同上 + toctree 列出子模块/子包
"""
import argparse
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP = {"__main__", "_compat", "skhynix", "text"}   # 非 API / 空壳文件
RENAME = {"cm_object": "object"}                     # charmy.cm_object -> object.rst


def _width(s):
    """RST 标题下划线按显示宽度算（CJK 占 2 格）。"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def render(title, dotted, children=()):
    full = [] if dotted.endswith(".backend") else ["   :full:"]  # backend 循环引用会让 mermaid 崩
    lines = [title, "=" * _width(title), "", f".. autoclasstree:: {dotted}",
             *full, "   :strict:", "", f".. automodule:: {dotted}",
             "   :members:", ""]
    if children:  # 包：追加 toctree
        lines += [".. toctree::", "   :maxdepth: 2", ""]
        lines += [f"   {c}" for c in sorted(children)] + [""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(HERE.parents[2] / "charmy"), help="包源码目录")
    ap.add_argument("--pkg", default="charmy", help="包名")
    ap.add_argument("--out", default=str(HERE), help="rst 输出根目录")
    ap.add_argument("--force", action="store_true", help="覆盖已有文件")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    src, out = Path(a.src).resolve(), Path(a.out).resolve()
    if not (src / "__init__.py").is_file():   # 传的是仓库根时自动下钻到包目录
        src = src / a.pkg

    leaves, pkgs = [], {}  # leaves: (dotted, parts, rst_name)
    for f in sorted(src.rglob("*.py")):
        parts = f.relative_to(src).with_suffix("").parts
        if any(p.startswith((".", "__pycache__")) for p in parts) or parts[-1] in SKIP:
            continue
        dotted = ".".join((a.pkg,) + parts)
        if parts[-1] == "__init__":
            pkgs.setdefault(".".join((a.pkg,) + parts[:-1]), [])
        else:
            name = RENAME.get(parts[-1], parts[-1])
            leaves.append((dotted, parts, name))
            pkgs.setdefault(".".join((a.pkg,) + parts[:-1]), []).append(name)

    jobs = []  # (rst_path, content, 是否派生页)
    for dotted, parts, name in leaves:
        jobs.append((out.joinpath(*parts[:-1], f"{name}.rst"),
                     render(name, dotted), False))
    for pkg, kids in pkgs.items():
        if not kids:
            continue
        subs = [p.split(".")[-1] for p in pkgs
                if p.rsplit(".", 1)[0] == pkg]
        title = "API 参考" if pkg == a.pkg else pkg
        jobs.append((out.joinpath(*pkg.split(".")[1:], "index.rst"),
                     render(title, pkg, kids + [f"{s}/index" for s in subs]),
                     True))  # index 由目录结构派生，内容变了就刷新

    for path, content, derived in jobs:
        rel = path.relative_to(out)
        same = path.exists() and path.read_text(encoding="utf-8") == content
        if same or (path.exists() and not (a.force or derived)):
            print(f"skip  {rel}")
            continue
        print(f"write {rel}")
        if not a.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(f"\n{len(jobs)} page(s) planned -> {out}")


if __name__ == "__main__":
    main()
