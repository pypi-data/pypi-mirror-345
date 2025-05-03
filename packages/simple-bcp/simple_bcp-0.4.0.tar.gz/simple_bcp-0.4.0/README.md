# Simple BCP

A Simple yet powerful Python bcp wrapper.  
`bcp` (**b**ulk **c**opy **p**rogram) is a command line tool that copies data from / into  MSSQL.  
You can read more about bcp [here](https://learn.microsoft.com/en-us/sql/tools/bcp-utility)

## Installation

You can install the package using pip:

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
output_file_path = bcp.download_table(table_name="your_table_name", database_parameters=database_parameters)
print("table data is available at ", output_file_path)
```

## Requirements

- Python >= 3.10
- `bcp` installed on your machine. [How to install bcp](https://learn.microsoft.com/en-us/sql/tools/bcp-utility#download-the-latest-version-of-the-bcp-utility)

## Author

[Noam Fisher](https://gitlab.com/noamfisher)
