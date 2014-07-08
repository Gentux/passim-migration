#!/bin/bash

eval "$(docopts -V - -h - : "$@" <<EOF
Usage: reset.sh [options] [(-r <PETITPOIS_CONFIG_FILE>)]

      -r, --repair              Repair broken POIs
      -v, --verbose             Generate verbose messages.
      -h, --help                Show help options.
      --version                 Print program version.
----
reset 0.1.0
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
EOF
)"

[ $verbose = 'true' ] && set -xv

SCRIPT_FILENAME=$(readlink -e $0)
SCRIPT_DIR=$(dirname ${SCRIPT_FILENAME})/scripts
DUMP_DIR=$(dirname ${SCRIPT_FILENAME})/mongodb_dump
PETITPOIS_DIR=$(python -c "import petitpois; print petitpois.__path__[0]")
ETALAGE_DIR=$(python -c "import etalagepassim; print etalagepassim.__path__[0]")

if [ ! -d ${DUMP_DIR}/souk_passim ]; then
    echo 'You need to make dumps before upgrading';
    exit 1
fi

[ $repair = 'true' ] && python ${ETALAGE_DIR}/scripts/update_db_change_field_name.py \
    -v -s "Comarquage" -i "text-block" -l "Note" -nl "Notes" ${PETITPOIS_CONFIG_FILE}

python ${SCRIPT_DIR}/unify_schemes_to_information_services_scheme.py

[ $repair  = 'true' ] && python ${SCRIPT_DIR}/repair_common_pois_erros.py
[ $? -eq 0 ] && [ $repair = 'true' ] && python ${PETITPOIS_DIR}/scripts/reindex.py -v -c ${PETITPOIS_CONFIG_FILE}
