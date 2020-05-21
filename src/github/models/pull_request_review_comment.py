from .comment import Comment


class PullRequestReviewComment(Comment):
    # def review(self) -> Review:
    #     return Review(self._raw["pullRequestReview"])

    def is_reply(self) -> bool:
        return self._raw["replyTo"] is not None
