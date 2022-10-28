set /p archivo=Nombre de archivo:
set directorio=%~d0%~p0
python -m PyQt5.uic.pyuic -x %directorio%%archivo%.ui -o %directorio%%archivo%.py
