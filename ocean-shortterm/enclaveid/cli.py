import getpass
import json
import logging
import os

import click
import utils.data as data_tools
from core import Enclaveid
from dotenv import find_dotenv, load_dotenv
from utils.generic import _calculate_scores_average as get_average_score
from utils.generic import save_json

SUPPORTED_PERIODS = ["weekly", "monthly", "annually", "lifetime"]
SUPPORTED_TYPES = ["conversations", "searches"]
DEFAULT_SAVE_PATH = os.path.join(os.getcwd(), "enclaveid_llm_output")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run(
    dir_path: str,
    period: str,
    data_type: str,
    start_date: str = "",
    end_date: str = "",
    save_path: str = DEFAULT_SAVE_PATH,
):
    """
    scores OCEAN traits for the specified period. Then it average those
    scores to obtain a final one that represents all the data used.

    Returns:
        final_score: The average score calculated from all scores generated
               over the periods.
    """

    if period not in SUPPORTED_PERIODS:
        raise ValueError(
            f"Period {period} is not supported. We support {SUPPORTED_PERIODS}."
        )

    if data_type not in SUPPORTED_TYPES:
        raise ValueError(
            f"Data type {data_type} is not supported. We support {SUPPORTED_TYPES}."
        )

    saved_latest_score = None
    enclaveid_instance = Enclaveid()

    save_path = os.path.join(save_path, data_type, period)

    if os.path.exists(save_path):
        # extract the latest saved score, if any
        final_score_path = os.path.join(save_path, "latest.json")
        if os.path.exists(final_score_path):
            with open(final_score_path, "r") as json_file:
                saved_latest_score = json.load(json_file)
    else:
        os.makedirs(save_path)

    data, data_start_date, data_end_date = data_tools.load_data(dir_path, data_type)

    logger.info(
        f"The data in the data directory provided has as the oldest date: "
        f"{data_start_date} and as the newest date: {data_end_date}. In total "
        f"we loaded {len(data)} data items."
    )

    if start_date:
        data_start_date = start_date
    if end_date:
        data_end_date = end_date

    if data_start_date > data_end_date:
        raise ValueError("Start date must be before end data.")

    total_data_items = 0

    if period == "lifetime":
        # Process lifetime data
        logger.info(
            f"Processing {len(data)} data items corresponding to the period "
            f"from {data_start_date} to {data_end_date}"
        )
        period_id = (
            f"{data_tools.date_to_str(data_start_date)}-"
            f"TO-{data_tools.date_to_str(data_end_date)}"
        )

        final_score, final_cost = enclaveid_instance.score(
            data, data_type, save_path=save_path, period_id=period_id
        )
        total_data_items = len(data)
        logger.info(f"Obtained score: {final_score}")

        # save period score
        int_save_path = os.path.join(save_path, f"{period_id}.json")
        save_json(int_save_path, final_score)
    else:
        logger.info(
            f"Using data from {data_start_date} to {data_end_date} on a {period} basis."
        )
        scores = []
        costs = []
        while data_start_date < data_end_date:
            current_period_end = data_tools.add_period(data_start_date, period)

            # Use overall end date if we exceed it
            if current_period_end > data_end_date:
                current_period_end = data_end_date

            start_date = data_tools.date_to_str(data_start_date)
            end_date = data_tools.date_to_str(current_period_end)

            # Extract data corresponding to this period
            period_data = data_tools.extract_data_per_period(data, start_date, end_date)

            # Process period data
            if period_data:
                period_id = f"{start_date}-TO-{end_date}"

                logger.info(
                    f"Processing {len(period_data)} data items corresponding "
                    f"to the period from {start_date} to {end_date}"
                )
                score, cost = enclaveid_instance.score(
                    period_data, data_type, save_path=save_path, period_id=period_id
                )
                logger.info(f"Obtained score: {score}")
                scores.append(score)
                costs.append(cost)

                # save period score
                int_save_path = os.path.join(save_path, f"{period_id}.json")
                save_json(int_save_path, score)

                # update starting date
                data_start_date = current_period_end
                total_data_items += len(period_data)

            else:
                logger.info(
                    f"No data to process for the period from {start_date} to {end_date}"
                )
                data_start_date = current_period_end
                total_data_items += len(period_data)
                continue

        # average all scores
        final_score = get_average_score(scores)
        final_cost = sum(costs)

    logger.info(f"Processed {total_data_items} items of data in total.")
    logger.info(
        f"Final score: {final_score} for the period from {data_start_date} "
        f"to {data_end_date}."
    )
    logger.info(f"Total cost: {final_cost} USD.")

    # save as the new overall score
    file_save_path = os.path.join(save_path, "latest.json")

    if saved_latest_score:
        latest_score = get_average_score([final_score, saved_latest_score])
        logger.info(
            f"Updating latest saved scores result from {saved_latest_score} "
            f"to {latest_score}"
        )
        final_score = latest_score
    else:
        logger.info(
            f"Not saved scores found. Saving final score {final_score} as "
            f"the overall score in {file_save_path}"
        )

    save_json(file_save_path, final_score)
    return final_score


@click.command()
@click.option(
    "-d",
    "--dir-path",
    "dir_path",
    required=True,
    help="Directory path where the data CSV files are located.",
)
@click.option(
    "-p",
    "--period",
    "period",
    required=True,
    help="Period for which you want to score. Examples: weekly, monthly, annually.",
)
@click.option(
    "-t", "--type", "data_type", required=True, help="'conversations' or 'searches'"
)
@click.option(
    "-sd",
    "--start-date",
    "start_date",
    required=False,
    help="Start date for the period in the format YYYY-MM-DD.",
)
@click.option(
    "-ed",
    "--end-date",
    "end_date",
    required=False,
    help="End date for the period in the format YYYY-MM-DD.",
)
@click.option(
    "--save_path",
    "save_path",
    required=False,
    help=f"Path to save files generated by the program. Default: {DEFAULT_SAVE_PATH}",
    default=DEFAULT_SAVE_PATH,
)
def main(
    dir_path: str,
    period: str,
    data_type: str,
    start_date: str = "",
    end_date: str = "",
    save_path: str = DEFAULT_SAVE_PATH,
):
    load_dotenv(find_dotenv(usecwd=True))

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass(
            prompt="Enter your OpenAI API key: "
        )

    final_score = run(
        dir_path,
        period.lower(),
        data_type.lower(),
        start_date=start_date,
        end_date=end_date,
        save_path=save_path,
    )
    print(final_score)


if __name__ == "__main__":
    main()
