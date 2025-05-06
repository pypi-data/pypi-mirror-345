#!/usr/bin/env python
import sys,os, argparse, warnings
from collections import defaultdict
from pyexeggutor import (
    build_logger,
    get_file_size,
    get_directory_size,
    format_bytes,
    get_md5hash_from_file,
)
from veba_core.relational import (
    VEBAEssentialsDatabase,
)

__program__ = os.path.split(sys.argv[0])[-1]




def main(args=None):
    # Options
    # =======
    # Path info
    python_executable = sys.executable
    bin_directory = "/".join(python_executable.split("/")[:-1])
    script_directory  =  os.path.dirname(os.path.abspath( __file__ ))
    script_filename = __program__
    description = """
    Running: {} v{} via Python v{} | {}""".format(__program__, sys.version.split(" ")[0], python_executable, script_filename)
    usage = f"{__program__} -i <veba_essentials_directory> -o <output.db>"
    epilog = "Copyright 2025"

    # Parser
    parser = argparse.ArgumentParser(description=description, usage=usage, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)

    # Pipeline
    parser.add_argument("-i","--veba_essentials_directory", type=str, required=True, help = "path/to/veba_output/essentials/")
    parser.add_argument("-o","--output_database", type=str, required=True, help = "path/to/output.db SQLite database")
    parser.add_argument("-s","--store_sequences", action="store_true", help = "Store sequences in database")

    # Options
    opts = parser.parse_args()
    opts.script_directory  = script_directory
    opts.script_filename = script_filename

    # logger
    logger = build_logger("veba-core build-relational-database")

    # Commands
    logger.info(f"Command: {sys.argv}")
     
    # Size
    size_in_bytes = get_directory_size(opts.veba_essentials_directory)
    logger.info(f"Database size: {format_bytes(size_in_bytes)} ({size_in_bytes} bytes)")

    # Build
    database_url = f"sqlite:///{opts.output_database}"
    logger.info(f"Database URL: {database_url}")
    db_controller = VEBAEssentialsDatabase(
        database_url=database_url,
        veba_essentials_directory=opts.veba_essentials_directory,
        store_sequences=bool(opts.store_sequences),
    )
    db_controller.populate_all(reset_first=True)
    size_of_database = get_file_size(opts.output_database, format=True)
    logger.info(f"Database filesize: {size_of_database} ({opts.output_database})")

    # Hash
    path_md5 = opts.output_database + ".md5"
    md5 = get_md5hash_from_file(opts.output_database)
    logger.info(f"MD5 hash: {md5} ({path_md5})")
    with open(path_md5, "w") as f:
        print(md5, file=f)


    
if __name__ == "__main__":
    main()
    
    

    
