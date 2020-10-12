if [ "X$1" = "X" ]
then
  echo "Specify treasure type A-Z"
  exit
fi
DNDDIR=$(dirname $(realpath ${BASH_SOURCE[0]}))
cd $DNDDIR
./dnd.sh 'Treasure:Type="'$1'"'
