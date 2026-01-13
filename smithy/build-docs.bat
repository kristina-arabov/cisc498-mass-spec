@echo off
setlocal

REM Build Smithy docs script for Windows
REM Usage: build-docs.bat [md|html|all]
REM   md   - Build markdown docs only
REM   html - Build HTML docs only (requires Python + Sphinx)
REM   all  - Build both (default)

set SMITHY_DIR=%~dp0
set BUILD_DIR=%SMITHY_DIR%build\smithyprojections\msrobot-smithy\docs\docgen
set DOCS_DIR=%SMITHY_DIR%docs

REM Default to all
set FORMAT=all
if "%1"=="md" set FORMAT=md
if "%1"=="html" set FORMAT=html

echo Building Smithy model...
cd /d "%SMITHY_DIR%"
call "%SMITHY_DIR%gradlew.bat" build
if %ERRORLEVEL% neq 0 (
    echo Build failed!
    exit /b 1
)

REM Create output directories
if not exist "%DOCS_DIR%\md" mkdir "%DOCS_DIR%\md"
if not exist "%DOCS_DIR%\html" mkdir "%DOCS_DIR%\html"

if "%FORMAT%"=="md" goto :build_md
if "%FORMAT%"=="html" goto :build_html

:build_all
echo.
echo === Building Markdown docs ===
call :do_build_md
echo.
echo === Building HTML docs ===
call :do_build_html
goto :done

:build_md
call :do_build_md
goto :done

:build_html
call :do_build_html
goto :done

:do_build_md
echo Copying markdown docs...
if exist "%BUILD_DIR%\content" (
    xcopy /E /Y /I "%BUILD_DIR%\content\*" "%DOCS_DIR%\md\" >nul
    echo Markdown docs available at: %DOCS_DIR%\md
) else (
    echo Error: Build directory not found. Run build first.
    exit /b 1
)
exit /b 0

:do_build_html
echo Building HTML docs with Sphinx...

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found! Please install Python and add it to PATH.
    exit /b 1
)

REM Install requirements if needed
if exist "%BUILD_DIR%\requirements.txt" (
    echo Installing Sphinx requirements...
    pip install -q -r "%BUILD_DIR%\requirements.txt" 2>nul
)

if exist "%BUILD_DIR%\content" (
    cd /d "%BUILD_DIR%"
    python -m sphinx -b html content build\html
    if %ERRORLEVEL% neq 0 (
        echo Sphinx build completed with warnings.
    )
    xcopy /E /Y /I "build\html\*" "%DOCS_DIR%\html\" >nul
    echo HTML docs available at: %DOCS_DIR%\html\index.html
) else (
    echo Error: Build directory not found. Run build first.
    exit /b 1
)
exit /b 0

:done
echo.
echo Done!
