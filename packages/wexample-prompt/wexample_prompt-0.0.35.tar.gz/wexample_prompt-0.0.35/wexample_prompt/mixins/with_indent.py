class WithIndent:
    log_indent: int = 0
    _indent_string: str = "  "

    def log_indent_up(self) -> None:
        self.log_indent += 1

    def log_indent_down(self) -> None:
        self.log_indent -= 1

    def build_indent(self, increment: int = 0) -> str:
        return str(self._indent_string * (self.log_indent + increment))
