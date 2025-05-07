import json
import os
import re
from datetime import datetime
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from adal import AuthenticationContext
from functools import reduce
import requests
from types import SimpleNamespace
import time
import pandas as pd

class Landing:
    """
        A class for landing API ingests and other data into Azure Data Lake Storage (ADLS). Currently can ingest SharePoint Online data and JSON (API-sourced) data.

        Methods:
        - set_static_col
        - set_config
        - set_bronze
        - set_landing_folder
        - set_content_type
        - set_tmp_file_location
        - set_autorename
        - set_distinct
        - set_tab_name
        - set_adls_container
        - set_auto_archive
        - set_sharepoint_location
        - set_sharepoint_auth
        - get_all_sharepoint_files
        - get_sharepoint_file
        - put_json_content
        - put_bronze

    """

    def __init__(self, spark, dbutils, database, bronze_table, target_folder = None, filename = None, catalog = 'default', container = 'bronze'):
        """
          Initializes a Landing object with the specified parameters.

          Parameters:
          - spark:                            SparkSession object to be used for processing.
          - dbutils:                          Databricks utilities object for file operations.
          - database:                         Name of the database where the data should be landed.
          - bronze_table:                     Name of the bronze table where the data should be landed.
          - target_folder (str, optional):    ADLS folder path where files should be stored. If None, it is inferred based on the database and bronze table.
          - filename (str, optional):         Filename with extension for the data to be landed.
          - catalog (str, optional):          Catalog used in Delta Lake (default is 'default').
          - container (str, optional):        ADLS storage container name (default is 'bronze').

          Attributes:
          - _dbutils:             Databricks utilities function for file operations.
          - _spark:               SparkSession object.
          - _container:           ADLS storage container name.
          - _target:              ADLS folder path where files should be stored.
          - _location:            Full path where files need to be stored.
          - _filename:            Cleaned filename with extension for the data.
          - _auto_archive:        Flag indicating whether to archive ingested files.
          - _file_path:           Full file path for the data.
          - _content_type:        Default content type for file upload (default is 'parquet').
          - _catalog:             Catalog used in Delta Lake.
          - _database:            Bronze database name.
          - _bronze_table:        Bronze table name for landing the data.
          - _bronze_table_path:   Complete path of the bronze table.
          - _joincolumns:         Columns to merge on when load type is set to merge.
          - _static_cols:         List of columns with fixed values to be added.
          - _loadtype:            Load type for data insertion (default is 'append').
          - _sharepoint_session:  SharePoint session object for authentication.
          - _timestamp:           Current timestamp.

          Raises:
          - Exception: If the specified location cannot be created.

          Notes:
          - The folder path is created if it does not exist.
        """

        self._dbutils       = dbutils                           # Required. Passes the dbutils function to be used down the line
        self._spark         = spark                             # Required. Passes a sparksession  to be used down the line

        #Ingestion vars
        self._container     = container                         # ADLS Storage container (Name of the blob storage)
        self._target        = target_folder                     # Required. the ADLS folder. Contains the full path after the storage container decleration. Should start with a /. If None or empty, one needs to be inferred.
        self._catalog       = catalog                           # Optional. the catalog used in delta lake. Defaults to prd
        self._database      = database                          # Required. the bronze database  that the data should be landed in
        self._bronze_table  = self.set_bronze(bronze_table, False)          # Required. the bronze tablename that the data should be landed in
        self._bronze_table_path  = f'{self._database}.{self._bronze_table}' # Complete path of the bronze table.

        if target_folder is None:
            self._target = database + '/' + self._bronze_table.replace("__", "/").lower()
            print(f'Target is not set so inferring based on bronze table name. Target set to {self._target}')

        if self._target is not None and 'abfss:' not in str(self._target):
            self._location      = os.environ.get("ADLS").format(container=self._container,path=self._target)    #full path of where files need to be stored. 
            #print(f'Target did not contain abfss yet; creating a full path location now: {self._location}')
        else:
            self._location      = self._target
            #print(f'Target was already a valid abfss location: {self._location}')

        self._file_name      = self._clean_filename(filename)    # Optional. the filename with extension that the data should be landed in

        self._excel_tabnames = []                               # Optional. Tells which tab names should be looked for in an excel file ingested from Sharepoint. If this list is empty, the first tab is used. 
        self._renamefiles   = True                              # Optional. Default behaviour adds a timestamp at the start of the filename in ADLS

        # Construct the full file path
        if self._file_name is not None and self._location is not None:
          self._file_path = os.path.join(self._location, self._file_name)
        else:
          self._file_path = None

        self._temp_file_path = None

        self._content_type  = 'parquet'                         # Default expectation is to upload a Parquet file. change it when needed using the SET function

        #Bronze vars
        
        self._distinct      = False                             # By default the input data is not made distinct
        self._joincolumns   = None                              # When load type is set to merge, this will contain the columns to merge on
        self._static_cols   = []                                # List of columns (dictionaries) that should be added with their fixed value, not in the source data. 
        self._loadtype      = 'append'                          # By default just add it into bronze

        self._dbxcreated = datetime.now()                       # default timestamp for the DbxCreated column. Can be overwritten. 

        self._column_logic = {}                                 # Optional. Can be used if a column needs to be manipulated before entering into bronze. contains a dictionary with the column name as key and a function as value.

        self._null_column_mismatch = False                      # Optional. If set to True, the function will try to add NULL columns to fix mismatches between the source and the bronze table.
        self._replacefile = True                                # Optional. If set to True, the function will re-ingest files that are already added, and older entries are marked as IsDeleted = 1. If set to false, the function will not re-ingest a file if the filename is already found in bronze layer.
        self._fix_schema = False                                # Optional. If set to True, the function will try to fix schema mismatches between the source and the bronze table.
        self._delta_columns = ['DbxCreated', 'DbxUpdated', 'IsDeleted', 'Sourcefile']

        #Helper vars
        self._sharepoint_session = None

        #Logging vars
        self._log_records_influenced = 0
        self._log_files_ingested = 0
        self._log_start_time = datetime.now()
        self._log_end_time = datetime.now()

        
        # Check if the database exists
        databases = [db.name for db in spark.catalog.listDatabases()]
        if database not in databases and database != 'pytest':
            raise ValueError(f"Database {database} not found in the SparkSession.")

        # Check if the table name is valid
        if not re.match(r'^[a-zA-Z0-9_]+$', self._bronze_table):
            raise ValueError(f"Invalid table name: {self._bronze_table}. Table names can only contain alphanumeric characters and underscores.")
        
        #print(f'location: {self._location} | for the bronze table {self._bronze_table_path}')
    
    ##############################################
    # Basic configuration options for landing.   #
    ##############################################

    def create_folder(self):
        # Ensure the specified location exists, create it if it doesn't
        if not os.path.exists(self._location):
            print(f'Folder path {self._location} did not exist yet. Making the dir at location.')
            try:
                os.makedirs(self._location, exist_ok=True)
            except Exception as e:
                raise Exception(f'Failed to create the folder at location {self._location}. Error: {e}')

    def set_static_col(self, cols = {}):
        """
        Set additional static columns for the bronze layer table.
        """
        print(f'Added columns to bronze layer table: {cols}')
        self._static_cols.append(cols)
        
        return self

    def get_static_col(self):
        """
        Get the status column for the bronze layer.
        """
        return self._static_cols
    
    def set_config(self, data = {}):
        """
        Store the config on the ingested data that allows us to put it to bronze layer
        """

        if 'loadtype' in data:
            self._loadtype = data['loadtype']
        
        if 'join' in data:
            if isinstance(data['join'], list):
              self._joincolumns = data['join']
            else:
              raise Exception(f'Invalid join columns: {data["join"]}. We expect a stringified list.')

        if self._loadtype == 'merge':
            if self._joincolumns is None:
                raise Exception('Join columns must be specified when load type is set to merge.')

        if 'replacefile' in data:
            if isinstance(data['replacefile'], bool):
              self._replacefile = data['replacefile']

        return self

    def get_config(self):
        """
        Get the configuration for the bronze layer.
        """
        return {
            'loadtype': self._loadtype,
            'join': self._joincolumns,
            'replaceFiles': self._replacefile,
            'static_cols': self._static_cols
        }

    def set_bronze(self, table, returning = True):
        """
        Sets the destination bronze table for landing the data.

        Args:
        - table (str): The name of the bronze table.
        - returning (bool): Flag to indicate if the function should return the updated object or the table name.

        Returns:
        - object or str: The updated object if returning is True, else returns the table name.
        """
        if not table.startswith("bronze__"):
            table = "bronze__" + table
            print(f'Changing bronze table name to {table}')
        self._bronze_table = table

        if returning:
            return self
        else:
            return table

    def set_landing_folder(self, folder):
        """
        Sets the landing folder path for the data.

        Args:
        - folder (str): The folder path for landing the data.
        """
        self._location = os.environ.get("ADLS").format(container=self._container,path=folder)

    def set_content_type(self, content_type):
        """
        Sets the content type for the data.

        Args:
        - content_type (str): The content type (JSON, CSV, XLSX, PARQUET).

        Raises:
        - ValueError: If the content type is not one of the allowed types.
        """
        allowed_content_types = ['json', 'csv', 'xlsx', 'xls','xlsm', 'parquet']
        if content_type.lower() not in allowed_content_types:
            raise ValueError(f"Invalid content type. Allowed types are: {', '.join(allowed_content_types)}")

        self._content_type = content_type
        return self
    
    def set_tmp_file_location(self, location):
        """
        Sets the temporary file location.

        Args:
        - location (str): The temporary file location.

        Returns:
        - object: The updated object with the temporary file location set.
        """
        self._tmp_file_location = location
        return self

    def set_autorename(self, rename = True):
        """
        Optional function to change the autorename that happens when adding a file to landing. By default the ingested filename is changed (or inferred) and includes the loading timestamp as part of the filename

        Args:
        - rename (bool): Required. True / False flag.
        """

        self._renamefiles = rename

        return self

    def set_adls_container(self, container):
        """
        Sets the ADLS container for the data.

        Args:
        - container (str): The container name.

        Returns:
        - object: The updated object with the container set.
        """
        self._container = container
        return self
    
    def set_auto_archive(self, archive):
        """
        Set the auto archive flag for the SharePoint files.

        Parameters:
        - archive (bool): Flag indicating whether to automatically archive SharePoint files.

        Returns:
        - None
        """
        if not isinstance(archive, bool):
            raise ValueError("The 'archive' parameter must be a boolean value.")

        self._auto_archive = archive

        return self      

    def set_tab_name(self, tabnames):
        """
        Set the standard tab to ingest for excel files collected from the SharePoint files.

        Parameters:
        - tabnames (string): the tab name to look for. Can be an array. if an array then the datatype is expected to be identical and ingests to the same table. 

        Returns:
        - None
        """
        if not isinstance(tabnames, list):
            raise ValueError(f"The 'tabname' parameter must be a list. Received type: {type(tabnames).__name__}.")

        self._excel_tabnames = tabnames

        return self      

    def set_fix_schema(self, fix_schema):
        """
        Set the null column mismatch flag for the SharePoint files.

        Parameters:
        - null_column_mismatch (bool): Flag indicating whether to add NULL columns to fix schema mismatches.

        Returns:
        - None
        """
        if not isinstance(fix_schema, bool):
            raise ValueError("The 'fix_schema' parameter must be a boolean value.")

        self._fix_schema = fix_schema

        return self
    
    def get_fix_schema(self):
        return self._fix_schema

    ##############################################
    # SharePoint Ingestion to landing function.  #
    ##############################################

    def set_sharepoint_location(self, Resource):
        """
        Sets the SharePoint Source location for the data.

        Args:
        - Resource (str): The SharePoint resource path.

        Returns:
        - object: The updated object with the SharePoint location set.
        """
        
        # Check if the Resource resembles a SharePoint Online URL
        if '.sharepoint.com/sites' not in Resource:
            raise ValueError("Invalid SharePoint Online URL format. Please provide a valid SharePoint Online URL.")

        self._sharepoint_uri = '/'.join(Resource.rstrip('/').split('/')[:3]) + '/'
        parts = Resource.rstrip('/').split('/')
        self._sharepoint_site = parts[4]
        self._sharepoint_folder = '/'.join(parts[5:])
        self._sharepoint_folder_path = os.path.join(self._sharepoint_site, self._sharepoint_folder)

        if not self._sharepoint_folder_path[0] == '/':
            self._sharepoint_folder_path = "/" + self._sharepoint_folder_path

        # Print the values of each variable for verification
        print("SharePoint URI:", self._sharepoint_uri)
        print("SharePoint Folder Path:", self._sharepoint_folder_path)

        return self

    def get_sharepoint_location(self):
        return {
            'sharepoint_uri': self._sharepoint_uri,
            'sharepoint_site': self._sharepoint_site,
            'sharepoint_folder': self._sharepoint_folder,
            'sharepoint_folder_path': self._sharepoint_folder_path
        }
    
    def get_sharepoint_auth(self):
        return {
            'sharepoint_user': self._sharepoint_user,
            'sharepoint_pass': self._sharepoint_pass,
            'sharepoint_client_id': self._sharepoint_client_id
        }

    def get_file_name(self):
        return self._file_name

    def set_sharepoint_auth(self, UserName, Password, Client_ID):
        """
        Sets the SharePoint authentication credentials.

        Args:
        - UserName (str): The username for SharePoint authentication.
        - Password (str): The password for SharePoint authentication.
        - Client_ID (str): The client ID for SharePoint authentication.

        Returns:
        - object: The updated object with the SharePoint authentication credentials set.

        Raises:
        - ValueError: If any of the input variables (UserName, Password, Client_ID) are empty.
        """
        if not UserName or not Password or not Client_ID:
            raise ValueError("Username, Password, and Client ID cannot be empty.")
        
        self._sharepoint_user      = UserName
        self._sharepoint_pass      = Password
        self._sharepoint_client_id = Client_ID

        return self

    def list_all_sharepoint_files(self, MatchingRegexPattern = '^.*\.(xlsx)$'):
        """
            This function will list all files under a Sharepoint folder and download the ones matched. Finally, it will hook the files into a delta bronze table defined. 
            
            Parameters:
            @MatchingRegexPattern: Matching criteria on file name as Regex Pattern i.e for xls files '^.*\.(xls)$' or files containing the MASTER word '^.*MASTER*'
            
            Return
            List of SharePoint file objects, use dir(file) to see all properties like file.serverRelativeUrl or file.name
        """  
        
        MyFiles = []

        response = self._sharepoint_apicall()

        if response:
            try:
                existing_files = []
                if self._replacefile == False and self._spark.catalog.tableExists(self._bronze_table_path):
                  print(f'Table {self._bronze_table_path} exists and we do not want to replace files, checking for existing files.')
                  #Check if the file exists in the lake first as we do not need to re-ingest the file
                  if self._renamefiles:
                    sql = f'''SELECT DISTINCT SUBSTR(Sourcefile, 23, 255) Sourcefile 
                              FROM {self._bronze_table_path}
                          '''
                  else:
                    sql = f'''SELECT DISTINCT Sourcefile 
                              FROM {self._bronze_table_path}
                          '''
                  try:
                      # Check if the table exists
                          distinct_files_df = self._spark.sql(sql)
                          existing_files = [row.Sourcefile for row in distinct_files_df.collect()]
                          print(f"Files found in the table already: {existing_files}")
                  except Exception as e:
                      print(f"Error checking for existing files: {e}")
                else:
                    print(f'Table {self._bronze_table_path} does not exist yet, so we cannot check for existing files.')

                jsons = json.loads(response.content)
                jsonvalue = jsons["d"]["results"]
                json_string = json.dumps(jsonvalue)
                files = json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))

                for file in files:
                    try:
                        if MatchingRegexPattern and re.match(MatchingRegexPattern, file.Name):
                            if self._replacefile == False and file.Name in existing_files:
                              print(f'Skipping file {file.Name} as it is already ingested and we do not want to re-ingest the file.')
                              continue
                            elif file.Name in existing_files:
                              print('Selected file {file.Name} as it is already ingested and we want to re-ingest the file, marking older records as IsDeleted = 1.')
                            MyFiles.append(file)
                    except Exception as file_error:
                        print(f"Error processing file {file.Name}: {str(file_error)}")

                return MyFiles
            
            except Exception as e:
                print(f"Failed to list all files in folder {self._sharepoint_folder_path}: {str(e)}")
                # Handle the exception gracefully or log it as needed
                # You can choose to raise the exception if it's critical or just continue with the remaining files
                return False
        else:
            print('No response from SharePoint API call')
            return False

    def download_sharepoint_file(self, file):
        print(f"Downloading file {file.Name}")
        try:
            self._file_path = self.get_sharepoint_file(file)
            return True
        except Exception as e:
            print(f"Error downloading file {file.Name}: {str(e)}")
            return False

    def convert_to_bronze(self, file):
        print(f"Adding file {file.Name} to bronze layer")
        try:
            self.put_bronze()
            return True
        except Exception as e:
            print(f"Error hooking the file {file.Name} in bronze layer: {str(e)}")
            return False

    def get_all_sharepoint_files(self, MatchingRegexPattern = '^.*\.(xlsx)$'):
        """
            This function will list all files under a Sharepoint folder and download the ones matched. Finally, it will hook the files into a delta bronze table defined. 
            
            Parameters:
            @MatchingRegexPattern: Matching criteria on file name as Regex Pattern i.e for xls files '^.*\.(xls)$' or files containing the MASTER word '^.*MASTER*'
            
            Return
            List of SharePoint file objects, use dir(file) to see all properties like file.serverRelativeUrl or file.name
        """  
        
        MyFiles = []

        response = self._sharepoint_apicall()

        if response:
            try:
                existing_files = []
                if self._replacefile == False:
                  #Check if the file exists in the lake first as we do not need to re-ingest the file
                  if self._renamefiles:
                    sql = f'''SELECT DISTINCT SUBSTR(Sourcefile, 23, 255) Sourcefile 
                              FROM {self._bronze_table_path}
                          '''
                  else:
                    sql = f'''SELECT DISTINCT Sourcefile 
                              FROM {self._bronze_table_path}
                          '''
                  # Check if the current file is already ingested
                  try:
                    distinct_files_df = self._spark.sql(sql)
                    existing_files = [row.Sourcefile for row in distinct_files_df.collect()]
                  except Exception as e:
                    print(f'Table doesnt exist yet so could not check for existing files.')

                jsons = json.loads(response.content)
                jsonvalue = jsons["d"]["results"]
                json_string = json.dumps(jsonvalue)
                files = json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))

                for file in files:
                    try:
                        if MatchingRegexPattern and re.match(MatchingRegexPattern, file.Name):
                            if self._replacefile == False and file.Name in existing_files:
                              print(f'Skipping file {file.Name} as it is already ingested and we do not want to re-ingest the file.')
                              continue
                            elif file.Name in existing_files:
                              print('Selected file {file.Name} as it is already ingested and we want to re-ingest the file, marking older records as IsDeleted = 1.')
                            MyFiles.append(file)

                            #print(f"File: {file.Name} - Selected for ingestion")
                            print(f"Downloading file {file.Name}")
                            self._file_path = self.get_sharepoint_file(file)

                            self.put_bronze()

                            # print('Archiving landed file')
                            # self._archive_file()

                    except Exception as file_error:
                        print(f"Error processing file {file.Name}: {str(file_error)}")

            except Exception as e:
                print(f"Failed to list all files in folder {self._sharepoint_folder_path}: {str(e)}")
                # Handle the exception gracefully or log it as needed
                # You can choose to raise the exception if it's critical or just continue with the remaining files

        self._sharepoint_files = MyFiles

        print(f'SharePoint folder {self._sharepoint_folder_path} contains {len(files)} files, out of which {len(MyFiles)} file(s) are selected.')

        return self

    def get_sharepoint_file(self, file, destination_filename=None):
        """
            This function will DOWNLOAD a file from a SharePoint, locally to databricks tmp folder first, and copied to a container if needed.
            
            Parameters:
            @FileNameSource: File name to download i.e. 'Master Remapping Table.xlsx'
            
            Return
            DownloadedPath:  Final location of the downloaded file.
        """

        SparkLocation = self._tmp_file_location
        PythonLocation = SparkLocation.replace('/dbfs/', 'dbfs:/')

        # Format all provided paths as needed
        if not self._sharepoint_folder_path.endswith('/'):
            self._sharepoint_folder_path += "/"
        if not self._sharepoint_uri.endswith('/'):
            self._sharepoint_uri += "/"
        if not self._sharepoint_folder_path.startswith('/'):
            self._sharepoint_folder_path = "/" + self._sharepoint_folder_path
        if self._location and not self._location.endswith('/'):
            self._location += "/"
        if self._location and self._location.startswith('/'):
            self._location = self._location[1:]

        if destination_filename is None:
            destination_filename = file.Name
        DownloadedPath = PythonLocation + file.Name

        ContainerPath = os.path.join(self._location, destination_filename)  # Format the Path, ADLS is stored with parameters

        self._dbxcreated = datetime.strptime(file.TimeCreated, '%Y-%m-%dT%H:%M:%SZ') if file.TimeCreated else datetime.strptime(file.TimeLastModified, '%Y-%m-%dT%H:%M:%SZ')

        try:
            response = self._sharepoint_apicall(file.Name)
            if response:
                # Generate a new filename based on the current datetime and original filename
                current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                original_filename, file_extension = os.path.splitext(file.Name)

                if self._renamefiles:
                    new_filename = f"{current_datetime} - {original_filename}{file_extension}"
                else:
                    new_filename = f"{original_filename}{file_extension}"

                with open(SparkLocation + file.Name, "wb") as local_file:
                    local_file.write(response.content)

                # Check if the uploaded file actually exists
                if os.path.exists(SparkLocation + file.Name):
                    # Move the file to ADLS with the new filename
                    new_file_path = os.path.join(self._location, new_filename)
                    try:
                        self._dbutils.fs.cp(PythonLocation + file.Name, new_file_path, True)
                      
                        if file_extension in ['.xlsx', '.xls']:
                            self._temp_file_path = PythonLocation + file.Name
                        else:
                            self._dbutils.fs.rm(PythonLocation + file.Name)

                        print(f'Successfully uploaded file to: {new_file_path}')

                        self._file_path = new_file_path
                        self._file_name = new_filename

                        self._log_files_ingested += 1
                    except Exception as e:
                      print(f'Error uploading file {file.Name} to path {new_file_path}: {e}')
                    return new_file_path
                else:
                    print('Error: Uploaded file does not exist')
                    return ("Error", "Uploaded file does not exist")

            else:
                error_msg = f"Error: Failed to retrieve file from SharePoint. Response: {response.text}"
                print(error_msg)
                return ("Error", error_msg)

        except Exception as e:
            error_message = f"An error occurred in get_sharepoint_file whilst trying to download the file: {e}"
            raise Exception(error_message)

    def get_temp_file_path(self):  
        """
        Returns the temporary file path where the file is downloaded before being moved to ADLS.
        """
        return self._temp_file_path if hasattr(self, '_temp_file_path') else None

    ###############################################
    # Raw Content Ingestion to landing function.  #
    ###############################################

    def put_json_content(self, json_data):
        """
        Stores JSON data into a JSON file at the specified location with the given filename.

        Args:
        - json_data (dict): The JSON data to be stored in the file.

        Returns:
        str: The full path of the saved JSON file.
        """
        try:

            # Get the row count of the JSON data
            row_count = len(json_data)

            # Write the JSON data to the file
            json_string = json.dumps(json_data, indent=4)
            
            #parquetfile     = self._file_path.replace('.json', '.parquet')
            #parquetfilename = self._filename.replace( '.json', '.parquet')
            try:
                # Write the JSON data to the file in ADLS Gen2
                df = self._spark.read.json(self._spark.sparkContext.parallelize([json_string]))
                # Write the DataFrame to a Parquet file on ADLS Gen2
                df.write.mode("overwrite").parquet(self._file_path)
                #self._dbutils.fs.put(self._file_path, json_string, overwrite=True)
                print("JSON data successfully written to the file.")
            except Exception as e:
                # Handle any exceptions that occur during the file write operation
                error_message = f"Error writing JSON data to file: {e}"
                print(error_message)

            #with open(self._file_path, 'w') as file:
            #    json.dump(json_data, file, indent=4)
            #time.sleep(10)

            # Check if the file was created
            files = self._dbutils.fs.ls(self._location)
            found_files = [file_info.name for file_info in files]

            #if parquetfilename in found_files:
            #return self._file_path, row_count
            #else:
            #    found_files_str = ", ".join(found_files)
            #    raise FileNotFoundError(f"The file was not found in the specified directory. looking for file {parquetfilename}, but files in the listed directory: {found_files_str}")
            
            self._file_name

            return self
        
        except (OSError, IOError) as e:
            # Handle file I/O errors
            error_message = f"Error occurred while writing JSON data to file: {e}"
            raise IOError(error_message)
        except Exception as e:
            # Handle other exceptions
            error_message = f"An error occurred: {e}"
            raise Exception(error_message)
        
    def put_xlsx_content(self, xlsx_content):
        """
        Stores xlsx streamed data into an XLSX file at the specified location with the given filename.

        Args:
        - xlsx_content (content): The xlsx binary data to be stored in the file.

        Returns:
        str: The full path of the saved xlsx file.
        """
        try:
                        
            current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            original_filename, file_extension = os.path.splitext(self._file_name)
            new_filename = f"{current_datetime} - {original_filename}{file_extension}"

            target_file_path   = self._location + '/' + new_filename

            #print(f'Filename: {self._file_name}, original filename: {original_filename}, new file name: {new_filename}')
            #print(f'Target locaction: {self._location}, target file path: {target_file_path}')
            
            PythonLocation = self._tmp_file_location.replace('/dbfs/', 'dbfs:/')
            try:
                with open(self._tmp_file_location + self._file_name, 'wb') as local_file:
                    local_file.write(xlsx_content)
            except Exception as e:
                print(f'Error saving in temp location {self._tmp_file_location}/{self._file_name}: {e}')

            if os.path.exists(self._tmp_file_location + self._file_name):
                # Move the file to ADLS with the new filename
                try:
                    self._dbutils.fs.cp(PythonLocation + self._file_name, target_file_path, True)
                    self._dbutils.fs.rm(PythonLocation + self._file_name)
                    self._file_name = new_filename
                    self._file_path = target_file_path
                    print(f'Successfully uploaded file to: {target_file_path}')

                except Exception as e:
                    print(f'Error uploading file {self._file_name} to path {target_file_path}: {e}')
            else:
                print('Error: Uploaded file does not exist')
            print("File downloaded successfully.")

            return self
        
        except (OSError, IOError) as e:
            # Handle file I/O errors
            error_message = f"Error occurred while writing xlsx data to file: {e}"
            raise IOError(error_message)
        except Exception as e:
            # Handle other exceptions
            error_message = f"An error occurred downloading the excel file into DBFS: {e}"
            raise Exception(error_message)
   
    #######################################
    # Databricks bronze layer ingestion.  #
    #######################################

    def set_file_name(self, filename):
        
        self._file_name = filename

        return self

    def set_column_logic(self, column_logic = {}):
        """
        Set the column logic for the bronze layer.
        """
        self._column_logic = column_logic
        return self

    def get_column_logic(self):
        return self._column_logic

    def _check_bronze_ingestion(self):
        """
        Get the distinct delta__sourcefile values from the bronze table self._bronze_table_path
        via self._spark.sql() and check that self._file_name is not ingested already.
        If the file is ingested already, update the bronze table by setting delta__deleted column to 1
        where the file name matches the ingested file.
        """
        # Get the distinct delta__sourcefile values from the bronze table
        existing_files = []
        if self._renamefiles:
          filetocheck = self._file_name[22:]
          sql = f'''
                    SELECT DISTINCT SUBSTR(Sourcefile, 23, 255) Sourcefile 
                    FROM {self._bronze_table_path}
                '''
        else:
          filetocheck = self._file_name
          sql = f'''
                    SELECT DISTINCT Sourcefile 
                    FROM {self._bronze_table_path}
                '''

        # Check if the current file is already ingested
        
        try:
            distinct_files_df = self._spark.sql(sql)
            existing_files = [row.Sourcefile for row in distinct_files_df.collect()]
        except Exception as e:
            print(f'Table doesnt exist yet so could not check for existing files.')
            
        if filetocheck in existing_files:

          if self._replacefile:
            # Update the bronze table to mark the ingested file as deleted. Use wildcard to enable both renamed with timestamp and non-renamed files to be updated.
            self._spark.sql(f"UPDATE {self._bronze_table_path} SET IsDeleted = 1 WHERE Sourcefile LIKE '%{filetocheck}'")
            print(f'Updated the bronze layer table to mark older records for file {filetocheck} as deleted')
            return True #Old records are marked, proceed with ingestion
          else:
            print(f'Skipped ingesting file {self._file_name} as it already exists in the bronze layer table')
            return False #We do not mark so we should block further processing of the file
        else:
          return True #No records are found, proceed with ingestion

    def get_distinct(self):
        return self._distinct

    def set_distinct(self):
        self._distinct = True

        return self

    def set_dbxcreated(self, timestamp):
        self._dbxcreated = timestamp

    def get_dbxcreated(self):
        return self._dbxcreated

    def _read_file(self):
        """
        Reads the file from the specified path and returns a DataFrame.
    
        Args:
        - file_path (str): The path to the file.
    
        Returns:
        - DataFrame: The DataFrame containing the data from the file.
        """
        if self._file_name is None:
            raise ValueError("Ran put_bronze but No filename specified.")

        file_extension = os.path.splitext(self._file_name)[1]

        try:
            # Check if the file is a CSV
            if file_extension == '.csv':
                stage = self._spark.read.format('csv') \
                    .option("header", "true") \
                    .option("quote", '"') \
                    .option("escape", '\"') \
                    .load(self._file_path)

            # Check if the file is an Excel file
            elif file_extension in ['.xlsx', '.xls']:
                # Read the Excel file using pandas

                filetoread = self.get_temp_file_path() if self.get_temp_file_path() else self._file_path
                print(f'Reading file from {filetoread}')
                SparkLocation = os.path.join('/dbfs/',self._container, self._target, self._file_name)

                all_sheets = pd.read_excel(filetoread, sheet_name=None)  # Read all sheets into a dictionary

                # Initialize an empty list to hold Spark DataFrames
                spark_dfs = []

                # Check if specific tab names are provided
                if isinstance(self._excel_tabnames, list) and self._excel_tabnames:
                    for tab_name in self._excel_tabnames:
                        if tab_name in all_sheets:
                            try:
                                df = all_sheets[tab_name]
                                #df = df.where(pd.notnull(df), None)

                                # Process in chunks of 50,000 records
                                for start in range(0, len(df), 50000):
                                    try:
                                        chunk = df.iloc[start:start + 50000]  # Get a chunk of 50,000 records
                                        spark_df = self._spark.createDataFrame(chunk)  # Convert to Spark DataFrame
                                        spark_df = spark_df.withColumn('SourceTabName', F.lit(tab_name))  # Add source tab name
                                        spark_dfs.append(spark_df)
                                    except Exception as chunk_error:
                                        print(f"Error processing chunk starting at index {start} for tab {tab_name}: {chunk_error}")
                            except Exception as tab_error:
                                print(f"Error processing tab {tab_name}: {tab_error}")
                        else:
                            print(f"Tab {tab_name} not found in the Excel file.")

                else:
                    # Load all tabs if no specific tab names are provided
                    for tab_name, df in all_sheets.items():
                        try:
                            #df = df.where(pd.notnull(df), None).astype(str)
                            # Process in chunks of 50,000 records
                            for start in range(0, len(df), 50000):
                                chunk = df.iloc[start:start + 50000]  # Get a chunk of 50,000 records
                                spark_df = self._spark.createDataFrame(chunk)  # Convert to Spark DataFrame
                                spark_dfs.append(spark_df)
                        except Exception as tab_error:
                            print(f"Error processing all sheets {tab_name}: {tab_error}")

                # Union all Spark DataFrames from different chunks
                if spark_dfs:
                    try:
                        stage = reduce(lambda df1, df2: df1.union(df2), spark_dfs)
                    except Exception as union_error:
                        print(f"Error during union of Spark DataFrames: {union_error}")
                        raise

                
            # Check if the file is a Parquet file
            elif file_extension == '.parquet':
                stage = self._spark.read.parquet(self._file_path)

            # Check if the file is a JSON file
            elif file_extension == '.json':
                stage = self._spark.read.json(self._file_path)

            else:
                raise Exception(f"Unsupported file format: {file_extension}")

            print(f"File read successfully at {datetime.now()}.")

            if self._temp_file_path is not None:
                try:
                    self._dbutils.fs.rm(self._temp_file_path)
                except Exception as e:
                    print(f"Error deleting temporary file {self._temp_file_path}: {e}")
            
            return stage

        except Exception as e:
            raise Exception(f"Error reading file: {self._file_path} | {str(e)}")

    def _clean_stage(self, stage):
        """
        Optimized function to clean the stage DataFrame by applying transformations and adding static columns.
        """
        try:
            # Add static columns if required
            if self._static_cols:
                print("Adding static columns to the DataFrame...")
                for static_col in self._static_cols:
                    for col, value in static_col.items():
                        stage = stage.withColumn(col, F.lit(value))
                print("Static columns added successfully.")

            # Clean column names
            column_mapping = {
                col: self._clean_column_name(col) for col in stage.columns if col != self._clean_column_name(col)
            }
            if column_mapping:
                stage = stage.select(
                    *[F.col(old_col).alias(new_col) if old_col in column_mapping else F.col(old_col)
                      for old_col, new_col in zip(stage.columns, [column_mapping.get(col, col) for col in stage.columns])]
                )
                print("Column names cleaned successfully.")

            # Add delta-specific columns
            delta_columns = {
                'DbxCreated': F.lit(self._dbxcreated),
                'DbxUpdated': F.lit(datetime.now()),
                'IsDeleted': F.lit(0),
                'Sourcefile': F.lit(self._file_name)
            }
            for col, value in delta_columns.items():
                stage = stage.withColumn(col, value)
            print("Delta columns added successfully.")

            # Ensure nulls are not replaced by NaN and cast back to original type
            for col in stage.columns:
                original_type = stage.schema[col].dataType
                stage = stage.withColumn(col, F.when(F.col(col).isNull(), None).otherwise(F.col(col)).cast(original_type))

            # Apply custom column logic if provided
            if self._column_logic:
                print("Applying custom logic to columns...")
                for col, logic_func in self._column_logic.items():
                    stage = stage.withColumn(col, logic_func(F.col(col)))
                print("Custom logic applied successfully.")

            # Apply distinct if required
            if self._distinct:
                print("Applying distinct to the DataFrame...")
                stage = stage.distinct()
                print("Distinct applied successfully.")

            return stage

        except Exception as e:
            raise Exception(f"Error in _clean_stage: {e}")
        
        
    def _stage_match_to_bronze(self, stage, delta_table):
        """
        Matches the schema of the stage DataFrame to the Delta table schema, ensuring compatibility.

        Args:
        - stage (DataFrame): The stage DataFrame to be matched.
        - delta_table (DeltaTable): The Delta table to match against.

        Returns:
        - DataFrame: The stage DataFrame with schema aligned to the Delta table.
        """
        try:
            # Extract Delta table schema and stage schema
            delta_schema = delta_table.toDF().schema
            stage_schema = stage.schema

            # Create dictionaries for quick lookup of field names and types
            delta_fields = {field.name.lower(): field.dataType for field in delta_schema.fields}
            stage_fields = {field.name.lower(): field.dataType for field in stage_schema.fields}

            # Identify missing and extra fields
            missing_fields = delta_fields.keys() - stage_fields.keys()
            extra_fields = stage_fields.keys() - delta_fields.keys()

            # Handle schema mismatches
            if (missing_fields or extra_fields) and not self._fix_schema:
                error_message = "Schema mismatch detected:\n"
                for field in missing_fields:
                    error_message += f"Missing in stage: {field}\n"
                for field in extra_fields:
                    error_message += f"Extra in stage: {field}\n"
                raise ValueError(error_message)

            if self._fix_schema:
                print("Fixing schema mismatches...")

                # Add missing fields to the stage DataFrame
                for field in missing_fields:
                    print(f"Adding missing field '{field}' to stage DataFrame as NULL.")
                    stage = stage.withColumn(field, F.lit(None).cast(delta_fields[field]))

                # Add extra fields to the Delta table
                for field in extra_fields:
                    print(f"Adding extra field '{field}' to Delta table.")
                    self._spark.sql(f"ALTER TABLE {self._bronze_table_path} ADD COLUMN {field} STRING")

            # Align stage schema to Delta table schema for append operations
            if self._loadtype == 'append':
                stage = stage.select(
                    *[F.col(field.name).cast(field.dataType) for field in delta_schema.fields]
                )

            print("Schema alignment completed successfully.")
            return stage

        except Exception as e:
            raise Exception(f"Error in _stage_match_to_bronze: {e}")
        

    def put_bronze(self):
        """
        Store the landed data into the designated bronze layer table.

        This function loads the landed data into a Spark DataFrame, processes it, and stores it in the designated bronze layer table.

        Returns:
        - bool: True if the data is successfully stored in the bronze layer table.

        Raises:
        - ValueError: If any errors occur during the data loading process.
        """
        start_time = time.time()
        print(f"Starting put_bronze function at {datetime.now()}. Trying to load the file located at {self._file_path}.")

        # Read and clean the file
        stage = self._read_file()
        stage = self._clean_stage(stage)

        # Check if the table exists
        table_exists = self._spark.catalog.tableExists(self._bronze_table_path)

        if not table_exists:
            # Infer schema and create table if it doesn't exist
            self._infer_table(stage, stage.columns)
            print(f"Table {self._bronze_table_path} created successfully.")
            return self

        # Load Delta table for schema matching and ingestion
        delta_table = DeltaTable.forName(self._spark, self._bronze_table_path)
        stage = self._stage_match_to_bronze(stage, delta_table)

        # Perform ingestion based on load type
        try:
            if self._loadtype == "overwrite":
                print(f"Overwriting {self._bronze_table_path} with new data.")
                stage.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(self._bronze_table_path)

            elif self._loadtype == "append":
                print(f"Appending data to {self._bronze_table_path}.")
                # Write the stage DataFrame in chunks of at most 50K records
                batch_size = 50000
                total_records = stage.count()
                num_batches = (total_records // batch_size) + (1 if total_records % batch_size > 0 else 0)

                for batch_num in range(num_batches):
                    print(f"Writing batch {batch_num + 1} of {num_batches}...")
                    batch = stage.limit(batch_size).subtract(stage.limit(batch_size * batch_num))
                    batch.write.format("delta").mode("append").saveAsTable(self._bronze_table_path)

            elif self._loadtype == "merge":
                print(f"Merging data into {self._bronze_table_path}.")
                # Check if the join columns are provided
                if self._joincolumns is None or not isinstance(self._joincolumns, list):
                    raise ValueError('No parameters added. A Merge load will need to know which values are used as join condition and it should be a list.')
                # Check if the join columns are present in the stage DataFrame and filter out where not null. 
                for join_column in self._joincolumns:
                    stage = stage.withColumn(join_column, F.when(F.col(join_column).isNull(), F.lit('')).otherwise(F.col(join_column)))
                    join_condition = ' AND '.join([f's.{col} = t.{col}' for col in self._joincolumns])
                    delta_table.alias('t').merge(
                        stage.alias('s'),
                        join_condition
                    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

            else:
                raise ValueError(f"Unsupported load type: {self._loadtype}")

            self._log_records_influenced = stage.count()
            print(f"Data ingestion completed successfully for {self._file_name} at {datetime.now()}.")

        except Exception as e:
            raise ValueError(f"Error during data ingestion: {e}")

        self._log_end_time = datetime.now()
        total_time = time.time() - start_time
        print(f"put_bronze function completed at {datetime.now()}. Total runtime: {total_time:.2f} seconds.")
        return self
        

    ################################################################################################
    # Logging functions. Used to keep track of the actions of the class if someone cares for it    #
    ################################################################################################

    def get_log(self):
        return {
            'database':             self._database,
            'bronze_table':         self._bronze_table,
            'catalog':              self._catalog,
            'file_path':            self._file_path,
            'start_time':           self._log_start_time,
            'end_time':             self._log_end_time,
            'files_ingested':       self._log_files_ingested,
            'records_influenced':   self._log_records_influenced
        }

    ################################################################################################
    # Helper functions. Used internally in the class and not designed for calling them externally. #
    ################################################################################################

    def _clean_column_name(self, column_name):
        """
        Cleans a column name by removing special characters and replacing spaces with underscores.

        Args:
        - column_name (str): The original column name to be cleaned.

        Returns:
        - str: The cleaned column name without special characters and with spaces replaced by underscores.
        """
        # Replace percentage signs with "_percentage"
        column_name = column_name.replace('%', '_percentage')

        # Remove special characters and replace spaces with underscores
        try:
            cleaned_name = re.sub(r'\W+', '', column_name.replace(' ', '_')).lower()
        except Exception as e:
            raise ValueError(f"Error cleaning column name: {e}")

        # Prepend 'source_' if the cleaned name is in the protected list
        if cleaned_name in self._delta_columns:
            cleaned_name = f'source_{cleaned_name}'

        # Replace double underscores with a single underscore
        cleaned_name = cleaned_name.replace('__', '_')

        # Drop the last underscore if it exists
        if cleaned_name.endswith('_'):
            cleaned_name = cleaned_name[:-1]

        # Check if the cleaned name is empty
        if len(cleaned_name) == 0:
            raise ValueError(f"Column '{column_name}' is not usable after cleaning.")

        return cleaned_name
  
    def _archive_file(self):
        """
        Archive the file by moving it to the 'Archive' subfolder.

        Returns:
        - str: The path of the archived file.
        """
        try:
            archive_folder = "Archive"
            archive_path = os.path.join(self._file_path, archive_folder)

            # Create the "Archive" subfolder if it doesn't exist
            if not self._dbutils.fs.ls(archive_path):
                self._dbutils.fs.mkdirs(archive_path)

            # Move the file to the "Archive" subfolder
            archive_file_path = os.path.join(archive_path, os.path.basename(self._file_path))
            self._dbutils.fs.mv(self._file_path, archive_file_path)

            return True

        except Exception as e:
            print(f"Error archiving file {self._file_path} to {archive_path}: {str(e)}")
            raise e

    def _clean_filename(self, filename):
        """
        Cleans the filename by removing illegal characters.

        Args:
        - filename (str): The original filename to be cleaned.

        Returns:
        - str: The cleaned filename without illegal characters.
        """
        # Remove illegal characters from the filename
        if filename is not None:
            cleaned_filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        else:
            cleaned_filename = filename

        return cleaned_filename
    
    def _infer_table(self, df, columns):
      """
        Infers the schema from the input DataFrame, creates a temporary view, and uses the inferred schema to create a Delta table.

        Parameters:
        - df (DataFrame): The input DataFrame from which the schema will be inferred.

        Returns:
        - bool: True if the Delta table creation is successful.

        Raises:
        - Exception: If there is an error during the Delta table creation process.
      """
      try:
          # Create a copy of the input DataFrame to modify the schema
          modified_df = df
          try:  # Ensure delta columns are added only once and at the start
            unique_columns = [col for col in columns if col not in self._delta_columns]
            modified_df = modified_df.select(*self._delta_columns + unique_columns)
            print(f"Columns reordered successfully at {datetime.now()}.")
          except Exception as e:
            raise Exception(f'Failed to reshuffle the order: {e}')
          
          # Infer the schema from the modified DataFrame
          modified_df.createOrReplaceTempView("temp_view")

          # Create Delta table with the inferred schema
          sqlcode = f"""
            CREATE TABLE {self._bronze_table_path} 
            USING DELTA 
            OPTIONS (header=true) 
            COMMENT 'Table created using the GDMO Landing class based off the schema of {self._file_name}' 
            AS SELECT * FROM temp_view
          """
          print(f'Trying to create the inferred delta table: {sqlcode}')
          self._spark.sql(sqlcode)                
          print(f"Table created successfully at {datetime.now()}.")

          return True

      except Exception as e:
          raise Exception(f"Delta table creation failed with Error: {e}")

    def _device_flow_session(self):
        """
        Helper function to set up authentication against SharePoint Online using device flow.

        Returns:
        - requests.Session: Session object with authentication headers set for SharePoint API calls.
        """
        # Check if all required parameters for token acquisition are populated
        if not all([self._sharepoint_uri, self._sharepoint_user, self._sharepoint_pass, self._sharepoint_client_id]):
            raise ValueError("Missing required parameters for token acquisition. Please ensure all SharePoint authentication parameters are provided.")

        try:
            authority_url = 'https://login.microsoftonline.com/common'
            ctx = AuthenticationContext(authority_url, api_version='v2.0')
            tresult = ctx.acquire_token_with_username_password(self._sharepoint_uri, self._sharepoint_user, self._sharepoint_pass, self._sharepoint_client_id)

            session = requests.Session()
            session.headers.update({'Authorization': f'Bearer {tresult["accessToken"]}',
                                    'SdkVersion':   'sample-python-adal',
                                    'x-client-SKU': 'sample-python-adal'})

            self._sharepoint_session = session

            return session

        except Exception as e:
            print(f"Error setting up authentication session to {self._sharepoint_uri}: {e}")
            raise e
    
    def _sharepoint_apicall(self, filename=None):
        """
        Make an API call to retrieve files from a SharePoint folder.

        Parameters:
        - filename (str): The name of the file to retrieve. If specified, the API call will target that specific file.

        Returns:
        - requests.Response: The response object from the API call.
        """
        try:
            if self._sharepoint_session is None:
                graph_session = self._device_flow_session()
            else:
                graph_session = self._sharepoint_session

            folder = '/'.join([stuff for stuff in self._sharepoint_folder.split("/") if stuff not in re.sub(r'^.*?.com', '', self._sharepoint_uri).split("/")]) + '/'

            api_call = f"{self._sharepoint_uri}sites/{self._sharepoint_site}/_api/web/GetFolderByServerRelativeUrl('{folder}')/Files"

            if filename is not None:
                api_call += f"('{filename}')/$value"

            response = graph_session.get(api_call, headers={'Accept': 'application/json;odata=verbose'})

            response.raise_for_status()  # Raise an HTTPError for bad responses

            return response

        except requests.exceptions.RequestException as e:
            print(f"Error making SharePoint API call: {e}")
            raise e
