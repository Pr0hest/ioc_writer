# check_yara_rules.py
#
# Copyright 2013 Mandiant Corporation.  
# Licensed under the Apache 2.0 license.  Developed for Mandiant by William 
# Gibb.
#
# Mandiant licenses this file to you under the Apache License, Version
# 2.0 (the "License"); you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
#
# Script to quickly check a YARA signature file against a set of files.
#

import os
import sys
import logging
import optparse

# logging config
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s  [%(filename)s:%(funcName)s]')

try:
    import yara
except ImportError, e:
    logging.error('Could not import yara')
    sys.exit(1)
    
def check_rules(rules, fp):
    matches = rules.match(fp)
    if matches:
        logging.info('Matched [%s] to %s' % (os.path.basename(fp), str(matches)))
        return True
    else:
        logging.debug('No match for [%s]' % os.path.basename(fp))
        return False
    
def main(options):
    if not options.verbose:
        logging.disable(logging.DEBUG)
    
    if not os.path.isfile(options.yara):
        logging.error('Yara rules file is not a file')
        sys.exit(1)
    
    try:
        rules = yara.compile(options.yara)
    except yara.SyntaxError, e:
        logging.error('Failed to process rules. [%s]' % str(e))
        sys.exit(1)
        
    path = options.fp
    if os.path.isfile(path):
        check_rules(rules, path)
    elif os.path.isdir(path):
        for fn in os.listdir(path):
            fp = os.path.join(path, fn)
            if os.path.isfile(fp):
                check_rules(rules, fp)
    else:
        logging.error('input is not a file or a directory')
        sys.exit(1)
    sys.exit(0)
    
def options():
    opts = []
    opts.append(optparse.make_option('--yara', '-y', dest = 'yara', 
                                    help = 'File of yara rules to process.', default = None))
    opts.append(optparse.make_option('--input', '-i', dest = 'fp', 
                                    help = 'Path of file or directory to check for yara matches.  Will not recurse the directory."', default = None))
    opts.append(optparse.make_option('--verbose', '-v', dest = 'verbose', action = 'store_true',
                                    help = 'Verbose output', default = None))
    return opts
    
if __name__ == "__main__":
    usage_str = """usage: %prog [options]
Test a yara rule against a set of files, or file."""
    parser = optparse.OptionParser(usage=usage_str, option_list=options())
    options, args = parser.parse_args()

    if not options.yara:
        logging.error('Must specify a yara rules file to process.')
        parser.print_help()
        sys.exit(1)

    if not options.fp:
        logging.error('Must specify a file or directory to process.')
        parser.print_help()
        sys.exit(1)

    main(options)
