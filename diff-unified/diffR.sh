# Compare unified repository file created from Basic against the one created from Orchestra
# Intended differences and those caused by bugs are then being removed
# The resulting diff file should be empty

CLASSPATH="../tools/diff-merge-1.5.1-SNAPSHOT-jar-with-dependencies.jar"

SOURCE="FixRepository"
OLD="$SOURCE-xslt.xml"
NEW="$SOURCE-python.xml"
DIFF="diff-$SOURCE.xml"
BASE="diffbase-$SOURCE.xml"
java -cp "$CLASSPATH" io.fixprotocol.xml.XmlDiff $NEW $OLD $DIFF -u
cp $DIFF $BASE

# (De)Activate line below to speed up testing of the code below after first run of orchestra2unified and XmlDiff ((de)activate them above)
# Base version contains all differences including those that are expected/intended, e.g. references to legacy spec volumes 1-7
#cp $BASE $DIFF

echo "\nRemoving known and intended deviations"
echo "> Remove namespace declaration and timestamp differences"
sed -i "" -e '/xmlns:xsi/d' -e '/xsi:/d' -e '/<?xml/d' -e '/fixRepository\/@generated/d' $DIFF

echo "> Remove latestEP attribute differences (not supported in Orchestra)"
sed -i "" '/latestEP/d' $DIFF

echo "> Remove abbreviations section differences (not supported in Orchestra)"
sed -i "" '/<abbreviations>/, /<\/abbreviations>/d' $DIFF

echo "> Remove entries for positions in FIXimate (no longer needed with FIXimate4 using Orchestra as source)"
sed -i "" -e '/@legacyPosition/d' -e '/@legacyIndent/d' $DIFF

echo "> Remove entries for component types ImplicitBlock and ImplicitBlockRepeating"
sed -i "" '/ImplicitBlock/d' $DIFF

echo "> Remove entries with generateImplFile, volume, inlined (to be confirmed that they are obsolete)"
# Note: script reverses input file to delete line with search pattern and previous line in original file
sed -i "" '/<replace sel=.*@inlined/d' $DIFF
tail -r $DIFF | sed -e '/^.[ ]*type="@generateImplFile"/{N;d;}' -e '/^.[ ]*type="@inlined"/{N;d;}' -e '/^.[ ]*type="@volume"/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

echo "> Remove entries for textId differences as empty phrases are no longer explicitly provided"
# See also GitHub issue #9
echo "> Remove entries for missing elaborationTextId references"
# They are basically obsolete as the phrases file only has textId with elaboration purpose
tail -r $DIFF | sed -e '/^.[ ]*type="@textId"/{N;d;}' -e '/^.[ ]*type="@elaborationTextId"/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

echo "> Remove entries for datatype differences due to the removal of examples"
# Note: result is kind of messy and needs further cleanup because some examples have more than 2 lines in the DIFF file
sed -i "" -e '/datatypes\[1\]\/datatype/{N;N;d;}' $DIFF
sed -i "" -e '/^"2006/d' -e '/^"15/d' -e '/^...Tm=/d' -e '/^Tm=/d' -e '/^MDEntryTime/d' -e '/^TransactTime/d' -e '/Example>/d' -e '/^Using/d' $DIFF

echo "> Remove entries for empty group definition in enum values"
tail -r $DIFF | sed -e '/^.[ ]*type="@group"/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

echo "> Remove entries with notReqXML=0 and required=0 (default values, no longer explicitly provided)"
tail -r $DIFF | sed -e '/^.[ ]*type="@notReqXML">0</{N;d;}' -e '/^.[ ]*type="@required">0</{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

echo "> Remove difference due to XSLT still showing issue attribute (removed in Orchestra)"
tail -r $DIFF | sed '/^.[ ]*type="\@issue/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

#-----------------------------------------------------------------------------------------------------
# BUGS REPORTED IN GITHUB - NONE
echo "\nRemoving known and erroneous deviations"
echo "> NONE"
#-----------------------------------------------------------------------------------------------------

# Remove closing XML elements (only for legibility, assumes that everything else has been removed)
sed -i "" -e '/<\/add/d' -e '/<\/replace/d' $DIFF

echo "\nCompleted, see $DIFF for repository deviations."
rm temp.xml
