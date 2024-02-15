import json
import logging
import os

import json_repair
import tiktoken
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from .templates import (
    CLASSIFICATION_TEMPLATE_CONV,
    CLASSIFICATION_TEMPLATE_SRCH,
    SCORE_TEMPLATE,
)

TRAIT_MARKERS_PATH = os.path.join(os.getcwd(), "assets/markers.json")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# disable requests default logging inherent from langchain
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


def calculate_cost(token_data: int):
    """
    Calculates the cost according to the number of tokens used.
    Pricing as of Dec 16th, 2023: https://openai.com/pricing

    Args:
        token_data (int): The number of tokens used.

    Returns:
        cost (float): The total cost in USD, rounded to four decimal places.
    """
    cost = 0
    if "gpt-3.5" in token_data:
        gpt_3_cost = (token_data["gpt-3.5"][0] / 1000 * 0.0010) + (
            token_data["gpt-3.5"][1] / 1000 * 0.0020
        )
        cost += gpt_3_cost

    if "gpt-4" in token_data:
        gpt_4_cost = (token_data["gpt-4"][0] / 1000 * 0.03) + (
            token_data["gpt-4"][1] / 1000 * 0.06
        )
        cost += gpt_4_cost

    return round(cost, 4)


def _get_number_of_tokens(text: str):
    """
    Counts the number of tokens in the input text.

    Args:
        text (str): The input text to be tokenized.

    Returns:
        int: The number of tokens in the text.
    """
    tokens = tiktoken.get_encoding("cl100k_base").encode(text)
    return len(tokens)


def _split_string(item: str, max_chars: int):
    """
    Splits a large string into smaller segments, ensuring each segment's length
    does not exceed max_chars. The string is divided at the first line break
    encountered, starting from the cut position and moving backwards.

    Args:
        item (str): The input text to be split.
        max_chars (int): The maximum number of characters allowed in each segment.

    Returns:
        pieces (list): A list of strings, each with a length less than or equal
        to max_chars. These segments reconstitute the original item string.
    """
    pieces = []
    while len(item) > max_chars:
        cut_position = item.rfind("\n", 0, max_chars)
        if cut_position == -1:
            cut_position = max_chars // 2
        pieces.append(item[:cut_position])
        item = item[cut_position:].lstrip()
    pieces.append(item)
    return pieces


def split(data: list, max_tokens: int = 2048, margin_error: int = 50):
    """
    Splits data items that are too large into smaller items suitable for processing
    by an LLM.

    Args:
        data (list): A list of data items, where each item is a string.
        max_tokens (int): The maximum number of tokens that the LLM can support.
        margin_error (int): The allowable range of tokens, above or below the maximum.

    Returns:
        items (list): A list of data items, each conforming to the maximum tokens thres.
    """

    items = []
    for item in data:
        tokens = _get_number_of_tokens(item)
        # if the item is sufficiently short, we accept it as it is.
        if tokens <= max_tokens:
            items.append(item)
        # Otherwise, if the item is too large, we split it into smaller pieces.
        else:
            approx_max_chars = (max_tokens * len(item) // tokens) - margin_error
            item_pieces = _split_string(item, approx_max_chars)
            items.extend(item_pieces)
    return items


def generate_chunks(data: list, max_tokens: int = 2048):
    """
    Concatenates data items into chunks, with each chunk being as close as possible to a
    specified maximum number of tokens.

    Args:
        data (list): A list of data items, where each data item is a string.
        max_tokens (int): The desired maximum number of tokens for each chunk.

    Returns:
        chunks (list): A list of chunks, each a string sized up to the maximum token
            limit.
    """
    chunks = []
    chunk = ""
    used_tokens = 0

    for item in data:
        item_tokens = _get_number_of_tokens(item)
        if used_tokens + item_tokens > max_tokens:
            # Start a new chunk only if the current chunk is closer to
            # max_tokens without the item
            if abs(max_tokens - used_tokens) < abs(
                max_tokens - (used_tokens + item_tokens)
            ):
                chunks.append(chunk)
                chunk = item
                used_tokens = item_tokens
            else:
                chunk += " " + item
                used_tokens += item_tokens
        else:
            chunk += " " + item if chunk else item
            used_tokens += item_tokens

    # Add the last chunk if it's not empty
    if chunk:
        chunks.append(chunk)

    return chunks


def remove_low_classified_chunks(labels: list):
    """
    Removes chunks that do not have any trait labeled with a high signal.

    Args:
        labels (list): A list of dictionaries, each with the key "labels" indicating
            the signal strength of each OCEAN trait as high, medium, low, or none.

    Returns:
        high_labeled_items (list): A list of dictionaries where each contains at
            least one "high" label."""
    high_labeled_items = []
    for item in labels:
        for _, label in item["labels"].items():
            if label.lower() == "high":
                high_labeled_items.append(item)
                break
    return high_labeled_items


def classify(chunks: list, mode: str):
    """
    Classifies each conversation or search history with signals of the five OCEAN
    traits as high, medium, low, or none, using OpenAI's LLM.

    Args:
        chunks (list): A list of strings representing either conversations or search
            history.
        mode (str): A string defining the data type "conversations" or "searches".

    Returns:
        classified_items (list): A list of dictionaries, each containing the chunk text
        and its corresponding OCEAN traits labels.
        input_tokens (int): The number of tokens sent to the LLM.
        output_tokens (int): The number of tokens in the output from the LLM.
    """
    classification_prompt = PromptTemplate(
        input_variables=["markers", "text"],
        template=CLASSIFICATION_TEMPLATE_CONV
        if mode == "conversations"
        else CLASSIFICATION_TEMPLATE_SRCH,
    )

    chain = LLMChain(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo-1106"), prompt=classification_prompt
    )

    with open(TRAIT_MARKERS_PATH, "r") as json_file:
        markers = json.load(json_file)

    classified_items = []
    input_tokens = 0
    output_tokens = 0

    for chunk in chunks:
        input_text = str(
            classification_prompt.format(markers=markers[mode], text=chunk)
        )
        input_tokens += _get_number_of_tokens(input_text)

        output_text = chain.run({"markers": markers[mode], "text": chunk})
        output_tokens += _get_number_of_tokens(output_text)

        labels = _extract_json(output_text)

        if labels:
            gpt_reasoning_explanation = labels.pop("explanation")
            logging.info(f"Classifying text: {chunk}")
            logging.info(f"LLM reasoning: {gpt_reasoning_explanation}")

            classified_items.append({"text": chunk, "labels": labels})

    return classified_items, input_tokens, output_tokens


def _extract_json(gpt_answer: str):
    """
    Extracts the latest JSON data from a string response and the remaining text.

    Args:
        gpt_answer(str): String that contains the JSON data.

    Returns:
        json_response(dict): The extracted JSON with the remaining text.
    """
    text = gpt_answer.replace("\\n", "\n")
    start_index = text.rfind("{")
    end_index = text.rfind("}")

    if start_index != -1 and end_index != -1 and start_index < end_index:
        json_text = text[start_index : end_index + 1]
        try:
            json_response = json_repair.loads(json_text)
        except json.JSONDecodeError:
            logger.info(f"Invalid answer format: {gpt_answer}")
            return {}

        json_response["explanation"] = text.strip()
        return json_response
    else:
        logger.info(f"Answer does not include a JSON object: {gpt_answer}")
        return {}


def _calculate_scores_average(scores_list: list):
    """
    Calculates the scores average from a scores list

    Args:
        scores_list(list): a list of dictionaries containing the trait scores

    Returns:
        averages(dict): a single score dictionary with the averaged scores
    """
    sums = {key: 0 for key in scores_list[0]}

    for item in scores_list:
        for key in item:
            sums[key] += float(item[key])

    averages = {key: round(total / len(scores_list), 2) for key, total in sums.items()}
    return averages


def score_items(items: list):
    """
    Scores the OCEAN traits on a scale from 0 to 1 for each given chunk of data.

    Args:
        items (list): A list of chunks to be scored.

    Returns:
        final_score (dict): A dictionary containing the scores for each of the five
            OCEAN traits.
        input_tokens (int): The number of tokens sent to the LLM.
        output_tokens (int): The number of tokens in the output from the LLM.
    """
    input_tokens = 0
    output_tokens = 0

    score_prompt = PromptTemplate(
        input_variables=["text", "labels"],
        template=SCORE_TEMPLATE,
    )

    chain = LLMChain(llm=ChatOpenAI(model_name="gpt-4"), prompt=score_prompt)

    if not items:
        return (
            {
                "openness": 0.5,
                "conscientiousness": 0.5,
                "extraversion": 0.5,
                "agreeableness": 0.5,
                "neuroticism": 0.5,
            },
            0,
            0,
        )

    scores_per_range = []
    for item in items:
        _input_text = str(score_prompt.format(text=item["text"], labels=item["labels"]))
        input_tokens += _get_number_of_tokens(_input_text)

        score = chain.run({"text": item["text"], "labels": item["labels"]})

        output_tokens += _get_number_of_tokens(score)
        score = _extract_json(score)

        if score:
            gpt_reasoning_explanation = score.pop("explanation")
            logging.info(
                f"Classifying text: {item['text']} with labels {item['labels']}"
            )
            logging.info(f"LLM reasoning: {gpt_reasoning_explanation}")

            scores_per_range.append(score)

    if len(scores_per_range) == 1:
        return scores_per_range[0], input_tokens, output_tokens

    final_score = _calculate_scores_average(scores_per_range)
    return final_score, input_tokens, output_tokens


def save_json(save_path: str, information: dict):
    """
    Save data as a JSON file.

    Args:
        save_path: path to save the file
        information: dictionary with the content to save
    """
    with open(save_path, "w") as json_file:
        json.dump(information, json_file, indent=4)
