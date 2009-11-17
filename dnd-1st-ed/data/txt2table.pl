#!/usr/bin/perl -wn

s/^\s*//;
s/\s*$//;
s/^([0-9]+)\s*-\s*([0-9]+)/$1->$2/;

if( /^(.*?)	/ )
{
  #found a row in the table
  if( $1 eq "Dice" || $1 =~ /[->0-9]+/ )
  {
    s/^Dice/Score/;
    s/(	+)/$1| /g;
    s/^/| /;
    s/$/	|/;
  }
}

if( /^TABLE\s*\(([^.]+).([^.]+)\.?\)\s*([^.]+)\.?$/ )
{
  $_ = "$1 $2 $3 (Score=d100)"
}

if( /^III[. ]+([^. ]+)[.\s]*(.*)$/ )
{
  print "#$2\n";
  $_ = "III $1 (Score=d100)"
}

print "$_\n";
