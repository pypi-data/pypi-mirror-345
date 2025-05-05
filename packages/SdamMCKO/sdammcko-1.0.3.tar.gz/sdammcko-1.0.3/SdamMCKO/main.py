
def q_help(N:int) -> str:
    """

    """
    file = f"".join([x.replace("/n","") for x in open("SdamMCKO/Guide.md")]).split("##")
    return file[N]


if __name__ == "__main__":

    q_help(1)