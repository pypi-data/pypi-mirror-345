# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "shipyard-bigquery",
#     "shipyard-templates"
# ]
# ///
import os
import sys
from shipyard_bigquery import BigQueryClient
from shipyard_templates import ShipyardLogger

logger = ShipyardLogger.get_logger()


def main():

    try:
        sys.exit(
            BigQueryClient(
                service_account=os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            ).connect()
        )
    except Exception as e:
        logger.error(f"Could not connect to BigQuery: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
