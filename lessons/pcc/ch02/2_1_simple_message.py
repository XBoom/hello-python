"""第 2 章练习 2-1：把一条消息放进变量并打印。

运行（仓库根目录）:
    source .venv/bin/activate
    python lessons/pcc/ch02/2_1_simple_message.py

例子会先打印出来。把 main 里的 TODO 写成你自己的消息后，再检查这一个文件:
    ruff format lessons/pcc/ch02/2_1_simple_message.py
    ruff check lessons/pcc/ch02/2_1_simple_message.py
    git status

git status 里可以出现 lessons/pcc/ch02/。不应出现 .venv 和 .env。这一章先不提交。
"""

# --- 例子：变量是一个名字，print 把它的内容打出来 ---
example = "变量保存一条消息"
print("例子:", example)


def main() -> None:
    # TODO: 删掉下一行。创建一个变量，放进你自己的一句话，然后 print 它。
    raise NotImplementedError("先完成 2-1")


if __name__ == "__main__":
    main()
