# Compare unified repository file created from Basic against the one created from Orchestra
# Intended differences and those caused by bugs are then being removed
# The resulting diff file should be empty

CLASSPATH="diff-merge-1.5.1-SNAPSHOT-jar-with-dependencies.jar"

SOURCE="Repository"
OLD="Fix$SOURCE.xml"
NEW="$SOURCE.xml"
DIFF="diff-$SOURCE.xml"
BASE="diffbase-$SOURCE.xml"
java io.fixprotocol.xml.XmlDiff $NEW $OLD $DIFF -u
cp $DIFF $BASE

# (De)Activate line below to speed up testing of the code below after first run of orchestra2unified and XmlDiff ((de)activate them above)
# Base version contains all differences including those that are expected/intended, e.g. references to legacy spec volumes 1-7
#cp $BASE $DIFF

# Remove namespace declaration and timestamp differences
sed -i "" -e '/xmlns:xsi/d' -e '/xsi:/d' -e '/<?xml/d' -e '/fixRepository\/@generated/d' $DIFF

# Remove latestEP attribute differences (not supported in Orchestra)
sed -i "" '/latestEP/d' $DIFF

# Remove abbreviations section differences (not supported in Orchestra)
sed -i "" '/<abbreviations>/, /<\/abbreviations>/d' $DIFF

# Remove entries for positions in FIXimate (no longer needed with FIXimate4 using Orchestra as source)
sed -i "" -e '/@legacyPosition/d' -e '/@legacyIndent/d' $DIFF

# Remove entries for component types ImplicitBlock and ImplicitBlockRepeating
sed -i "" -e '/ImplicitBlock/d' -e '/XMLDataBlock/d' $DIFF

# Remove entries with generateImplFile, volume, inlined (to be confirmed that they are obsolete)
# Note: script reverses input file to delete line with search pattern and previous line in original file
sed -i "" '/<replace sel=.*@inlined/d' $DIFF
tail -r $DIFF | sed -e '/^.[ ]*type="@generateImplFile"/{N;d;}' -e '/^.[ ]*type="@inlined"/{N;d;}' -e '/^.[ ]*type="@volume"/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remove entries for textId differences as empty phrases are no longer explicit provided (see also GitHub issue #9)
# Remove entries for missing elaborationTextId references (they are basically obsolete as the phrases file only has textId with elaboration purpose)
tail -r $DIFF | sed -e '/^.[ ]*type="@textId"/{N;d;}' -e '/^.[ ]*type="@elaborationTextId"/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remove entries for datatype differences due to the removal of examples
# Note: result is kind of messy and needs further cleanup because some examples have more than 2 lines in the DIFF file
sed -i "" -e '/datatypes\[1\]\/datatype/{N;N;d;}' $DIFF
sed -i "" -e '/^"2006/d' -e '/^"15/d' -e '/^...Tm=/d' -e '/^Tm=/d' -e '/^MDEntryTime/d' -e '/^TransactTime/d' -e '/Example>/d' -e '/^Using/d' $DIFF

# Remove entries for empty group definition in enum values
tail -r $DIFF | sed -e '/^.[ ]*type="@group"/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remove entries with notReqXML=0 and required=0 (default values, no longer explicitly provided)
tail -r $DIFF | sed -e '/^.[ ]*type="@notReqXML">0</{N;d;}' -e '/^.[ ]*type="@required">0</{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

#-----------------------------------------------------------------------------------------------------
# BUGS REPORTED IN GITHUB

# Remove 2-line pedigree differences due to issues #25
tail -r $DIFF | sed '/^.[ ]*type="@updated/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remaining errors:
# - Missing enums for RiskLimitStatus and ProtectionTermEventDayType are due to an error in Basic that will be corrected with EP271

rm temp.xml
