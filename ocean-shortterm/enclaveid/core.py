import logging
import os

import utils.data as data_tools
import utils.generic as tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Enclaveid:
    """
    This class implements the pipeline to score Conversation or HistorySearch data.
    """

    def __init__(self, max_input_tokens=3076):
        self.max_input_tokens = max_input_tokens

    def score(self, data: list, mode: str, save_path: str, period_id: str):
        """scores the provided data based on OCEAN personality traits.

        Args:
            data (list): A list of objects, either of Conversation type or
                         HistorySearch type.
            mode (str): Specifies the type of data being scored, either
                        "conversations" or "searches".
            save_path (str): path to save intermediate files.
            period_id (str): period identifier to name intermediate files.

        Returns:
            score (dict): A dictionary containing the OCEAN traits scores for
                          the provided data.
            cost (float): The cost in USD of generating the scores dict using
                          OpenAI's models.
        """
        used_tokens = {}

        # return default scores in case we do not have data to process
        if not data:
            raise TypeError(f"Not data provided to score. period_id {period_id}")

        # The data data is initially sorted by date. To improve data processing for,
        # conversations we aim to re-sort the data by participants. This ensures
        # consistency in the data when inputting it into the classification and
        # score models. For searches, we do not care about re-sorting
        if mode == "conversations":
            data = sorted(data, key=lambda conv: ",".join(sorted(conv.participants)))

        # Transform the data into strings while retaining only the relevant fields.
        # For example, for Conversations, we keep only the sender's name and the
        # message whereas in search history, we only keep the search title.
        data = data_tools.format_as_str(data)
        data_size = len(data)

        # Each data item comprises a set of searches or messages. Some of these
        # sets can be quite large, so we split them into smaller subsets.
        logger.info("Split large data items into smaller items")
        data = tools.split(data, max_tokens=self.max_input_tokens)
        logger.info(
            f"Went from {data_size} items to {len(data)} items. All of them "
            f"below a maximum token theshold of {self.max_input_tokens}"
        )
        data_size = len(data)

        # A data item can be as brief as a single message or search title. However, we
        # do not want to classify each data item separately, as the context may be
        # insufficient for an accurate classification. Therefore, we concatenate data
        # items into the largest possible string that fits within the context window
        # of a maximum reserved number of tokens.
        chunks = tools.generate_chunks(data, self.max_input_tokens)
        logger.info(
            f"We compressed {data_size} data items into {len(chunks)} chunks "
            f"of data with a maximum size of {self.max_input_tokens} tokens."
        )

        # Classify each chunk of data by its OCEAN trait signals
        logger.info(f"Classify {len(chunks)} total chunks of data")
        classified_chunks, in_tokens, out_tokens = tools.classify(chunks, mode=mode)
        used_tokens["gpt-3.5"] = [in_tokens, out_tokens]
        tools.save_json(
            os.path.join(save_path, f"{period_id}_classification_results.json"),
            classified_chunks,
        )

        # Remove low classified signals
        logger.info("Remove low classified chunks")
        chunks = tools.remove_low_classified_chunks(classified_chunks)
        logger.info(
            f"Only {len(chunks)} out of {len(classified_chunks)} "
            "chunks have at least one trait classified as high."
        )

        # Score the high-classified chunks
        logger.info(f"Scoring a total of {len(chunks)} chunks.")
        score, in_tokens, out_tokens = tools.score_items(chunks)
        used_tokens["gpt-4"] = [in_tokens, out_tokens]

        # Calculating the cost
        cost = tools.calculate_cost(used_tokens)

        return score, cost

    def alternative_score(self, data: list, mode: str):
        # TODO: implement alternative version for testing
        pass
