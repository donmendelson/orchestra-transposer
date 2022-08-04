# Compare Orchestra XML file created from Unified with XSLT against the one created with Python
# Intended differences and those caused by bugs are then being removed
# The resulting diff file should be empty

CLASSPATH="diff-merge-1.5.1-SNAPSHOT-jar-with-dependencies.jar"

OLD="../tests/xml/OrchestraFIXLatest_EP269.xml"
NEW="../tests/out/FixRepository2Orchestra.xml"
DIFF="diff-Orchestra.xml"
BASE="diffbase-Orchestra.xml"
java -cp "$CLASSPATH" io.fixprotocol.xml.XmlDiff $NEW $OLD $DIFF -u
cp $DIFF $BASE
