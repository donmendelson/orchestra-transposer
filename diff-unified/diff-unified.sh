# Create unified repository and phrases file from an Orchestra file (runs several minutes without any output)
#echo "Converting FIX Latest to Unified repository and phrases files..."
python3 ../orchestratransposer.py ../tests/xml/OrchestraFIXLatest.xml --to unif -o Repository.xml Phrases.xml

# Compare old and new repository file
./diffR.sh

# Compare old and new phrases file
./diffP.sh
