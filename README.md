# BioNLP2016 - SeeDev Task
University of Melbourne's SeeDev binary event extraction system for BioNLP-Shared Task 2016.

Authors: P.C. Nagesh, Gitansh Khirbat <br>
Date: 20th June 2016 <br>
Project: SeeDev binary event extraction of BioNLP-Shared Task 2016.<br>
Paper: { <br>
		@inproceedings{panyam2016seedev, <br>
	        title={SeeDev Binary Event Extraction using SVMs and a Rich Feature Set}, <br>
	        author={Panyam, Nagesh C. and Khirbat, Gitansh and Verspoor, Karin and Cohn, Trevor and Ramamohanarao, Kotagiri}, <br>
      		booktitle={Proceedings of the 4th BioNLP Shared Task Workshop, ACL 2016}, <br>
        	pages={82},	<br>
	  	year={2016}, <br>
      }

PDF: { <br>
https://www.aclweb.org/anthology/W/W16/W16-30.pdf#page=92 <br>
}


## PROJECT INFORMATION

This is the public release of the University of Melbourne's system for SeeDev binary event extraction of BioNLP-Shared Task 2016. This task addresses the extraction of genetic and molecular mechanisms that regulate plant seed development from the natural language text of the published literature. This system makes use of support vector machine classifier with linear kernel powered by a rich set of features and achieved second-best results.

More details about the task can be obtained from: http://2016.bionlp-st.org/tasks/seedev

## License

MIT License

Copyright (c) [2016] [Unimelb]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## GETTING THE CODE UP
### Prerequisites
This code requires Python to be installed on your system. It is compatible with Python2 and Python3. If you do not have Python, it can be downloaded from https://www.python.org/downloads/

### External Software
This system assumes parses for input text are available. Constituency and Dependency parsing can be generated with Stanford CoreNLP software. It can be obtained from http://stanfordnlp.github.io/CoreNLP/

### Installing 
The archive contains 3 python files. They are:
<ol>
<li> classifier.py - Contains main() function, classifier and feature information </li>
<li> preprocess.py - Code to preprocess data using corenlpparse.py and produces data points (entity pairs). </li>
<li> corenlpparse.py - Contains methods to read data from files using Stanford's CoreNLP. </li>
<li> prepare_examples.sh  - this will run preprocess on all Seedev documents and prepare examples for classification. </li>
</ol>

### Using the code 
The code can be run by following these steps -
<ol>
<li> Prepare Data - Create a sub-directory "./data" within the directory of this code.
<ol>
  <li> Get SeeDev binary data from http://2016.bionlp-st.org/tasks/seedev - Three zip files would be obtained which are: BioNLP-ST-2016_SeeDev-binary_dev, BioNLP-ST-2016_SeeDev-binary_train and BioNLP-ST-2016_SeeDev-binary_test.
  </li>
  <li> Unzip these three files in the "./data" directory to get the files of the form "./data/BioNLP-ST-2016_SeeDev-binary_dev", "./data/BioNLP-ST-2016_SeeDev-binary_train" and "./data/BioNLP-ST-2016_SeeDev-binary_test".
  </li>
  <li> Run the Stanford CoreNLP to get dependency parsing on each "./*.txt" file present in the above three directories and store their output (parses) in "*.txt.out" format.
  	If Stanford CoreNLP is installed in your system, you can do "java -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,parse,ner,dcoref -file SeeDev-binary-11489176-1.txt  -outputDirectory  ./" to get  SeeDev-binary-11489176-1.txt.out.
	Do this for all *.txt files ( for i in *.txt; do  java -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,parse,ner,dcoref -file $i  -outputDirectory  ./ ; done	
  </li>
</ol>
</li>

<li> Assuming linux like system, (modify suitably otherwise) run the following script: <br>  bash prepare_examples.sh  <br>
</li>
<li> Run the classification , the main code <br>
Run the code by: python classifier.py <br>
</li>
<li>
The code will produce classifier result (Precision, Recall and F-Score) in the command line interface for each relation, followed by the overall results.
</li>
</ol>

## Contact

For questions about this distribution, bug reports and fixes, please contact:

Nagesh C. Panyam, Gitansh Khirbat <br>
Department of Computing and Information Systems <br>
The University of Melbourne, Australia <br>
{npanyam, gkhirbat}@student.unimelb.edu.au
