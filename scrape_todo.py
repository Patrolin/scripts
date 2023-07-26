
from sys import argv

def read_input() -> str:
    acc_input = ""
    with open(argv[1], "r", encoding="utf8") as f:
        acc_input = f.read()
    return acc_input

def parse_todos(text: str) -> list[str]:
    acc_todos = []
    for line in text.splitlines():
        if line.startswith("GIVEN"):
            acc_todos.append("")
        if acc_todos and line.strip():
            acc_todos[-1] = acc_todos[-1] + f"{line}\n"
    if acc_todos and (acc_todos[-1] == ""): acc_todos.pop()
    return acc_todos

if __name__ == "__main__":
    text = read_input()
    todos = parse_todos(text)
    for i, todo in enumerate(todos):
        print(f"{i+1}) \n{todo}\n")
