from datetime import datetime

from sortedcontainers import SortedList


class Conversation:
    """
    It creates an object of type Conversation that have the properties
    date and message. Each message has the property sender_name, content, and time.
    """

    def __init__(self, date, messages, participants):
        self.date = datetime.strptime(date, "%Y-%m-%d")
        self.messages = messages
        self.participants = participants

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return (
            f"Conversation(date='{self.date}', "
            f"messages={self.messages}, "
            f"participants={self.participants})"
        )


class SearchHistory:
    """
    It creates an object of type SearchHistory that have the properties
    date and searches. Each search has the property hout and title.
    """

    def __init__(self, date, searches):
        self.date = datetime.strptime(date, "%Y-%m-%d")
        self.searches = searches

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return f"SearchHistory(date='{self.date}', searches={self.searches})"


class DataHandler:
    """
    It handles the addition of conversations and/or search history. It also
    allows to retrieve the information.
    """

    def __init__(self):
        self.conversations = SortedList()
        self.search_history = SortedList()

    def add_data_item(self, item, data_type):
        if data_type == "conversations":
            self.conversations.add(item)
        elif data_type == "searches":
            self.search_history.add(item)
        else:
            raise ValueError(f"Data type '{data_type}' not supported.")

    def get_data_by_type(self, data_type):
        if data_type == "conversations":
            return self.conversations
        elif data_type == "searches":
            return self.search_history
        else:
            raise ValueError(f"Data type '{data_type}' not supported.")

    def get_data(self, data_type):
        data = self.get_data_by_type(data_type)
        if not data:
            return [], None, None

        oldest_date = data[0].date
        newest_date = data[-1].date

        return data, oldest_date, newest_date

    def get_data_by_date_range(self, start_date, end_date, data_type):
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        data = self.get_data_by_type(data_type)
        return [item for item in data if start_datetime <= data.date <= end_datetime]
