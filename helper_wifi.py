from wifi import Cell

#pip install wifi
    

# Replace 'wlan0' with your wireless interface name if needed
cells = Cell.all('wlan0')
for cell in cells:
    print(f"SSID: {cell.ssid}, Signal: {cell.signal}")