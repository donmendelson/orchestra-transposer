# Create Orchestra repository from the Unified repository files created by basic2orchestra (runs several minutes without any output)
# Not required if Orchestra repository file is copied from GitHub (https://github.com/FIXTradingCommunity/unified2orchestra/actions)
echo "\nConverting Unified created from Basic with XSLT to Orchestra repository files..."
#python3 ../orchestratransposer.py ../diff-unified/FixRepository-xslt.xml ../diff-unified/FixPhrases_en-xslt.xml --from unif --to orch -o orchestra-python.xml

# Compare Orchestra XML file created from Unified with XSLT against the one created with Python
# Intended differences and those caused by bugs are then being removed
# The resulting diff file should be empty

echo "\nComparing Orchestra repository file created from Unified using XSLT with the one created from Unified using Python"

OLD="orchestra-xslt.xml"
NEW="orchestra-python.xml"
DIFF="diff-orchestra.xml"
BASE="diffbase-orchestra.xml"

# Remove addedEP="-1" from Python version (XSLT version suppresses it) before creating the base difference file
grep ' addedEP="-1"' orchestra-python.xml > temp.xml
if [[ -s temp.xml ]]; then
  echo 'Removing attributes addedEP="-1" from Python source...'
  sed -i ".bak" 's/ addedEP="-1"//g' $NEW
fi

CLASSPATH="../tools/diff-merge-1.5.1-SNAPSHOT-jar-with-dependencies.jar"
java -cp "$CLASSPATH" io.fixprotocol.xml.XmlDiff $NEW $OLD $DIFF -u
cp $DIFF $BASE

# (De)Activate line below to speed up testing of the code below after first run of orchestra2unified and XmlDiff ((de)activate them above)
# Base version contains all differences including those that are expected/intended, e.g. references to legacy spec volumes 1-7
#cp $BASE $DIFF

echo Removing known and intended deviations

# Remove namespace declaration and timestamp differences
sed -i "" -e '/\@xmlns:/d' -e '/<?xml/d' $DIFF

# Remove differences in metadata (due to Dublin Core terms)
sed -i "" -e '/^.[ ]*<add.*metadata/d' -e '/^.[ ]*<dc:/d' -e '/^.[ ]*<remove.*dcterms/d' $DIFF

# Remove differences due to new appinfo element for session category
sed -i "" '/fixr:category\[\@name=\&#34;Session\&\#34;\]/d' $DIFF

# Remove differences due to latestEP attribute (no longer relevant in Orchestra)
sed -i "" '/^.[ ]*<add.*type="@latestEP"/d' $DIFF

# Remove differences due to builtin attribute values (0/1 versus false/true)
sed -i "" '/^.[ ]*<replace.*\@builtin/d' $DIFF

# Remove difference due to XSLT still showing issue attribute (removed in Orchestra)
tail -r $DIFF | sed '/^.[ ]*type="\@issue/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remove differences due to examples (no longer provided as part of the metadata)
# Note: script reverses input file to delete line with search pattern and previous two lines in original file
tail -r $DIFF | sed '/^.[ ]*purpose="EXAMPLE"/{N;N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remove XSLT errors (will not be fixed) when translating pedigree in Unified for groups and numInGroup fields
# XSLT translates Unified repeatingGroup pedigree to Orchestra group pedigree instead of numInGroup pedigree
# First, remove cases where the group has pedigree differences (e.g. different EP number for changes to group and numInGroup)
sed -i "" -e '/^.[ ]*<replace.*fixr:group.*\@updated/d' -e '/^.[ ]*<remove.*fixr:group.*\@updated/d' $DIFF
# Second, remove cases where numInGroup field erroneously did not have pedigree before and DIFF believes it should remove it
# This includes cases where group updates/deprecations are "lost in translation" to Orchestra with XSLT (e.g. PriceQualifierGrp)
sed -i "" -e '/^.[ ]*<remove.*numInGroup.*\@added/d' -e '/^.[ ]*<remove.*numInGroup.*\@updated/d' -e '/^.[ ]*<remove.*numInGroup.*\@deprecated/d' $DIFF
# Third, remove cases where group has no pedigree and DIFF believes it has to add it to the group
# Note: Somewhat risky as other two-line issues may also have differences related to updated(EP) attributes
# Note: script reverses input file to delete line with search pattern and previous line in original file
tail -r $DIFF | sed '/^.[ ]*type="\@updated/{N;d;}' | tail -r > temp.xml
cp temp.xml $DIFF

# Remove appinfo elements (not provided by XSLT version)
sed -i "" '/^.[ ]*<remove.*appinfo/d' $DIFF

# Remove replacements of annotations and related removals (Python version of Orchestra creates separate elements per line of multi-line documentation)
# NOTE: This removes too much when the content of the documentation is different or nested elements other than <documentation> exist in annotation!
sed -i "" -e '/^.[ ]*<replace.*annotation/d' -e '/^.[ ]*<remove.*annotation/d' $DIFF

# Remove lines starting with text and not a command ("<..."), e.g. multi-line text following a replace command
# NOTE: This may remove too much, not all cases known yet!
# Strip spaces from beginning of line
sed -i "" 's/^[ ]*//g' $DIFF
# Remove all lines unless they begin with a DIFF command ("<...") or the type attribute
grep '^<\|^type=' $DIFF > temp.xml
cp temp.xml $DIFF

#-----------------------------------------------------------------------------------------------------
# BUGS REPORTED IN GITHUB
# echo Removing known and erroneous deviations
echo NO MORE KNOWN BUGS FOR EP272
#-----------------------------------------------------------------------------------------------------

# Remove closing XML elements but only if they are at the beginning if the lines
# (only for legibility, assumes that everything else has been removed before that)
sed -i "" -e '/^<\/add/d' -e '/^<\/replace/d' $DIFF

echo "Completed, see $DIFF for repository deviations."
rm temp.xml
