DNDDIR=$(dirname $(realpath ${BASH_SOURCE[0]}))
cd $DNDDIR
# Generate a gem, applying Shine cantrip if it's below value.
./dnd.sh 'Gems with Shine:Score=d100'
