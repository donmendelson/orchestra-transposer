# Create unified repository and phrases file from an Orchestra file (runs several minutes without any output)
python3 ../orchestratransposer.py FIXLatest.xml --to unif -o Repository.xml Phrases.xml

CLASSPATH="./diff-merge-1.5.1-SNAPSHOT-jar-with-dependencies.jar"

OLD="FixRepository.xml"
NEW="RepositoryFromOrchestra.xml"
DIFF="diff-Repository.xml"
BASE="diffbase-Repository.xml"
java io.fixprotocol.xml.XmlDiff $NEW $OLD $DIFF -u
cp $DIFF $BASE

# (De)Activate line below to speed up testing of the code below after first run of orchestra2unified and XmlDiff ((de)activate them above)
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

# Remove entries with notReqXML (to be verified if these should continue ot be present or not)
sed -i "" -e '/<replace sel=.*@notReqXML/d' $DIFF
tail -r $DIFF | sed -e '/^.[ ]*type="@notReqXML"/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

#-----------------------------------------------------------------------------------------------------
# BUGS REPORTED IN GITHUB

# Remove single line differences due to issue #7 (pedigree missing and phrase reference incorrect)
sed -i "" -e '/<replace sel=.*@updated/d' -e '/<remove sel=.*@updated/d' -e '/<replace sel=.*repeatingGroup.*@textId/d' $DIFF

# Remove 2-line pedigree differences due to issue #7 and EP-1 (to be confirmed that we can drop it, we suppress it in FIXimate4)
tail -r $DIFF | sed -e '/^.[ ]*type="@added/{N;d;}' -e '/^.[ ]*type="@updated/{N;d;}' -e '/^.[ ]*type="@deprecated/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remove incorrect references to message titles (#11)
# Remove duplicate enums causing missing enum datatypes (issue #12)
# Remove missing reference attribute for length fields (issue #14)
sed -i "" -e '/<replace sel=.*@textId">MSG_/d' -e '/<remove sel=.*\/enum/d' -e '/<remove sel=.*\/text\(\)/d' $DIFF
tail -r $DIFF | sed -e '/^.[ ]*type="@enumDatatype"/{N;d;}' -e '/^.[ ]*type="@associatedDataTag"/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remove difference for the setting of "required" (issue #13)
sed -i "" '/<replace sel=.*@required/d' $DIFF

rm temp.xml
