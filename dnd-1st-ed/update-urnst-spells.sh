../tableRoller.py "Table" data/ data/spells-urnst/ ./tmp.table  | grep '\[Level:'  | sed 's/.*Spell: \(.*\).$/\1/' | sort > spells.tmp
./updateCount.pl spells.tmp data/spells-urnst/Spells-M-U.txt  > spells-replace.tmp && mv spells-replace.tmp data/spells-urnst/Spells-M-U.txt 
