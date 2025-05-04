# Simple BCP

A Simple yet powerful Python bcp wrapper.  
`bcp` (**b**ulk **c**opy **p**rogram) is a command line tool that copies data from / into  MSSQL.  
You can read more about bcp [here](https://learn.microsoft.com/en-us/sql/tools/bcp-utility)

## Installation

Install the package using pip:

```bash
pip install simple_bcp
```

## Usage

```python
import simple_bcp

bcp = simple_bcp.BCP()
database_parameters = simple_bcp.MsSqlDatabaseParameters(
    server_hostname="your-sql-server-hostname",
    username="user",
    password="pass"
)
output_file_path = bcp.download_table(table_name="your_table_name", 
                                      database_parameters=database_parameters)
print("downloaded table data is now available at ", output_file_path)
bcp.upload_into_table(table_name="dest_table_name",
                      database_parameters=database_parameters,
                      data_file_path=output_file_path)
print("the data is now copied to dest_table_name")
```

## Requirements

- Python >= 3.10
- `bcp` installed on your machine. [How to install bcp](https://learn.microsoft.com/en-us/sql/tools/bcp-utility#download-the-latest-version-of-the-bcp-utility)

## Repo & Author

Developed by [Noam Fisher](https://gitlab.com/noamfisher),
You can see the project in https://gitlab.com/noamfisher/simple_bcp
