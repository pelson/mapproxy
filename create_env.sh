#!/usr/bin/env conda-execute

export ENV=$1
echo $ENV

conda create --yes -c conda-forge -p ${ENV} nomkl python pip pillow pyyaml cartopy

source activate $ENV
pip install ./

python -c "import mapproxy; print(mapproxy);"

export PREFIX=$ENV

du -hs $PREFIX
rm -rf $PREFIX/share/doc $PREFIX/share/gtk-doc 
rm -rf $PREFIX/lib/libicu* $PREFIX/lib/libxml*
rm -rf $PREFIX/bin/sqlite3
export SP_DIR=$PREFIX/lib/python*/site-packages
rm -rf $SP_DIR/scipy/stats
du -hs $PREFIX

