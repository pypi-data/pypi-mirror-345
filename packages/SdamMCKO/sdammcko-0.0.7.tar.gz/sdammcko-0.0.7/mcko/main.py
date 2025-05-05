
def help(N:int) -> str:
    file = f"".join([x.replace("/n","") for x in open("README.md")]).split("##")
    print(file[N])
