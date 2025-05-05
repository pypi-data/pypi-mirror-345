from ...domain.models.twitter_user_metadata import TwitterUserMetadata


class TwitterMessageMetaData:
    def __init__(self, tweet_id: str, user: TwitterUserMetadata, message:  str, created_at: str, view_count: int, retweet_count: int, reply_count: int):
        self.tweet_id = tweet_id
        self.message = message
        self.user = user
        self.created_at = created_at,
        self.view_count = view_count
        self.retweet_count = retweet_count
        self.reply_count = reply_count

    def to_dict(self) -> dict:
        """
        Convert TwitterMessage instance to a dictionary.

        Returns:
            dict: A dictionary representation of the TwitterMessage instance.
            If the user attribute is a TwitterUser instance, it will be converted
            to a dictionary using its __dict__ attribute.
        """
        return {
            'tweet_id': self.tweet_id,
            'message': self.message,
            'created_at': self.created_at,
            'view_count': self.view_count,
            'retweet_count': self.retweet_count,
            'reply_count': self.reply_count,
            'user': self.user.to_dict()
        }