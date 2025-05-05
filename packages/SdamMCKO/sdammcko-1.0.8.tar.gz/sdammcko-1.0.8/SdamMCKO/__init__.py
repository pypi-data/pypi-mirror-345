f"""

"""

def q_help(N:int) -> str:
    """

    """
    try:
        file = open('Guide.md', 'r', encoding='utf-8')
        content = f"".join(file.read()).split("##")
        print(content[N])
    except:
        
        file =  open('SdamMCKO/Guide.md', 'r', encoding='utf-8')
        content = f"".join(file.read()).split("##")
        print(content[N])


if __name__ == "__main__":

    q_help(2)

