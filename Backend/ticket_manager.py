import json
from pathlib import Path
from datetime import datetime


class TicketManager:

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.ticket_dir = output_dir / "generated_tickets"
        self.counter_file = self.ticket_dir / "ticket_counter.json"

        self.ticket_dir.mkdir(parents=True, exist_ok=True)

    def _get_next_ticket_number(self):
        if self.counter_file.exists():
            with open(self.counter_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            last_number = data.get("last_ticket_number", 0)
        else:
            last_number = 0

        next_number = last_number + 1

        with open(self.counter_file, "w", encoding="utf-8") as f:
            json.dump(
                {"last_ticket_number": next_number},
                f,
                indent=4
            )

        return next_number

    def create_ticket(
        self,
        request_id,
        employee,
        email,
        title,
        description,
        category,
        priority
    ):
        ticket_number = self._get_next_ticket_number()
        ticket_id = f"TKT-{ticket_number:02d}"

        ticket = {
            "Ticket ID": ticket_id,
            "Request ID": request_id,
            "Employee": employee,
            "Email": email,
            "Title": title,
            "Description": description,
            "Category": category,
            "Priority": priority,
            "Status": "Open",
            "Created At": datetime.now().isoformat(timespec="seconds")
        }

        ticket_file = self.ticket_dir / f"{ticket_id}.json"

        with open(ticket_file, "w", encoding="utf-8") as f:
            json.dump(ticket, f, indent=4)

        return ticket