import sys
import pathlib

sys.path.insert(0, '../src/FinToolsAP/')

import QueryWRDS


# directory for loacl wrds database 
LOCAL_WRDS_DB = pathlib.Path('/home/andrewperry/Documents/wrds_database/WRDS.db')

def main():
    DB = QueryWRDS.QueryWRDS('andrewperry', LOCAL_WRDS_DB)

if __name__ == "__main__":
    main()