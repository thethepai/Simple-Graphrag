from graphrag.index.cli import index_cli


def main():
    # 设置参数
    root = "./ragtest"
    init = True

    # 调用 index_cli 函数
    index_cli(
        root=root,
        init=init,
    )


if __name__ == "__main__":
    main()
