# BioNLP2016 - SeeDev Task
University of Melbourne's SeeDev binary event extraction system for BioNLP-Shared Task 2016.

Authors: Nagesh PC, Gitansh Khirbat <br>
Date: 20th June 2016 <br>
Project: SeeDev binary event extraction of BioNLP-Shared Task 2016.<br>
Paper: {Link goes here when the paper is up on ACL-web}


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

This code requires a working Stanford CoreNLP software. It can be obtained from http://stanfordnlp.github.io/CoreNLP/

### Installing 
The archive contains 3 python files. They are:
<ol>
<li> classifier.py - Contains main() function, classifier and feature information </li>
<li> preprocess.py - Code to preprocess data using corenlpparse.py and produces data points (entity pairs). </li>
<li> corenlpparse.py - Contains methods to read data from files using Stanford's CoreNLP. </li>
</ol>

### Using the code 
The code can be run by following these steps -
<ol>
<li> Load Data - Create a sub-directory "data" within the directory of this code.
<ol>
  <li> Store the training data in a sub-directory named "training_data" within this directory like this: "/data/train_data/" </li>
  <li> Store the test data in a sub-directory named "test_data" within this directory like this: "/data/test_data/" </li>
</ol>
</li>
<li> Depending on your system, open the corresponding command line interface (Terminal, Command Prompt). Set the current working directory as the directory containing the file classifier.py. <br>
Run the code by: python classifier.py <br>
</li>
<li>
The code will produce classifier result (Precision, Recall and F-Score) in the command line interface for each relation, followed by the overall results.
</li>
</ol>


## Contributing

Fork it!<br>
Create your feature branch: git checkout -b my-new-feature <br>
Commit your changes: git commit -am 'Add some feature' <br>
Push to the branch: git push origin my-new-feature <br>
Submit a pull request :D 

## History

version 1.0 - Initial release. 
Date - 22nd June 2016.

## Contact

For questions about this distribution, bug reports and fixes, please contact:
Nagesh PC, Gitansh Khirbat
Department of Computing and Information Systems
The University of Melbourne, Australia
{npanyam, gkhirbat}@student.unimelb.edu.au
