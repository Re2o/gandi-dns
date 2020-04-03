import logging
import logging.config
import pathlib
import traceback

import click
import toml

from re2oapi import Re2oAPIClient
from gandi import GandiAPIClient, DomainsRecords, Record

RUN_PATH = pathlib.Path(__file__).parent


def process_zone(zone, domains_records, logger):
    pass


@click.command()
@click.option(
    "--config-dir", default=RUN_PATH.resolve(), help="Configuration directory."
)
@click.option("--dry-run/--complete", default=False, help="Performs a dry run.")
def main(config_dir, dry_run):
    logging.config.fileConfig(config_dir / "logging.conf")
    logger = logging.getLogger("dns")
    logger.debug("Fetching configuration from %s.", config_dir)
    config = toml.load(config_dir / "config.toml")
    re2o_client = Re2oAPIClient(
        config["Re2o"]["hostname"],
        config["Re2o"]["username"],
        config["Re2o"]["password"],
        use_tls=config["Re2o"]["use_TLS"],
    )
    zones = re2o_client.list("dns/zones")

    default_API_key = config["Gandi"]["API_KEY"]

    for zone in zones:
        # Re2o has zones names begining with '.'. It is a bit difficult to translate
        # that into toml
        name = zone["name"][1:]
        try:
            configured_zone = config["Gandi"]["zone"][name]
        except KeyError as e:
            logger.error("Could not find zone named %s in configuration.", e)
            continue

        key = configured_zone.get("API_KEY", default_API_key)
        gandi_client = GandiAPIClient(key)

        logger.info("Fetching last update for zone %s.", name)
        last_update_file = config_dir / "last_update_{}.toml".format(name)
        last_update_file.touch(mode=0o644, exist_ok=True)
        last_update = DomainsRecords(gandi_client, name, fetch=False)
        try:
            last_update.from_dict(toml.load(last_update_file))
        except Exception as e:
           logger.warning("Could not retrieve last update.")
           logger.debug(e)
        logger.info("Fetching current records for zone %s.", name)
        current_records = DomainsRecords(gandi_client, name)
        logger.info("Fetching re2o records for zone %s.", name)
        new_records = set()

        if zone["originv4"]:
            new_records.add(
                Record(
                    gandi_client,
                    name,
                    rrset_name="@",
                    rrset_type=Record.Types.A,
                    rrset_values=[zone["originv4"]["ipv4"]],
                )
            )

        if zone["originv6"]:
            new_records.add(
                Record(
                    gandi_client,
                    name,
                    rrset_name="@",
                    rrset_type=Record.Types.AAAA,
                    rrset_values=[zone["originv6"]],
                )
            )

        for a_record in zone["a_records"]:
            new_records.add(
                Record(
                    gandi_client,
                    name,
                    rrset_name=a_record["hostname"],
                    rrset_type=Record.Types.A,
                    rrset_values=[a_record["ipv4"]],
                )
            )

        for aaaa_record in zone["aaaa_records"]:
            logger.debug("aaaa records %r", aaaa_record)
            new_records.add(
                Record(
                    gandi_client,
                    name,
                    rrset_name=aaaa_record["hostname"],
                    rrset_type=Record.Types.AAAA,
                    rrset_values=[ipv6["ipv6"] for ipv6 in aaaa_record["ipv6"]],
                )
            )

        for cname_record in zone["cname_records"]:
            new_records.add(
                Record(
                    gandi_client,
                    name,
                    rrset_name=cname_record["hostname"],
                    rrset_type=Record.Types.CNAME,
                    # The dot is to conform with Gandi API
                    rrset_values=[cname_record["alias"]+'.'],
                )
            )

        # Delete records added by this script that are not in new_records.
        to_be_deleted = set(last_update.records) & (
            set(current_records.records) - set(new_records)
        )
        # Add records that are in new_records except if they are already there.
        to_be_added = set(new_records) - set(current_records.records)
        logger.debug("Re2o records are %r", new_records)
        logger.debug("I will add : %r", to_be_added)
        logger.debug("I will delete : %r", to_be_deleted)

        if not dry_run:
            saved = []
            for r in to_be_deleted:
                logger.info("Deleting record %r for zone %s.", r, name)
                try:
                    r.delete()
                except requests.exceptions.HTTPError as e:
                    logger.error("Failed to delete %r for zone %s: %s", r, name, e)
                    saved.append(r)

            for r in to_be_added:
                logger.info("Adding record %r for zone %s.", r, name)
                try:
                    r.save()
                    saved.append(r)
                except requests.exceptions.HTTPError as e:
                    logger.error("Failed to add %r for zone %s: %s", r, name, e)
            logger.debug("Saving update for zone %s.", name)
            with last_update_file.open("w") as f:
                toml.dump({"records": [r.as_dict() for r in saved]}, f)
        else:
            logger.info("This is a dry run for zone %s.", name)
            logger.info("Records to be deleted : %r", to_be_deleted)
            logger.info("Records to be added : %r", to_be_added)


if __name__ == "__main__":
    main()
