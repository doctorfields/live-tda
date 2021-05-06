#!/usr/bin/env sh

# abort on errors
set -e

npm run build

cd dist

git init
git add -A
git commit -m 'deploy'
git push -f https://github.com/doctorfields/live-tda.git master:gh-pages
rm -rf .git

cd -
