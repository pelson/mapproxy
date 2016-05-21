#!/usr/bin/env bash
set -x

mkdir -p "$1" "$2" "$3"
build=$(cd "$1/" && pwd)
cache=$(cd "$2/" && pwd)
env_dir=$(cd "$3/" && pwd)


# -------

wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/.conda
export PATH=$HOME/.conda/bin:$PATH

# -------

source create_env.sh $HOME/env
cp -rf $HOME/env $build/
