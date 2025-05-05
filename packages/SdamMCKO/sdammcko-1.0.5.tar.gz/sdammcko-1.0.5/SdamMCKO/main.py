def q_help(N:int) -> str:
    """

    """
    with open('Guide.md', 'r', encoding='utf-8') as file:
     content = f"".join(file.read()).split("##")
     print(content[N])


if __name__ == "__main__":

    q_help(2)