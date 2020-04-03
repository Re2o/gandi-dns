# Re2o Gandi DNS

This is a small script that can be the interface between Re2o and Gandi for the DNS.
So far it manages:

* A records
* AAAA records
* CNAME records
* Origin record

more can be added but I did not need them.

The script keeps track of the records it can manage in toml files in `last_updates`, so that it won't delete records that you add manually in Gandi interface if they don't exist in Re2o.

## Usage

```
Usage: main.py [OPTIONS]

Options:
  --config-dir TEXT       Configuration directory.
  --dry-run / --complete  Performs a dry run.
  --keep / --update       Update service status on Re2o. Won't update if it is
                          a dry-run.

  --help                  Show this message and exit.

```

## Installation

Clone the repository (e.g. in `/usr/local/dns`) the install the requirements (with pip for example : `pip install -r requirements.txt`) and it's done.

You can also setup a cron to run this on a regular basis. 
