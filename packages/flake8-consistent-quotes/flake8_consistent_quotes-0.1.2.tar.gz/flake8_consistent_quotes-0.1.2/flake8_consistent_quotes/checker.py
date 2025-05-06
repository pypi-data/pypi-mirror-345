import ast
import tokenize
from collections import Counter

LineNumber = int
ColumnNumber = int


class Flake8ConsistentQuotesChecker:
    name = "flake8-consistent-quotes"
    version = "0.1.2"

    def __init__(self, tree: ast.AST, filename: str | None = None):
        self.tree = tree
        self.filename = filename
        self.errors: list[tuple[LineNumber, ColumnNumber, str]] = []

    def run(self):  # type: ignore[no-untyped-def]
        if not self.filename:
            return

        try:
            with open(self.filename, "rb") as f:
                tokens = list(tokenize.tokenize(f.readline))
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError, TypeError):
            return

        # Собираем docstrings по позициям
        docstring_positions: set[tuple[LineNumber, ColumnNumber]] = (
            self._collect_docstring_positions()
        )

        quote_counts: Counter[str] = Counter()
        string_tokens: list[tokenize.TokenInfo] = []

        for tok in tokens:
            if tok.type == tokenize.STRING:
                if (tok.start[0], tok.start[1]) in docstring_positions:
                    continue  # Пропускаем docstring
                string_tokens.append(tok)
                if tok.string.startswith(
                    ("'", "r'", "u'", "b'", "f'", "R'", "U'", "B'", "F'")
                ):
                    quote_counts["'"] += 1
                elif tok.string.startswith(
                    ('"', 'r"', 'u"', 'b"', 'f"', 'R"', 'U"', 'B"', 'F"')
                ):
                    quote_counts['"'] += 1

        if not quote_counts:
            return

        # Определяем наиболее частую кавычку
        preferred = quote_counts.most_common(1)[0][0]
        not_preferred = "'" if preferred == '"' else '"'

        for tok in string_tokens:
            if preferred in tok.string:
                continue

            if tok.string.startswith(not_preferred):
                line, col = tok.start
                self.errors.append(
                    (
                        line,
                        col,
                        f"FCQ001 inconsistent quote style: expected {preferred}",
                    )
                )

        for e in self.errors:
            yield (*e, type(self))

    def _collect_docstring_positions(self) -> set[tuple[LineNumber, ColumnNumber]]:
        """
        Возвращает множество позиций docstring'ов в виде (line, column)
        """
        doc_pos = set()

        prev_node = None
        for node in ast.walk(self.tree):
            expr = None

            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
            ):
                if not (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                ):
                    continue

                if ast.get_docstring(node, clean=False) is None:
                    continue
                expr = node.body[0]
            elif isinstance(node, ast.Expr) and isinstance(prev_node, ast.Assign):
                expr = node

            if expr:
                doc_pos.add((expr.lineno, expr.col_offset))

            prev_node = node

        return doc_pos
