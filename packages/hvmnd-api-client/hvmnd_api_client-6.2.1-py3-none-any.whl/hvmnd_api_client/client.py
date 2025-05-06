import os
import hashlib
import logging
import datetime
import requests


class InvalidPlatformException(BaseException):
    def __init__(self):
        pass


class APIClient:
    """
    A client for interacting with the hvmnd-api.
    """

    def __init__(self, base_url: str, api_token: str):
        """
        Initialize the API client.

        Args:
            base_url (str): The base URL of the API (e.g., 'http://localhost:8080').
            api_token (str): hvmnd-api API token.
        """
        self.base_url = base_url.rstrip('/')
        self.token = api_token or os.getenv('HVMND_API_TOKEN', '')
        if not self.token:
            raise ValueError("api_token is required (argument or HVMND_API_TOKEN env)")
        self.logger = logging.getLogger("hvmnd_api_client")
        self.available_platforms = ["telegram", "webapp"]

    def get_nodes(
            self,
            id_: int = None,
            renter: int = None,
            status: str = None,
            any_desk_address: str = None,
            software: str = None,
            machine_id: str = None
    ):
        """
        Retrieve nodes based on provided filters.

        Args:
            id_ (int, optional): Node ID.
            renter (int, optional): Renter ID. If 'non_null', returns nodes with a non-null renter.
            status (str, optional): Node status.
            any_desk_address (str, optional): AnyDesk address.
            software (str, optional): Software name to filter nodes that have it installed.
            machine_id (str, optional): Machine ID or local socket name on node

        Returns:
            dict: Parsed response containing a list of nodes or an error.
        """
        url = f"{self.base_url}/telegram/nodes"
        params = {
            'id': id_,
            'renter': renter,
            'status': status,
            'any_desk_address': any_desk_address,
            'machine_id': machine_id,
            'software': software,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        response = self._handle_response(
            requests.get(url, params=params, headers={"Authorization": f"Bearer {self.token}"})
        )

        return response

    def update_node(self, node: dict):
        """
        Update a node.

        Args:
            node (dict): Node data to update. Must include 'id' or a unique identifier
                         for the node (see your API docs for specifics).

        Returns:
            dict: The parsed response containing updated node data or an error.
        """
        url = f"{self.base_url}/telegram/nodes"

        params = {k: v for k, v in node.items() if v is not None}

        response = requests.patch(url, json=params, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def create_node(self, any_desk_address: str, any_desk_password: str, status: str, machine_id: str):
        """
        Create a new node. Use in hvmnd-node-service to initialize new nodes.

        Args:
            any_desk_address (str): The AnyDesk address for the node.
            any_desk_password (str): The AnyDesk password for the node.
            status (str): The status of the node (e.g., 'available').
            machine_id (str): The machine ID of the node.

        Returns:
            dict: The parsed response containing the newly created node's ID or an error.
        """
        url = f"{self.base_url}/telegram/nodes"
        payload = {
            "any_desk_address": any_desk_address,
            "any_desk_password": any_desk_password,
            "status": status,
            "machine_id": machine_id
        }

        # Send POST request to the API to create the node
        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})

        return self._handle_response(response)

    def get_payments(self, id_: int = None, user_id: int = None, status: str = None, limit: int = None):
        """
        Retrieve payments based on provided filters.

        Args:
            id_ (int, optional): Payment ID.
            user_id (int, optional): User ID.
            status (str, optional): Payment status (e.g., 'completed', 'pending').
            limit (int, optional): Maximum number of results to return.

        Returns:
            dict: The parsed response containing a list of payments or an error.
        """
        url = f"{self.base_url}/telegram/payments"
        params = {
            'id': id_,
            'user_id': user_id,
            'status': status,
            'limit': limit,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = self._handle_response(
            requests.get(url, params=params, headers={"Authorization": f"Bearer {self.token}"})
        )

        payments = response['data']
        for payment in payments:
            self._parse_timestamptz_field(payment, 'datetime')
        response['data'] = payments

        return response

    def create_payment_ticket(self, user_id: int, amount: float):
        """
        Create a payment ticket.

        Args:
            user_id (int): ID of the user making the payment.
            amount (float): Amount for the payment ticket.

        Returns:
            dict: Parsed response containing the created payment ticket or an error.
        """
        url = f"{self.base_url}/telegram/payments"
        payload = {"user_id": user_id, "amount": amount}
        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def complete_payment(self, id_: int):
        """
        Complete a payment.

        Args:
            id_ (int): The payment ID.

        Returns:
            dict: Parsed response indicating the payment has been completed, or an error.
        """
        url = f"{self.base_url}/telegram/payments/complete/{id_}"
        response = requests.patch(url, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def cancel_payment(self, id_: int):
        """
        Cancel a payment.

        Args:
            id_ (int): The payment ID.

        Returns:
            dict: Parsed response indicating the payment has been canceled, or an error.
        """
        url = f"{self.base_url}/telegram/payments/cancel/{id_}"
        response = requests.patch(url, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def get_users(
            self,
            id_: int = None,
            telegram_id: int = None,
            username: str = None,
            email: str = None,
            session_token: str = None,
            platform: str = 'telegram',
            limit: int = None
    ):
        """
        Retrieve users based on provided filters.

        Args:
            id_ (int, optional): User ID.
            telegram_id (int, optional): Telegram ID.
            username (str, optional): Telegram username.
            email (str, optional): Webapp email.
            session_token (str, optional): Webapp session cookie.
            platform (str): User platform. Either 'webapp' or 'telegram'.
            limit (int, optional): Max number of results to return.

        Returns:
            dict: The parsed response containing a list of users or an error.
        """

        if platform not in self.available_platforms:
            raise InvalidPlatformException()

        url = f"{self.base_url}/{platform}/users"

        if platform == 'telegram':
            params = {
                'id': id_,
                'telegram_id': telegram_id,
                'username': username,
                'limit': limit
            }

        if platform == 'webapp':
            params = {
                'id': id_,
                'email': email,
                'session_token': session_token
            }

        params = {k: v for k, v in params.items() if v is not None}
        response = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def create_user(
            self,
            user_data: dict
    ):
        """
        Create a new user.

        Args:
            user_data (dict): A dictionary with fields like:
                - telegram_id (int): Required.
                - total_spent (float, optional)
                - balance (float, optional)
                - first_name (str, optional)
                - last_name (str, optional)
                - username (str, optional)
                - language_code (str, optional)
                - banned (bool, optional)

        Returns:
            dict: Parsed response containing the newly created user or an error.

        Raises:
            ValueError: If 'telegram_id' is not provided in user_data.
        """
        if 'telegram_id' not in user_data:
            raise ValueError("telegram_id is required to update a user")

        url = f"{self.base_url}/telegram/users"
        payload = {k: v for k, v in user_data.items() if v is not None}
        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def update_user(self, user_data: dict):
        """
        Update an existing user.

        Args:
            user_data (dict): A dictionary with fields like:
                - telegram_id (int): Required.
                - total_spent (float, optional)
                - balance (float, optional)
                - first_name (str, optional)
                - last_name (str, optional)
                - username (str, optional)
                - language_code (str, optional)
                - banned (bool, optional)

        Returns:
            dict: Parsed response containing updated user data, or an error.

        Raises:
            ValueError: If 'telegram_id' is not provided in user_data.
        """
        if 'telegram_id' not in user_data:
            raise ValueError("telegram_id is required to update a user")

        url = f"{self.base_url}/telegram/users"
        payload = {k: v for k, v in user_data.items() if v is not None}
        response = requests.put(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def ping(self):
        """
        Ping the API.

        Returns:
            bool: True if the API is reachable (status_code == 200), False otherwise.
        """
        url = f"{self.base_url}/ping"
        response = requests.get(url)
        return response.status_code == 200

    def save_hash_mapping(self, question: str, answer: str):
        """
        Save a hash mapping for a question and answer.

        Args:
            question (str): The question text.
            answer (str): The answer text.

        Returns:
            dict: Parsed response data, including the generated hash.
        """
        url = f"{self.base_url}/telegram/quiz/save-hash"
        payload = {"question": question, "answer": answer}
        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def get_question_answer_by_hash(self, answer_hash: str):
        """
        Retrieve a question and answer using its hash.

        Args:
            answer_hash (str): The hash value.

        Returns:
            dict: Parsed response containing the question and answer, or an error.
        """
        url = f"{self.base_url}/telegram/quiz/get-question-answer"
        params = {"hash": answer_hash}
        response = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def save_user_answer(self, telegram_id: int, question: str, answer: str):
        """
        Save a user's answer to a question.

        Args:
            telegram_id (int): The Telegram ID of the user.
            question (str): The question text.
            answer (str): The answer text.

        Returns:
            dict: Parsed response or an error.
        """
        url = f"{self.base_url}/telegram/quiz/save-answer"
        payload = {
            "telegram_id": telegram_id,
            "question": question,
            "answer": answer
        }
        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def create_login_token(self, id_: int, telegram_id: int, status: str | None = None):
        """
        Create or retrieve a login token for a user based on their Telegram ID.

        Args:
            id_ (int): The user's ID in the 'users' table.
            telegram_id (int): The user's Telegram ID.
            status (str, optional): Status of the token (e.g., 'active', 'disabled').

        Returns:
            dict: Parsed response containing the token data or an error.
        """
        url = f"{self.base_url}/telegram/tokens"
        payload = {
            "user_id": id_,
            "telegram_id": telegram_id,
            "status": status
        }

        if not status:
            del payload['status']

        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def get_login_token(self, id_: int | None = None, telegram_id: int | None = None):
        """
        Retrieve login token(s) by user_id or telegram_id.

        Args:
            id_ (int, optional): The user's ID in the 'users' table.
            telegram_id (int, optional): The user's Telegram ID.

        Returns:
            dict: Parsed response containing token data or an error.
        """
        url = f"{self.base_url}/telegram/tokens"
        query_params = {}
        if id_:
            query_params["user_id"] = id_
        if telegram_id:
            query_params["telegram_id"] = telegram_id

        response = requests.get(url, params=query_params, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def get_notifications(
            self,
            user_id: int = None,
            notification_platform: str = None,
            is_read: bool = None,
            is_sent: bool = None
    ):
        """
        Fetch notifications based on filters.

        Args:
            user_id (int, optional): The ID of the user.
            notification_platform (str, optional): Platform of notification, e.g. "text", "email".
            is_read (bool, optional): Filter by read status.
            is_sent (bool, optional): Filter by sent status.

        Returns:
            dict: Parsed response with a list of notifications or an error.
        """
        url = f"{self.base_url}/common/notifications"
        query_params = {}

        if user_id is not None:
            query_params["user_id"] = user_id
        if notification_platform:
            query_params["notification_platform"] = notification_platform
        if is_read is not None:
            query_params["is_read"] = str(is_read).lower()  # "true" or "false"
        if is_sent is not None:
            query_params["is_sent"] = str(is_sent).lower()  # "true" or "false"

        response = requests.get(url, params=query_params, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def create_notification(
            self,
            user_id: int,
            notification_text: str,
            notification_platform: str = "all"
    ):
        """
        Create a new notification.

        Args:
            user_id (int): The ID of the user for whom the notification is created.
            notification_text (str): The text/body of the notification.
            notification_platform (str, optional): The platform (e.g., "email", "sms").
                Defaults to "all".

        Returns:
            dict: Parsed response containing the newly created notification or an error.
        """
        url = f"{self.base_url}/common/notifications"
        payload = {
            "user_id": user_id,
            "notification_text": notification_text,
            "notification_platform": notification_platform
        }
        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def update_notification(
            self,
            notification_id: int,
            user_id: int = None,
            notification_text: str = None,
            notification_platform: str = None,
            is_read: bool = None,
            is_sent: bool = None
    ):
        """
        Update an existing notification.

        Args:
            notification_id (int): The ID of the notification to update.
            user_id (int, optional): If provided, updates the user ID linked to the notification.
            notification_text (str, optional): The new text of the notification.
            notification_platform (str, optional): The new platform of the notification.
            is_read (bool, optional): Whether the notification is marked as read.
            is_sent (bool, optional): Whether the notification is marked as sent.

        Returns:
            dict: Parsed response with the updated notification or an error.
        """
        url = f"{self.base_url}/common/notifications"
        payload = {
            "id": notification_id,
            "user_id": user_id,
            "notification_text": notification_text,
            "notification_platform": notification_platform,
            "is_read": is_read,
            "is_sent": is_sent
        }

        # Remove None values from the payload
        payload = {key: value for key, value in payload.items() if value is not None}

        response = requests.put(url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def create_rent_session(self, rent_session: dict):
        """
        Create a new rent session.

        Args:
            rent_session (dict): A dictionary containing:
                - 'renter' (int): Required. ID of the user renting.
                - 'status' (str): Required. Current status of the rent session.
                - 'platform' (str): Required. Platform identifier (e.g., 'telegram').
                - 'node_id' (int, optional): The ID of the node being rented.
                - 'total_price' (float, optional): Total price of the session. Defaults to 0 if not specified.
                - 'rent_start_time' (datetime, optional): Python datetime for session start.
                - 'last_balance_update_timestamp' (datetime, optional): datetime for last balance update.
                - 'rent_stop_time' (datetime, optional): datetime for session stop.

        Returns:
            dict: Parsed response containing the created rent session or an error.
        """
        url = f"{self.base_url}/common/rent-sessions"

        # Safely convert Python datetime fields to RFC3339 if they exist
        if (
            'rent_start_time' in rent_session
            and rent_session['rent_start_time']
            and isinstance(rent_session['last_balance_update_timestamp'], datetime.datetime)
        ):
            rent_session['rent_start_time'] = rent_session['rent_start_time'].isoformat().replace('+00:00', 'Z')
        if (
            'last_balance_update_timestamp' in rent_session
            and rent_session['last_balance_update_timestamp']
            and isinstance(rent_session['last_balance_update_timestamp'], datetime.datetime)
        ):
            rent_session['last_balance_update_timestamp'] = (
                rent_session['last_balance_update_timestamp'].isoformat().replace('+00:00', 'Z')
            )
        if (
            'rent_stop_time' in rent_session
            and rent_session['rent_stop_time']
            and isinstance(rent_session['rent_stop_time'], datetime.datetime)
        ):
            rent_session['rent_stop_time'] = (
                rent_session['rent_stop_time'].isoformat().replace('+00:00', 'Z')
            )

        response = requests.post(url, json=rent_session, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def update_rent_session(self, rent_session: dict):
        """
        Update an existing rent session.

        Args:
            rent_session (dict): A dictionary containing updated fields, including:
                - 'id' (int): Required. ID of the rent session to update.
                - 'renter' (int, optional)
                - 'node_id' (int, optional)
                - 'status' (str, optional)
                - 'platform' (str, optional)
                - 'total_price' (float, optional)
                - 'rent_start_time' (datetime, optional)
                - 'last_balance_update_timestamp' (datetime, optional)
                - 'rent_stop_time' (datetime, optional)

        Returns:
            dict: Parsed response containing the updated rent session or an error.
        """
        url = f"{self.base_url}/common/rent-sessions"

        # Convert Python datetime objects to RFC3339 if present
        if (
            'rent_start_time' in rent_session
            and rent_session['rent_start_time']
            and isinstance(rent_session['rent_start_time'], datetime.datetime)
        ):
            rent_session['rent_start_time'] = rent_session['rent_start_time'].isoformat().replace('+00:00', 'Z')
        if (
            'last_balance_update_timestamp' in rent_session
            and rent_session['last_balance_update_timestamp']
            and isinstance(rent_session['last_balance_update_timestamp'], datetime.datetime)
        ):
            rent_session['last_balance_update_timestamp'] = (
                rent_session['last_balance_update_timestamp'].isoformat().replace('+00:00', 'Z')
            )
        if (
            'rent_stop_time' in rent_session
            and rent_session['rent_stop_time']
            and isinstance(rent_session['rent_stop_time'], datetime.datetime)
        ):
            rent_session['rent_stop_time'] = (
                rent_session['rent_stop_time'].isoformat().replace('+00:00', 'Z')
            )

        response = requests.patch(url, json=rent_session, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def get_rent_sessions(self, rent_session: dict):
        """
        Retrieve rent sessions based on provided filters.

        Args:
            rent_session (dict):
                renter (int): User who started rent session.
                node_id (int): The node ID to filter by.
                status (str, optional): Filter by session status.
                platform (str, optional): Filter by platform (default 'telegram').

        Returns:
            dict: Parsed response containing a list of matching rent sessions or an error.
        """
        url = f"{self.base_url}/common/rent-sessions"

        if 'platform' not in rent_session:
            rent_session['platform'] = 'telegram'

        params = {k: v for k, v in rent_session.items() if v is not None}

        response = self._handle_response(
            requests.get(url, params=params, headers={"Authorization": f"Bearer {self.token}"})
        )

        rent_sessions = response['data']
        for rent_session in rent_sessions:
            self._parse_timestamptz_field(rent_session, 'rent_start_time')
            self._parse_timestamptz_field(rent_session, 'last_balance_update_timestamp')
            self._parse_timestamptz_field(rent_session, 'rent_stop_time')
        response['data'] = rent_sessions

        return response

    def get_active_rent_sessions_and_occupied_nodes(self, user_id: int):
        rent_session = {
            'status': 'active',
            'renter': user_id
        }
        active_rent_sessions = self.get_rent_sessions(rent_session)['data']
        active_rent_sessions_and_occupied_nodes = []
        for session in active_rent_sessions:
            node = self.get_nodes(id_=session['node_id'])['data'][0]
            active_rent_sessions_and_occupied_nodes.append(
                (node, session,)
            )
        return active_rent_sessions_and_occupied_nodes

    def save_user_interaction(self, user_interaction: dict) -> dict:
        if not isinstance(user_interaction['telegram_id'], int):
            raise Exception(f"telegram_id is not int")
        if not isinstance(user_interaction['event_type'], str):
            raise Exception(f"event_type is not str")
        if not isinstance(user_interaction['event_data'], str):
            raise Exception(f"event_data is not str")

        response = requests.post(f"{self.base_url}/telegram/user-interactions", json={
            "telegram_id": user_interaction['telegram_id'],
            "event_type": user_interaction['event_type'],
            "event_data": user_interaction['event_data'],
        }, headers={"Authorization": f"Bearer {self.token}"})

        return self._handle_response(response)

    def get_support_agents(
        self,
        *,
        id_: int | None = None,
        user_id: int | None = None,
        limit: int | None = None,
    ):
        """
        Fetch support‑agent records.

        Args:
            id_      (int, optional): Exact agent id. If given, it is appended
                                      to the path (`/support/agents/{id}`).
            user_id  (int, optional): Filter by the user the agent represents.
            limit    (int, optional): Max number of rows to return.

        Returns
        -------
        dict
            Standard API envelope with agents in ``data``.
        """
        url = f"{self.base_url}/support/agents"
        if id_ is not None:
            url += f"/{id_}"

        params = {k: v for k, v in {"user_id": user_id, "limit": limit}.items() if v is not None}

        response = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def create_support_agent(self, *, agent: dict):
        """
        Create a support agent.

        Parameters
        ----------
        agent : dict
            Anything accepted by your `POST /support/agents` handler.
        """
        url = f"{self.base_url}/support/agents"
        response = requests.post(url, json=agent, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    def update_support_agent(self, *, id_: int, agent: dict):
        """
        PATCH an existing support agent.

        Only the keys you include in *agent* will be updated.
        """
        url = f"{self.base_url}/support/agents/{id_}"
        response = requests.patch(url, json=agent, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(response)

    # ----------  Support Chats  ----------

    def get_support_chats(
        self,
        *,
        id_: int | None = None,
        user_id: int | None = None,
        agent_id: int | None = None,
        status: str | None = None,
        limit: int | None = None,
    ):
        """
        Retrieve support‑chat sessions.
        """
        url = f"{self.base_url}/support/chats"
        if id_ is not None:
            url += f"/{id_}"

        params = {
            "user_id": user_id,
            "agent_id": agent_id,
            "status": status,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        resp = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(resp)

    def create_support_chat(self, *, chat: dict):
        """
        Open a new support chat.

        {
            "customer_id": `web_app_user_id: int`
        }
        """
        url = f"{self.base_url}/support/chats"
        resp = requests.post(url, json=chat, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(resp)

    def close_support_chat(self, *, id_: int):
        """Close a chat by id (PATCH `/support/chats/close/{id}`)"""
        url = f"{self.base_url}/support/chats/close/{id_}"
        resp = requests.patch(url, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(resp)

    # ----------  Support Messages  ----------

    def get_support_messages(
        self,
        *,
        chat_id: int | None = None,
        user_id: int | None = None,
        agent_id: int | None = None,
        limit: int | None = None,
    ):
        """
        Fetch messages in support chats.

        If *chat_id* is supplied the backend will usually ignore the other
        filters and return all messages for that chat.
        """
        url = f"{self.base_url}/support/messages"
        params = {
            "chat_id": chat_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}

        resp = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(resp)

    def create_support_message(self, *, message: dict):
        """
        Add a message to a chat. Example payload::

            {
                "chat_id": 1,
                "sender": "system",   # or "agent"
                "sender_agent_id": 1,
                "content": "Hello, I need help…"
            }
        """
        url = f"{self.base_url}/support/messages"
        resp = requests.post(url, json=message, headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(resp)

    def update_support_message(self, *, id_: int, **flags):
        """
        Patch a message’s delivery/read booleans.

        client.update_support_message(
            id_=123,
            delivered_to_telegram=True,
            delivered_to_web=True
        )
        """
        url = f"{self.base_url}/support/messages/{id_}"
        resp = requests.patch(url, json=flags,
                              headers={"Authorization": f"Bearer {self.token}"})
        return self._handle_response(resp)

    # --- Utility Methods ---

    def _parse_timestamptz_field(self, data: dict, field_name: str):
        """
        Convert a timestamptz field in ISO 8601 format to a datetime object with timezone support.
        Updates `data[field_name]` in place if parsing is successful.

        Args:
            data (dict): The dictionary containing the field.
            field_name (str): The name of the field to convert.

        Returns:
            None
        """
        if field_name in data and data[field_name]:
            try:
                # Python <3.11 doesn't directly parse the 'Z' suffix, so you may replace 'Z' with '+00:00' if needed:
                iso_str = data[field_name].replace('Z', '+00:00')
                data[field_name] = datetime.datetime.fromisoformat(iso_str)
            except Exception as e:
                self.logger.debug(f"Failed to parse field {field_name} ('{data[field_name]}'): {e}")
                data[field_name] = None

    @staticmethod
    def generate_hash(question: str, answer: str) -> str:
        """
        Generate a hash for a question and answer.

        Args:
            question (str): The question text.
            answer (str): The answer text.

        Returns:
            str: A 32-character hash.
        """
        data = question + answer
        hash_object = hashlib.sha256(data.encode())
        return hash_object.hexdigest()[:32]

    def _handle_response(self, response):
        """
        Handle the API response by parsing JSON and checking for errors.

        Args:
            response (requests.Response): The response object to parse.

        Returns:
            dict: Parsed JSON data if successful.

        Raises:
            Exception: If the API returns an error or an invalid response.
        """
        try:
            json_data = response.json()
        except ValueError:
            # Response is not JSON
            response.raise_for_status()
            raise Exception(f"Invalid response: {response.text}")

        if 200 <= response.status_code < 300:
            if not json_data.get('success', False):
                error_message = json_data.get('error', 'Unknown error')
                raise Exception(f"API Error: {error_message}")
            else:
                return json_data
        if 404 == response.status_code:
            self.logger.debug(json_data.get('error', response.reason))
            return {
                'success': False,
                'error': json_data.get('error', response.reason),
                'data': []
            }
        else:
            error_message = json_data.get('error', response.reason)
            self.logger.debug(error_message)
            raise Exception(f"API Error: {error_message}")
