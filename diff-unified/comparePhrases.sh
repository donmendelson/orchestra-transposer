# Files need to be split into their phrases to make them comparable
PHRASETYPE=$1
SOURCE=$2
TARGET=$3

cd phrases/$PHRASETYPE
echo "Comparing phrases for $PHRASETYPE..."

# Put together a list of all phrases found in source and target folder (remove path)
ls $SOURCE/*.xml $TARGET/*.xml > temp.txt
sed -i "" 's/.*\///g' temp.txt
sort -u -o List.txt temp.txt
rm temp.txt *.xml

# Concatenate files for source and target if both have that phrase
# Small files are appended to ceate one large file for XmlDiff
FILE1=${PHRASETYPE}_${SOURCE}.xml
FILE2=${PHRASETYPE}_${TARGET}.xml
touch $FILE1 $FILE2
echo "<phrases>" >> $FILE1
echo "<phrases>" >> $FILE2
while read file;
do
  if [ -f "$SOURCE/$file" ] && [ -f "$TARGET/$file" ];
  then
    # Add phrase to single phrases files
    cat "$SOURCE/$file" >> $FILE1
    cat "$TARGET/$file" >> $FILE2
  else
    # Check if missing file is only due to empty phrase in the other file, i.e. actually no difference in content, just syntax
    if [ -f "$SOURCE/$file" ]
    then
      grep "<text/>" "$SOURCE/$file" > x.txt
      if [ ! -f x.txt ]; then echo "Error: $file not found in $TARGET folder!"; fi
    fi
    if [ -f "$TARGET/$file" ]
    then
      grep "<text/>" "$TARGET/$file" > x.txt
      if [ ! -f x.txt ]; then echo "Error: $file not found in $SOURCE folder!"; fi
    fi
  fi
done < List.txt
echo "</phrases>" >> $FILE1
echo "</phrases>" >> $FILE2
if [ -f x.txt ]; then rm x.txt; fi

# Compare the new file against the old one to see if and how the new one has to change
DIFF="DIFF_$PHRASETYPE.xml"
CLASSPATH="../../diff-merge-1.5.1-SNAPSHOT-jar-with-dependencies.jar"
java io.fixprotocol.xml.XmlDiff $FILE2 $FILE1 $DIFF -u

# Remove namespace declaration and diff-element(s) to have achieve an empty file if there are no differences
sed -i "" -e '/<?xml/d' -e '/<diff/d' $DIFF
[ -s $DIFF ] && echo ">>> Differences found for $PHRASETYPE!"
[ ! -s $DIFF ] && echo ">>> No differences found for $PHRASETYPE!"
