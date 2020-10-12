DNDDIR=$(dirname $(realpath ${BASH_SOURCE[0]}))
cd $DNDDIR
../tr-cmd.py "$*" data data/spells-urnst

#../tableRoller.py "$*" data Spells-just-names.txt

