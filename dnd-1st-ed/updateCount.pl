#!/usr/bin/perl -w

$bumpeesFile=$ARGV[0];
$toBumpFile=$ARGV[1];

open( BUMPEES, "$bumpeesFile") or die "Couldn't open $bumpeesFile: $!";

while(<BUMPEES>)
{
  chomp;
  $bumpees{$_} = 0 if( !defined($bumpees{$_}) );
  $bumpees{$_} = $bumpees{$_} + 1;
}

close(BUMPEES);

open( TOBUMP, "$toBumpFile") or die "Couldn't open $toBumpFile: $!";

while(<TOBUMP>)
{
  chomp;

  $bump = 0;
  if( /^\|\s*([0-9]+)(\s*)(\|.*)/ )
  {
    ($num, $ws, $rest) = ($1, $2, $3);
    $iter = $rest;
    while( $iter =~ /\|\s*([^|]+?)\s*(\|.*)/ )
    {
      ($tok, $iter) = ($1, $2);
      if( defined($bumpees{$tok}) )
      {
        #print "Bumping $tok X${num}X\n";
        $bump = $bumpees{$tok};
      }
    }

    if( $bump )
    {
      print "| " . ($num + $bump) . "$ws$rest\n";
    }
    else
    {
      print "$_\n";
    }
  }
  else
  {
    print "$_\n";
  }
}

close(BUMPEES);


