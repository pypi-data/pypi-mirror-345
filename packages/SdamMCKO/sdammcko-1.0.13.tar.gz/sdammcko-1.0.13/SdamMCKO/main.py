def q_help(N:int) -> str:
    """

    """
    try:
        file = open('Guide.txt', 'r', encoding='utf-8')
        content = f"".join(file.read()).split("##")
        print(content[N])
    except:
        try:
            file =  open('SdamMCKO/Guide.txt', 'r', encoding='utf-8')
            content = f"".join(file.read()).split("##")
            print(content[N])
        except FileNotFoundError as er:
            
            print('SdamGIA_PY/SdamMCKO') 