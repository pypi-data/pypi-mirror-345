from lark import Transformer, Lark, Tree
from lark.indenter import Indenter

from kvlang.grammar import load_grammar
from kvlang.transformer import KvTransformer


class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

    def handle_NL(self, token):
        if '\n' not in token:
            return
        yield from super().handle_NL(token)


def create_parser(transformer: type[Transformer] = KvTransformer) -> Lark:
    return Lark(
        load_grammar(), parser="lalr",
        postlex=TreeIndenter(), transformer=transformer()
    )


def parse(text: str) -> Tree:
    parser = create_parser()
    return parser.parse(text)
