from ticket_manager import TicketManager
from pathlib import Path
import json
from datetime import datetime
from typing import Optional

from models import EmployeeRequest


class ITSupportAgent:

    def __init__(self, output_dir: Path):

        self.output_dir = output_dir
        self.request_counter_file = output_dir / "request_counter.json"

        self.employee: Optional[str] = None
        self.email: Optional[str] = None
        self.request: Optional[EmployeeRequest] = None

        self.conversation_history = []

        self.workflow = None
        self.workflow_step = None

        self.ticket_manager = TicketManager(output_dir)

    # ---------------------------------------------------------
    # Generate sequential request ID
    # ---------------------------------------------------------

    def generate_request_id(self):

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        if self.request_counter_file.exists():

            with open(
                self.request_counter_file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            last_number = data.get(
                "last_request_number",
                0
            )

        else:

            last_number = 0

        next_number = last_number + 1

        with open(
            self.request_counter_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "last_request_number": next_number
                },
                f,
                indent=4
            )

        return f"REQ-{next_number:02d}"

    # ---------------------------------------------------------
    # Start support request
    # ---------------------------------------------------------

    def start_session(
        self,
        employee: str,
        email: str
    ):

        self.employee = employee.strip()
        self.email = email.strip()

        request_id = self.generate_request_id()

        date_opened = datetime.now().strftime(
            "%a %d %b"
        )

        self.request = EmployeeRequest(
            request_id=request_id,
            employee=self.employee,
            email=self.email,
            date_opened=date_opened,
            request="",
            initial_action_taken="Not started"
        )

        self.conversation_history = []

        return request_id

    # ---------------------------------------------------------
    # Check whether session exists
    # ---------------------------------------------------------

    def is_session_active(self):

        return self.request is not None

    # ---------------------------------------------------------
    # Add message to conversation
    # ---------------------------------------------------------

    def add_message(
        self,
        role: str,
        content: str
    ):

        self.conversation_history.append(
            {
                "role": role,
                "content": content
            }
        )

    # ---------------------------------------------------------
    # Store initial employee request
    # ---------------------------------------------------------

    def set_initial_request(
        self,
        request_text: str
    ):

        if self.request is None:
            return

        if not self.request.request:

            self.request.request = request_text

    # ---------------------------------------------------------
    # Update troubleshooting/action state
    # ---------------------------------------------------------

    def update_action_taken(
        self,
        action: str
    ):

        if self.request is None:
            return

        self.request.initial_action_taken = action

    # ---------------------------------------------------------
    # Get request information
    # ---------------------------------------------------------

    def get_request_data(self):

        if self.request is None:
            return None

        return {
            "Request ID": self.request.request_id,
            "Employee": self.request.employee,
            "Email": self.request.email,
            "Date Opened": self.request.date_opened,
            "Request": self.request.request,
            "Initial Action Taken So Far":
                self.request.initial_action_taken
        }

    def start_printer_workflow(self):
        self.workflow = "printer"
        self.workflow_step = "check_queue"


    def handle_printer_workflow(self, user_message: str):
        message = user_message.strip().lower()

        if self.workflow_step == "check_queue":

            self.workflow_step = "clear_queue"

            return (
                "I'll help you troubleshoot the printer. "
                "Is there anything currently stuck in the print queue?"
            )

        if self.workflow_step == "clear_queue":

            if message in {"yes", "y", "there is", "there are"}:
                self.workflow_step = "check_after_queue"

                return (
                    "Please clear the print queue and try printing again. "
                    "Is the printer working now?"
                )

            if message in {"no", "n", "nothing"}:
                self.workflow_step = "restart_spooler"

                return (
                    "Please restart the print spooler and try printing again. "
                    "Is the printer working now?"
                )

            return (
                "Please answer yes or no. "
                "Is there anything currently stuck in the print queue?"
            )

        if self.workflow_step == "check_after_queue":

            if message in {"yes", "y", "working", "it works", "fixed"}:
                self.workflow = None
                self.workflow_step = None

                return (
                    "Great. The printer issue appears to be resolved. "
                    "No ticket is required based on the troubleshooting result."
                )

            if message in {"no", "n", "still not working", "not working"}:
                self.workflow_step = "restart_spooler"

                return (
                    "Please restart the print spooler and try printing again. "
                    "Is the printer working now?"
                )

            return "Please answer yes or no. Is the printer working now?"

        if self.workflow_step == "restart_spooler":

            if message in {"yes", "y", "working", "it works", "fixed"}:
                self.workflow = None
                self.workflow_step = None

                return (
                    "Great. The printer issue appears to be resolved. "
                    "No ticket is required."
                )

            if message in {"no", "n", "still not working", "not working"}:
                self.workflow_step = "asset_tag"

                return (
                    "The issue is still unresolved. "
                    "Please provide the printer asset tag so I can create "
                    "the required support ticket."
                )

            return "Please answer yes or no. Is the printer working now?"

        if self.workflow_step == "asset_tag":

            asset_tag = user_message.strip()

            if len(asset_tag) < 2:
                return "Please provide a valid printer asset tag."

            ticket = self.ticket_manager.create_ticket(
                request_id=self.request.request_id,
                employee=self.request.employee,
                email=self.request.email,
                title="Printer troubleshooting issue",
                description=(
                    f"Printer issue reported by {self.request.employee}. "
                    f"Troubleshooting was attempted, but the issue persisted. "
                    f"Printer asset tag: {asset_tag}"
                ),
                category="Printer",
                priority="Medium"
            )

            self.workflow = None
            self.workflow_step = None

            return (
                f"The printer issue could not be resolved through the "
                f"required troubleshooting steps.\n\n"
                f"I have created support ticket **{ticket['Ticket ID']}** "
                f"for the printer with asset tag **{asset_tag}**."
            )

        return "I need more information to continue troubleshooting."

    def detect_workflow(self, user_message: str):
        message = user_message.lower()

        printer_keywords = [
            "printer",
            "printing",
            "print",
            "printer isn't working",
            "printer is not working"
        ]

        if any(keyword in message for keyword in printer_keywords):
            return "printer"

        return None