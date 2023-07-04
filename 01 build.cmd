@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib

echo ^<head^> > .\release\log14401.html
echo ^<link rel="stylesheet" href="style.css"^> >> .\release\log14401.html
echo ^<title^>Logik - Feiertage / Ferien (14401)^</title^> >> .\release\log14401.html
echo ^<style^> >> .\release\log14401.html
echo body { background: none; } >> .\release\log14401.html
echo ^</style^> >> .\release\log14401.html
echo ^<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"^> >> .\release\log14401.html
echo ^</head^> >> .\release\log14401.html

@echo on

type .\README.md | C:\Python27\python -m markdown -x tables >> .\release\log14401.html

cd ..\..
C:\Python27\python generator.pyc "14401_FeiertageFerien" UTF-8

xcopy .\projects\14401_FeiertageFerien\src .\projects\14401_FeiertageFerien\release /exclude:.\projects\14401_FeiertageFerien\src\exclude.txt

@echo Fertig.

@pause
