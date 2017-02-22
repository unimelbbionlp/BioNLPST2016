mkdir predicted_relations/ 
cat /dev/null  > train_examples.txt
cat /dev/null  > dev_examples.txt
cat /dev/null  > test_examples.txt
cat /dev/null  > train_and_dev_examples.txt

find data/BioNLP-ST-2016_SeeDev-binary_dev/   -iname "*.txt" | while read fname ; do 
	documentid=${fname/.txt/};  
	python preprocess.py $documentid data/  >> dev_examples.txt
done

find data/BioNLP-ST-2016_SeeDev-binary_train/   -iname "*.txt" | while read fname ; do 
	documentid=${fname/.txt/};  
	python preprocess.py $documentid data/  >> train_examples.txt 
done

cat train_examples.txt dev_examples.txt > train_and_dev_examples.txt

find data/BioNLP-ST-2016_SeeDev-binary_test/   -iname "*.txt" | while read fname ; do 
	documentid=${fname/.txt/};  
	python preprocess.py $documentid data/  >> test_examples.txt
done
