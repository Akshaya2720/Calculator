from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
import ast, operator as op, math

_ALLOWED_BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
    ast.Pow: op.pow,
}
_ALLOWED_UNARY_OPS = {ast.UAdd: op.pos, ast.USub: op.neg}
_ENV = {
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'log': math.log,
    'exp': math.exp,
    'abs': abs,
    'pi': math.pi,
    'e': math.e,
}

def _safe_eval(node: ast.AST, names: dict) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, names)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in names:
            return names[node.id]
        raise ValueError(f"Unknown name: {node.id}")
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPS:
        return _ALLOWED_UNARY_OPS[type(node.op)](_safe_eval(node.operand, names))
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN_OPS:
        left = _safe_eval(node.left, names)
        right = _safe_eval(node.right, names)
        return _ALLOWED_BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fn = node.func.id
        if fn in names and callable(names[fn]):
            args = [_safe_eval(arg, names) for arg in node.args]
            if node.keywords:
                raise ValueError("Keyword args not allowed")
            return names[fn](*args)
        raise ValueError(f"Unknown function: {fn}")
    raise ValueError("Unsupported expression")


def safe_evaluate(expr: str, last: float | int | None) -> float:
    names = dict(_ENV)
    if last is not None:
        names['ans'] = last
    try:
        tree = ast.parse(expr, mode='eval')
        return _safe_eval(tree, names)
    except ZeroDivisionError:
        raise ZeroDivisionError("Division by zero")
    except Exception as e:
        raise ValueError(str(e))


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.last = None

        self.entry = tk.Entry(self, font=("Segoe UI", 18), justify='right', bd=8, relief='groove')
        self.entry.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=8, pady=8)
        self.entry.focus_set()

        buttons = [
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.', '(', '+'),
            (')','%','//','**'),
            ('AC','⌫','=','ans'),
        ]

        for r, row in enumerate(buttons, start=1):
            for c, label in enumerate(row):
                cmd = (lambda ch=label: self.on_button(ch))
                tk.Button(self, text=label, command=cmd, font=("Segoe UI", 14), width=5, height=2).grid(row=r, column=c, padx=4, pady=4, sticky='nsew')

        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        for i in range(len(buttons)+1):
            self.grid_rowconfigure(i, weight=1)

        self.bind('<Return>', lambda e: self.on_button('='))
        self.bind('<KP_Enter>', lambda e: self.on_button('='))
        self.bind('<BackSpace>', lambda e: self.on_button('⌫'))
        self.bind('<Escape>', lambda e: self.on_button('AC'))

    def on_button(self, ch: str):
        if ch == 'AC':
            self.entry.delete(0, tk.END)
            return
        if ch == '⌫':
            cur = self.entry.get()
            if cur:
                self.entry.delete(len(cur)-1, tk.END)
            return
        if ch == '=':
            expr = self.entry.get().strip()
            if not expr:
                return
            try:
                value = safe_evaluate(expr, self.last)
                self.entry.delete(0, tk.END)
                self.entry.insert(0, str(value))
                self.last = value
            except Exception as e:
                messagebox.showerror("Error", str(e))
            return
        if ch == 'ans':
            if self.last is not None:
                self.entry.insert(tk.END, 'ans')
            else:
                messagebox.showinfo("Info", "No previous answer yet")
            return
        # default: append character
        self.entry.insert(tk.END, ch)


if __name__ == '__main__':
    Calculator().mainloop()
