# Files need to be split into their phrases to make them comparable
SOURCE=$1
TARGET=$2
PHRASETYPE=$3
PHRASEPREFIX=$4
PATTERN=$5

mkdir -p phrases/$PHRASETYPE
echo "\nExtracting $SOURCE into separate files for $TARGET $PHRASETYPE..."
cd phrases/$PHRASETYPE
mkdir -p old new

# Extract all phrases for datatypes into separate files (double quotes needed to expand variable for prefix)
cd $TARGET
rm *.xml
csplit -s -k -f $PHRASEPREFIX ../../../$SOURCE "/^.[ ]*<phrase textId=\"$PATTERN/" {100}

# Quit if pattern was not found in the source file
if [ ! -f ${PHRASEPREFIX}01 ]; then echo "No $PHRASETYPE found"; rm ${PHRASEPREFIX}00; CONT=0; exit; fi
rm ${PHRASEPREFIX}00

# Check if csplit reached its limit of 99 files and continue processing if that is the case
BATCH=0
if [ -f ${PHRASEPREFIX}99 ];
then
  CONT=1
  BATCH=1
  FILE=${PHRASEPREFIX}099
  cp ${PHRASEPREFIX}99 $FILE
else
  CONT=0
fi

while [ ! $CONT == 0 ]
do
  csplit -s -k -f $PHRASEPREFIX$BATCH $FILE "/^.[ ]*<phrase textId=\"$PATTERN/" {100}
  rm ${PHRASEPREFIX}${BATCH}00
  FILE=${PHRASEPREFIX}${BATCH}99
  if [ -f $FILE ];
  then
    BATCH=$(($BATCH+1));
  else
    CONT=0;
  fi
done
if [ ! $BATCH == 0 ]; then echo ">>> More than ${BATCH}00 $PHRASETYPE found!"; fi

# Only the first phrases element is need from each file, remove remainder
# Note: this is not really needed for prefixes that are sorted in the source file, e.g. DT for datatypes, but simple
for f in $PHRASEPREFIX*; do sed -i "" '/<\/phrase/q' $f; done

# Rename files by replacing sequence number with phrases ID
for file in $PHRASEPREFIX*; do if [ -f $file ]; then grep -m1 "" $file | cut -d'"' -f 2 | xargs -I '{}' mv $file '{}'.xml; fi done
