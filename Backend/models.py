from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EmployeeRequest:

    request_id: str
    employee: str
    email: str
    date_opened: str
    request: str
    initial_action_taken: str = "Not started"


@dataclass
class AgentResponse:

    request_id: str
    response: str
    action: str
    category: Optional[str] = None
    priority: Optional[str] = None
    ticket_id: Optional[str] = None
    sources: list[str] = field(default_factory=list)


@dataclass
class Ticket:

    ticket_id: str
    request_id: str
    employee: str
    email: str
    title: str
    description: str
    category: str
    priority: str
    status: str = "Open"