if [ "X$1" = "X" ]
then
  echo "Specify treasure type A-Z"
  exit
fi
./dnd.sh 'Treasure:Type="'$1'"'
