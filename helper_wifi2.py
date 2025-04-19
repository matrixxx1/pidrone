import subprocess
    
def scan_wifi():
    try:
       output = subprocess.check_output(["iwlist", "wlan0", "scanning"]).decode("utf-8")
       return output
    except subprocess.CalledProcessError:
       return "Error: Wireless interface not found or scanning failed."
    
output = scan_wifi()
print(output)
    
# Further parsing of the output is needed to extract SSIDs and other information.