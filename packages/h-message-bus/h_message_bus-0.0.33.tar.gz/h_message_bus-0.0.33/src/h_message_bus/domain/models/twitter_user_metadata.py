class TwitterUserMetadata:
    def __init__(self,
                 id: str,
                 screen_name: str,
                 user_name: str = None,
                 description: str = None,
                 followers_count: int = 0,
                 like_count: int = 0,
                 is_verified: bool = False,
                 url: str = None,
                 bio_urls: list = None):
        """
        Initialize a TwitterUserMetadata instance.

        Args:
            id (str): The user's Twitter ID
            screen_name (str): The user's screen name
            user_name (str, optional): The user's name
            description (str, optional): The user's bio description
            followers_count (int, optional): Number of followers
            like_count (int, optional): Number of likes
            is_verified (bool, optional): Whether the user is verified
            url (str, optional): The user's profile URL
            bio_urls (list, optional): URLs mentioned in the user's bio
        """
        self.id = id
        self.screen_name = screen_name
        self.user_name = user_name
        self.description = description
        self.followers_count = followers_count
        self.like_count = like_count
        self.is_verified = is_verified
        self.url = url
        self.bio_urls = bio_urls or []

    def to_dict(self) -> dict:
        """
        Convert TwitterUserMetadata instance to a dictionary.

        Returns:
            dict: A dictionary representation of the TwitterUserMetadata instance.
        """
        return {
            'id': self.id,
            'screen_name': self.screen_name,
            'user_name': self.user_name,
            'description': self.description,
            'followers_count': self.followers_count,
            'like_count': self.like_count,
            'is_verified': self.is_verified,
            'url': self.url,
            'bio_urls': self.bio_urls
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TwitterUserMetadata':
        """
        Create a TwitterUserMetadata instance from a dictionary.

        Args:
            data (dict): A dictionary containing TwitterUserMetadata attributes

        Returns:
            TwitterUserMetadata: A new TwitterUserMetadata instance
        """
        return cls(
            id=data.get('id'),
            screen_name=data.get('screen_name'),
            user_name=data.get('user_name'),
            description=data.get('description'),
            followers_count=data.get('followers_count', 0),
            like_count=data.get('like_count', 0),
            is_verified=data.get('is_verified', False),
            url=data.get('url'),
            bio_urls=data.get('bio_urls', [])
        )