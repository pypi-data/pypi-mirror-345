from kvlang.common import ROOT


def load_grammar() -> str:
    with open(ROOT / "kv.lark", encoding="utf-8") as kv:
        return kv.read()
