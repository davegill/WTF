#!/usr/bin/env python

import os
import sys
import getopt
import re
import shutil
import subprocess
import time

# Import common functions and definitions
import common


## run_wrf_tests.py
##
## Top-level script for running a set of regression tests for WRF. 
## 
## This script must be passed a "WRF Test File" (with a *.wtf filename extension), which 
## contains shell variable definitions for important user-specified parameters, such as 
## the directory pathnames for different test suite components.   One WRF Test File should 
## be created for each particular machine-compiler combination, such as "Linux with gfortran",
## or "<my_computer_name> with pgi".    
##
##  Author: Brian Bonnlander
##  Modification history:
##          Sep 2016, Michael Kavulich, Jr.: Ported original ksh script to python
##          Oct 2016, "                    : Script can be run directly from command line, or the function run_test can be
##                                              called from any other script

#list_of_codes_to_test[0]=code_to_test(False,"/Users/kavulich/WRFDA_REGTEST/WRF")
#list_of_codes_to_test[1]=code_to_test(True,"https://github.com/wrf-model/WRF","master")
list_of_codes_to_test=list() #initialize empty list
tardir = "/Users/kavulich/WTF/WTF/tarballs"


# First, we need to define some sub-functions

# usage: print out script usage info and exit

def usage():
   print("\nUsage: " + __file__ + " TEST_FILE.wtf")
   sys.exit(1)

##########################################################################

def run_wrf_tests():

 print("Starting script " + __file__)
##
## Parse command line and set WRF test file name.
## Check that the file exists and has a ".wtf" extension
##

 if not len(sys.argv)==2:
    print("\nError: you must specify a test file\n")
    usage()

 testfile=sys.argv[1]
 if testfile.rsplit('.', 1)[1]=="wtf":
    if not os.path.isfile(testfile):
       print("\nError: test file " + testfile + " does not exist!\n")
       usage()
 else:
    print("Error: Test files must end in '.wtf' extension")
    usage()

 starttime = time.asctime( time.localtime(time.time()) )
 print "Starting WTF :", starttime

 run_test(testfile)

 endtime = time.asctime( time.localtime(time.time()) )
 print "WTF done:", endtime


###################################################################################
# read_wtf: Read a test file, output the settings as a "test" class (as defined in common.py)

def read_wtf(testfile):
 
 new_test = common.test(testfile)         # Create a new test object
 with open(testfile) as tf:
    regexp = re.compile(r'^export')       # This regex checks if the line is setting an environment variable;
                                          # these are the lines we are interested in
    for line in tf:
       line = line.lstrip()               # "lstrip()" strips any leading whitespace from the line
       if regexp.search(line) is not None:
          line = line.replace("export","",1) # Remove "export" from start of line
          if "BUILD_TYPES" in line:       # "BUILD_TYPES" is a space-separated string, need to convert to list
             print("Found a BUILD_TYPE")
#             regex2 = re.compile(r'("|\').+("|\')') # This regex is a little intimidating I know, but it's just looking for 
#             line = re.findall(regex2,line)
             build_string = line.replace("BUILD_TYPES=","",1)
#             build_string = line[0]
             print("Line is")
             print(line)
             print("Build string is")
             print(build_string)
             new_test.build_types = build_string.split(" ")

 return new_test

# run_test: Reads test file, finds code, runs tests, prints results. This is the main guy!
def run_test(testfile):

 ##  Import settings from the WTF master control file. 
 test_from_file = read_wtf(testfile)

 ## Get WRF copies to build
 
 # Call ls to get a list of files in tardir
 ls_proc = subprocess.Popen(["ls", "-l", tardir], stdout=subprocess.PIPE)
 (out, err) = ls_proc.communicate()
 if err:
    sys.exit("There was an error: " + err)

 tar_ls_lines = out.splitlines() # Since ls -l returns files separated by line, we'll split the output by line

 del tar_ls_lines[0] # Get rid of the first element of our list; the first line returned by "ls -l" is unimportant
 for tar_line in tar_ls_lines:
    tar_name = tar_line.split(" ")[-1] # "tar_name" is the last column of this line from the "ls -l" command: the filename!
    regexp = re.compile(r'tar$')       # This regex checks if the last three characters of the filename are "tar"
    if regexp.search(tar_name) is not None:
       print(tar_name + " is a tar file")
       print("Found a tar file, will test it!")
       list_of_codes_to_test.append(tar_name)
    else:
       if "README" in tar_name:
          continue # There's always a readme, skip it
       else:
          print("WARNING: found unknown file " + tar_name)

 if not list_of_codes_to_test:
    print("\nERROR\nERROR\nERROR\n\nNo tests specified!")
    print("No tarfiles in " + tardir)
    sys.exit(1)

 print("list_of_codes_to_test:")
 print(list_of_codes_to_test)


 ##  Loop over all WRF source tarfiles.
 for code_to_test in list_of_codes_to_test:

    ## Run top-level build script
    print("Building " + code_to_test)
#    build_code(code_to_test,test_from_file)
 #   . $WRF_TEST_ROOT/scripts/allBuild.ksh  
 #   if [ $? -ne 0 ]; then
 #      echo "$WRF_TEST_ROOT/scripts/allBuild.ksh returned $?; aborting!"
 #      exit 255
 #   fi 

    ## Run top-level testing script
    print("Testing " + code_to_test)
 #   . $WRF_TEST_ROOT/scripts/allTest.ksh  
 #   retCode=$?
 #   if [ $retCode -ne 0 ]; then
 #      echo "$WRF_TEST_ROOT/scripts/allTest.ksh returned $retCode; aborting!"
 #      exit 255
 #   fi 
 
     ## Run script to generate summary of test results.
    print("Checking " + code_to_test)
 #    . $WRF_TEST_ROOT/scripts/allCheck.ksh  


 print("Script done!")    


#######################################################################################

if __name__ == "__main__":
    # execute only if run as a script
    run_wrf_tests()
