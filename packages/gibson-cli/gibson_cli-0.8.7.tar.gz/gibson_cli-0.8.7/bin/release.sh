sh bin/clean.sh
sh bin/build.sh
read -p "Enter the PyPI token: " token
uv publish --username __token__ --password $token
sh bin/clean.sh
