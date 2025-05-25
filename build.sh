rm dist/vision-training.exe
pyinstaller -F __main__.py
mv dist/__main__.exe dist/vision-training.exe
