Set WshShell = CreateObject("WScript.Shell")
' Ejecuta el watchdog en segundo plano (0 oculta la ventana)
WshShell.Run "cmd /c d:\proyecto\carbones_y_pollos_tpv\watchdog_bridge.bat", 0, False
