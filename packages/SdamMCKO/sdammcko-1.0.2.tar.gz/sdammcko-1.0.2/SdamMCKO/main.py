
def q_help(N:int) -> str:
    """

    """
    file = f"".join([x.replace("/n","") for x in open("Guide.md")]).split("##")
    print(file[N])
