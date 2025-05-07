from brynq_sdk_brynq import BrynQ
from typing import List, Union
from .get_data import GetData
from .activity import Activity
from .item import Item
from .order import Order
from .project import Project
from .resource import Resource
from .time_tracking import TimeTracking
from .user import User
from .leave import Leave


class VPlan(BrynQ):
    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        A class to fetch data from the vPlan API. See https://developer.vplan.com/documentation/#tag/General/ for more information
        """
        super().__init__()
        self.timeout = 3600
        self.headers = self._get_credentials(label)
        self.post_headers = {**self.headers, 'Content-Type': 'application/json'}
        self.base_url = 'https://api.vplan.com/v1/'
        self.get = GetData(self)
        self.activity = Activity(self)
        self.item = Item(self)
        self.order = Order(self)
        self.project = Project(self)
        self.resource = Resource(self)
        self.time_tracking = TimeTracking(self)
        self.user = User(self)
        self.leave = Leave(self)

    def _get_credentials(self, label) -> dict:
        """
        Retrieve API key and env from the system credentials.
        Args: label (Union[str, List]): The label or list of labels to get the credentials.
        Returns: str: The authorization headers
        """
        credentials = self.get_system_credential(system='vplan', label=label)
        headers = {
            'X-Api-Key': credentials['X-Api-Key'],
            'X-Api-Env': credentials['X-Api-Env']
        }
        return headers