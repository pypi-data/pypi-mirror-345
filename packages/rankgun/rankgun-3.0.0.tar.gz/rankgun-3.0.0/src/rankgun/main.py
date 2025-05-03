"""RankGun Python Package."""

import httpx

from .models import robloxResponse

baseUrl: str = "https://api.rankgun.works"


class Client:
    """Client to containerize rankgun workspaces.

    Args:
    ----
        wid: Workspace Id
        key: Workspace Api Key

    """

    def __init__(self, wid: str, token: str):
        """Init client class."""
        self.wid: str = wid
        self.client: httpx.Client = httpx.Client(headers={"api-token": token})

    def promote(self, uid: int) -> robloxResponse:
        """Promote an individual.

        Promote an individual to the next rank.

        Args:
        ----
            uid: Target ROBLOX User Id

        """
        response = self.client.post(url=f"{baseUrl}/roblox/promote", json={"user_id": uid, "workspace_id": self.wid})
        response.raise_for_status()

        robloxresponse = robloxResponse.model_validate(response.json())

        return robloxresponse

    def demote(self, uid: int) -> robloxResponse:
        """Demote an individual.

        Demotes an individual to the next rank.

        Args:
        ----
            uid: Target ROBLOX User Id

        """
        response = self.client.post(url=f"{baseUrl}/roblox/demote", json={"user_id": uid, "workspace_id": self.wid})
        response.raise_for_status()

        robloxresponse = robloxResponse.model_validate(response.json())

        return robloxresponse

    def setRank(self, uid: int, rank: int) -> robloxResponse:
        """Set the rank of an individual.

        Sets the rank of an individual to a certain rank.

        Args:
        ----
            uid: Target ROBLOX User Id
            rank: Target Roblox Rank

        """
        response = self.client.post(
            url=f"{baseUrl}/roblox/set-rank", json={"user_id": uid, "workspace_id": self.wid, "rank": rank}
        )
        response.raise_for_status()

        robloxresponse = robloxResponse.model_validate(response.json())

        return robloxresponse


if __name__ == "__main__":  # pragma: no cover
    pass
