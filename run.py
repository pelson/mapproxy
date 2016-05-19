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

pip install -e ./

python -c "import mapproxy; print(mapproxy);"

mapproxy-util serve-develop mymapproxy/mapproxy.yaml --bind $PORT
