#!/usr/bin/env conda-execute

# conda execute
# env:
#  - nomkl
#  - python
#  - pip
#  - pillow
#  - pyyaml
#  - cartopy
# channels:
#  - conda-forge
# run_with: bash

set -e 

pip install -e ./

python -c "import mapproxy; print(mapproxy);"

echo $PREFIX
echo $PATH

du -hs $PREFIX

rm -rf $PREFIX/share/doc $PREFIX/share/gtk-doc 
rm -rf $PREFIX/lib/libicu* $PREFIX/lib/libxml*
rm -rf $PREFIX/bin/sqlite3
export SP_DIR=$PREFIX/lib/python*/site-packages
rm -rf $SP_DIR/scipy/stats $SP_DIR/pyproj

du -hs $PREFIX

mapproxy-util serve-develop mymapproxy/mapproxy.yaml --bind ${PORT:=8080}
