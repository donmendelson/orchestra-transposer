# Create unified repository and phrases file from the Orchestra file created by unified2orchestra (runs several minutes without any output)
echo "Converting FIX Latest to Unified repository and phrases files..."
python3 ../orchestratransposer.py ../tests/out/FixRepository2Orchestra.xml --to unif -o Repository.xml Phrases.xml

# Compare old and new repository file
./diffR.sh

# Compare old and new phrases file
./diffP.sh
