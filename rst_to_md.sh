FILES=$(find . -type f -name "*.rst")
#FILES=*.rst
for f in $FILES
do
  filename="${f%.*}"
  echo "Converting $f to $filename.md"
  pandoc $f -f rst -t markdown -o $filename.md
  sed -i 's/:::/```/g' "$filename.md"
  sed -i 's/{.toctree}/{toctree}/g' "$filename.md"
  sed -i 's/{.tags}/{tags}/g' "$filename.md"
  sed -i 's/\\//g' "$filename.md"
done