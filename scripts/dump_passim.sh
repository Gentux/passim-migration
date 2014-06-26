#!/bin/bash

eval "$(docopts -V - -h - : "$@" <<EOF
Usage: dump_passim [options]

      -d, --database=DATABASE   MongoDB database to use
      -D, --directory=DIR       Directory where dump will be stored
      -p, --petitpois-dir=DIR   Petitpois source directory
      -u, --petitpois-url=URL   Petitpois URL
      -l, --login=LOGIN         Petitpois Login
      -P, --password=PWD        Petitpois password
      -v, --verbose             Generate verbose messages.
      -h, --help                Show help options.
      --version                 Print program version.
----
dump_passim.sh 0.1.0
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
EOF
)"


[ $verbose = 'true' ] && set -xv


DUMP_DIR=$(readlink -e ${direcoty:-"$(pwd)/v$(date +%y).$(date +%m)"})
MONGO_DATABASE=${database:-"souk_passim"}
PETITPOIS_DIR=${petitpois_dir:-"$(python -c 'import petitpois; print petitpois.__path__[0]')"}
PETITPOIS_URL=${petitpois_url:-"http://petitpois.passim.info"}
PETITPOIS_LOGIN=${login}
PETITPOIS_PASSWORD=${password}


[ -d ${DUMP_DIR}/mongodb_dump/ ] || mkdir -p ${DUMP_DIR}/mongodb_dump/
mongodump -d ${MONGO_DATABASE} -o ${DUMP_DIR}/mongodb_dump/

[ -d ${DUMP_DIR}/csv_dump/ ] || mkdir -p ${DUMP_DIR}/csv_dump/
python ${PETITPOIS_DIR}/scripts/export_csv_api.py \
    -u ${PETITPOIS_URL}/poi/search -e ${PETITPOIS_LOGIN} -p ${PETITPOIS_PASSWORD} ${DUMP_DIR}/csv_dump/dump.zip
