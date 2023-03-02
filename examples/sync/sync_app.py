import os
import sys
import getopt
import logging

from blueprint.sync import bpsync
from blueprint.sync import bpconcile

from blueprint.lib import event
from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

def main(argv):
    blueprint_lite_file = ''
    working_directory = ''
    output_blueprint_file = ''

    try:
        opts, args = getopt.getopt(argv,"h:b:s:w:o:",["bpfile=","wdir=","ofile="])
    except getopt.GetoptError:
        print('sync.py -b <blueprint_lite_file> -w <working_directory -o <output_blueprint_file>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("Usage :")
            print('   sync.py -b <blueprint_lite_file> -w <working_directory> -o <output_blueprint_file>')
            sys.exit()
        elif opt in ("-b", "--bpfile"):
            blueprint_lite_file = arg
        elif opt in ("-w", "--wdir"):
            working_directory = arg
        elif opt in ("-o", "--ofile"):
            output_blueprint_file = arg

    # if blueprint_lite_file == None or blueprint_lite_file == '':
    #     blueprint_lite_file = './examples/sync/data/bplite-2.yaml'

    # if working_directory == None or working_directory == '':
    #     working_directory = './examples/sync/temp'

    if blueprint_lite_file == None or blueprint_lite_file == '' or working_directory == None or working_directory == '':
            print("Usage :")
            print('   sync.py -b <blueprint_lite_file> -w <working_directory> -o <output_blueprint_file>')
            sys.exit()

    bm = bpsync.BlueprintMorphius.from_yaml_file(blueprint_lite_file)
    bp = bm.sync_blueprint(working_dir = working_directory, annotate = True)

    # bpr = bpconcile.BlueprintReconciler(bp)
    # bpr.reconcile()

    (out_yaml_str, errors) = bp.to_yaml_str()
    if output_blueprint_file == None or output_blueprint_file == '':
        print(out_yaml_str)
    else:
        with open(output_blueprint_file, 'w') as yaml_file:
            yaml_file.write(out_yaml_str)

    if len(errors) > 0:
        eprint(event.format_events(errors, event.Format.Table))

if __name__ == "__main__":
   main(sys.argv[1:])