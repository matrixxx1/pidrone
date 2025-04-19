    function sD(x,y,z){  
		window.location.href='/?action=ap&value1=' + x + '&value2=' + y + '&value3=' + z  + '&value4=' + window.droneX  + '&value5=' + window.droneY  + '&value6=' + window.droneZ;
		} 
	
	function sD2(x,y,z){  
		window.location.href='/?action=aplevel2&value1=' + x + '&value2=' + y + '&value3=' + z  + '&value4=' + window.droneX  + '&value5=' + window.droneY  + '&value6=' + window.droneZ;
		}
    
    
    function getIt(eleName){ 
		return document.getElementById(eleName).value; 
		}  
		

    function isChecked(eleName){ 
		return document.getElementById(eleName).checked; 
	}  

    function subForm(){
		if (isChecked(chkPause)==false ) {
			window.location.href='/?action=' + getIt("action") + '&value1=' + getIt("value1") + '&value2=' + getIt("value2") + '&value3=' + getIt("value3") + '&value4=' + getIt("value4") + '&value5=' + getIt("value5") + '&value6=' + getIt("value6"); 
		}
	}
    
	function autoPilot(){ 
		if (getIt("action")=="ap"){subForm();}
		}
    
	
	function autoPilotRefresh(){ 
		window.location.href='/';
		}
 