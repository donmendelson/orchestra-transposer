# Create unified repository and phrases file from the Orchestra file created by unified2orchestra (runs several minutes without any output)
# Not required if Unified repository files are copied from GitHub (https://github.com/FIXTradingCommunity/unified2orchestra/actions)
echo "\nConverting FIX Latest to Unified repository and phrases files..."
#python3 ../orchestratransposer.py ../diff-orchestra/orchestra-python.xml --to unif -o FixRepository-python.xml FixPhrases_en-python.xml

# Compare old and new repository file
echo "\nComparing Unified repository file created from Basic using XSLT with the one created from Orchestra using Python"
./diffR.sh

# Compare old and new phrases file
echo "\nComparing Unified phrases file created from Basic using XSLT with the one created from Orchestra using Python"
./diffP.sh
