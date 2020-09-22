#!/bin/bash

directory=
trace=
verbose=

usage()
{
    echo "usage: worker.sh [[[-i directory ] [-t] [-v]] | [-h]]"
}

while [ "$1" != "" ]; do
    case $1 in
        -i | --input-dir )      shift
                                directory=$1
                                ;;
        -t | --trace )          trace="--trace"
                                ;;
        -v | --verbose )        verbose="--verbose"
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

if [[ -z "$directory" ]]; then
  echo "You must specify input directory"
  exit 1
fi

python3 chapter_worker.py -i "$directory" "$trace" "$verbose"

python3 verse_worker.py -i "$directory" "$trace" "$verbose"

python3 tr_worker.py -i "$directory" "$trace" "$verbose"

