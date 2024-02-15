import csv
import os
from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from .data_handler import Conversation, DataHandler, SearchHistory

INMEMORY_DATA_MANAGER = DataHandler()


def add_period(date, period):
    if period == "weekly":
        return date + relativedelta(weeks=1)
    elif period == "monthly":
        return date + relativedelta(months=1)
    elif period == "annually":
        return date + relativedelta(years=1)
    else:
        return date


def _get_files_path(dir_path):
    csv_paths = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".csv"):
                csv_paths.append(os.path.join(root, file))
    return csv_paths


def _load_file(file_path, file_type):
    data = defaultdict(list)
    participants = set()
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        if file_type == "conversations":
            for row in reader:
                participants.add(row["sender_name"])
                data[row["date"]].append(
                    {
                        "sender_name": row["sender_name"],
                        "content": row["content"],
                        "time": row["time"],
                    }
                )
            return [
                Conversation(date, messages, list(participants))
                for date, messages in data.items()
            ]
        if file_type == "searches":
            # extract date from file name
            date = os.path.splitext(os.path.basename(file_path))[0]
            for row in reader:
                data[date].append({"hour": row["hour"], "title": row["title"]})
            return [SearchHistory(date, searches) for date, searches in data.items()]
        return []


def _load_content(dir_path, data_type):
    """
    It loads Conversation-type and HistorySearch-type items into the data manager.
    """
    files_path = _get_files_path(dir_path)

    for file_path in files_path:
        file_data = _load_file(file_path, data_type)
        for item in file_data:
            INMEMORY_DATA_MANAGER.add_data_item(item, data_type)


def load_data(dir_path, data_type):
    _load_content(dir_path, data_type)
    return INMEMORY_DATA_MANAGER.get_data(data_type)


def load_data_per_date_range(dir_path, start_date, end_date, data_type):
    _load_content(dir_path, data_type)
    return INMEMORY_DATA_MANAGER.get_data_by_date_range(start_date, end_date, data_type)


def extract_data_per_period(data, start_date, end_date):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    if not data:
        return []

    if isinstance(data[0], Conversation):
        return [conv for conv in data if start_datetime <= conv.date <= end_datetime]
    if isinstance(data[0], SearchHistory):
        return [hist for hist in data if start_datetime <= hist.date <= end_datetime]


def date_to_str(date: datetime):
    return datetime.strftime(date, "%Y-%m-%d")


def format_as_str(raw_data):
    str_data = []
    if raw_data:
        if isinstance(raw_data[0], Conversation):
            for conversation in raw_data:
                conversation_str = (
                    f"Chat between {conversation.participants} on "
                    f"{date_to_str(conversation.date)}\n"
                )
                for message in conversation.messages:
                    conversation_str += (
                        f"{message['time']}: "
                        f"{message['sender_name']}: {message['content']} \n"
                    )
                str_data.append(conversation_str)

        if isinstance(raw_data[0], SearchHistory):
            for search_history in raw_data:
                searches_str = f"On {date_to_str(search_history.date)}, user:"
                for search in search_history.searches:
                    searches_str += f"{search['title']} at {search['hour']} \n"
                str_data.append(searches_str)
    return str_data
