@echo off
set PYTHONPATH=%PYTHONPATH%;%CD%\src
python -m pytest tests/unit/infrastructure/test_logging_config.py -v
echo.
echo Resultado dos testes: %ERRORLEVEL%
pause
