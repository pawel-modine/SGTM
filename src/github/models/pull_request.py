from datetime import datetime
from typing import List, Optional, Dict, Any
from src.logger import logger
from src.utils import parse_date_string
from .review import Review
from .comment import Comment
from .commit import Commit
from .user import User
import copy


class PullRequest(object):
    def __init__(self, raw_pull_request: Dict[str, Any]):
        self.__raw = copy.deepcopy(raw_pull_request)
        self.__assignees = self._assignees_from_raw()

    def _assignees_from_raw(self) -> List[str]:
        return sorted([node["login"] for node in self.__raw["assignees"]["nodes"]])

    def assignees(self) -> List[str]:
        return self.__assignees

    def set_assignees(self, assignees: List[str]):
        self.__raw = copy.deepcopy(self.__raw)
        self.__raw["assignees"]["nodes"] = [
            {"login": assignee_login} for assignee_login in assignees
        ]
        self.__assignees = self._assignees_from_raw()

    def requested_reviewers(self) -> List[str]:
        return sorted(
            node["requestedReviewer"]["login"]
            for node in self.__raw["reviewRequests"]["nodes"]
        )

    def reviewers(self) -> List[str]:
        return [review.author_handle() for review in self.reviews()]

    def assignee(self) -> str:
        maybe_multi_assignees = self.assignees()
        if len(maybe_multi_assignees) == 1:
            return maybe_multi_assignees[0]
        elif len(maybe_multi_assignees) == 0:
            logger.info("GitHub PR has no assignees. Choosing author as assignee")
            return self.author_handle()
        else:
            assignee = maybe_multi_assignees[0]
            logger.info(
                "GitHub PR has multiple assignees: {} Choosing first one in alphabetical order as as assignee: {}".format(
                    maybe_multi_assignees, assignee
                )
            )
            return assignee

    def id(self) -> str:
        return self.__raw["id"]

    def number(self) -> int:
        return self.__raw["number"]

    def title(self) -> str:
        return self.__raw["title"]

    def url(self) -> str:
        return self.__raw["url"]

    def repository_id(self) -> str:
        return self.__raw["repository"]["id"]

    def repository_name(self) -> str:
        return self.__raw["repository"]["name"]

    def owner_handle(self) -> str:
        return self.owner().login()

    def owner(self) -> User:
        return User(self.__raw["owner"])

    def repository_owner_handle(self) -> str:
        return self.__raw["repository"]["owner"]["login"]

    def author(self) -> User:
        return User(self.__raw["author"])

    def author_handle(self) -> str:
        return self.author().login()

    def body(self) -> str:
        return self.__raw["body"]

    def set_body(self, body: str):
        self.__raw = copy.deepcopy(self.__raw)
        self.__raw["body"] = copy.deepcopy(body)

    def closed(self) -> bool:
        return self.__raw["closed"]

    def merged(self) -> bool:
        return self.__raw["merged"]

    def mergeable(self) -> bool:
        return self.__raw["mergeable"]

    def is_approved(self) -> bool:
        if len(self.reviews()) > 0:
            reviews = self.reviews()
            reviews.sort(key=lambda review: review.submitted_at(), reverse=True)
            return reviews[0].is_approval()
        else:
            return False

    def is_build_successful(self) -> bool:
        return self.build_status() == Commit.BUILD_SUCCESSFUL

    def merged_at(self) -> Optional[datetime]:
        merged_at = self.__raw.get("mergedAt", None)
        if merged_at is None:
            return None
        return parse_date_string(merged_at)

    def reviews(self) -> List[Review]:
        return [Review(review) for review in self.__raw["reviews"]["nodes"]]

    def comments(self) -> List[Comment]:
        return [Comment(comment) for comment in self.__raw["comments"]["nodes"]]

    def to_raw(self) -> Dict[str, Any]:
        return copy.deepcopy(self.__raw)

    def build_status(self) -> Optional[str]:
        return self.commits()[0].status() if self.commits()[0].status() else None

    def commits(self) -> List[Commit]:
        return [Commit(commit) for commit in self.__raw["commits"]["nodes"]]
