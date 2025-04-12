def appendFile(file_path,text_to_append):
    with open(file_path, "a") as file:
        file.write(text_to_append)

def getFileExt(thefile):
    cutFile = thefile.lower().replace("?",".").split(".")
    return thefile[1]
    
def getFileName(thefile):
    cutFile = thefile.lower().replace("?",".").split(".")
    return thefile[0] 