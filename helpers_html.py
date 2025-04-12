
def makeLink(href, text):
    return "\n <a href='" + href + "'>" + text + "</a>" 

def makeInput(id,cls="",value=""):
    return "\n " + id + ": <input type='text' id='" + id + "' class='" + cls + "' value='" + value + "' /> " 

def getMimeType(fileExt):
    retval = "text/html"
    if (fileExt=="gif" ): 
        retval="image/gif"
    if ( fileExt=="jpg" ): 
        retval="image/jpeg"
    if (  fileExt=="png"): 
        retval="image/png"
    if (fileExt=="css" ): 
       retval = "text/css"                       
    if (fileExt=="js"  ): 
       retval =  "text/javascript"
    if (fileExt=="html"  ): 
        retval = "text/html"
    return retval