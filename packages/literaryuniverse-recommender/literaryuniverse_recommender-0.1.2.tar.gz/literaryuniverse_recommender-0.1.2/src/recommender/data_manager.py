import pandas as pd
from ast import literal_eval
from typing import Optional, List, Set


class DataManager:
    """Handles data loading, preprocessing, and language validation"""

    def __init__(
        self,
        story_path: str,
        user_path: str,
        rating_path: Optional[str] = None,
        behavior_path: Optional[str] = None,
    ) -> None:
        self.story_path: str = story_path
        self.user_path: str = user_path
        self.rating_path: Optional[str] = rating_path
        self.behavior_path: Optional[str] = behavior_path
        self.stories: Optional[pd.DataFrame] = None
        self.users: Optional[pd.DataFrame] = None
        self.ratings: Optional[pd.DataFrame] = None
        self.behavior: Optional[pd.DataFrame] = None

    def load_data(self) -> None:
        """Load and preprocess all datasets"""
        self._load_stories()
        self._load_users()

        if self.rating_path:
            self._load_ratings()
        if self.behavior_path:
            self._load_behavior()

        self._validate_languages()

    def _load_stories(self) -> None:
        """Load and preprocess story data"""
        self.stories = pd.read_csv(self.story_path)
        self.stories["keywords"] = self._parse_list_column(self.stories["keywords"])
        self.stories["genres"] = self._parse_list_column(self.stories["genres"])
        self.stories["features"] = self.stories.apply(
            self._build_story_features, axis=1
        )

    def _load_users(self) -> None:
        """Load and preprocess user data"""
        self.users = pd.read_csv(self.user_path)
        self.users["favoriteGenres"] = self._parse_list_column(
            self.users["favoriteGenres"]
        )
        self.users["preferredKeywords"] = self._parse_list_column(
            self.users["preferredKeywords"]
        )
        self.users["features"] = self.users.apply(self._build_user_features, axis=1)

    def _load_ratings(self) -> None:
        """Load and preprocess rating data"""
        self.ratings = pd.read_csv(self.rating_path)
        self.ratings["timestamp"] = pd.to_datetime(self.ratings["timestamp"])

    def _load_behavior(self) -> None:
        """Load and preprocess behavioral data"""
        self.behavior = pd.read_csv(self.behavior_path)
        self.behavior["reads"] = self._parse_list_column(self.behavior["reads"])
        self.behavior["impressions"] = self._parse_list_column(
            self.behavior["impressions"]
        )
        self.behavior["timestamp"] = pd.to_datetime(self.behavior["timestamp"])

    def _parse_list_column(self, col: pd.Series) -> pd.Series:
        """Parse string representations of lists"""
        return col.apply(lambda x: literal_eval(x) if pd.notnull(x) else [])

    def _build_story_features(self, row: pd.Series) -> List[str]:
        """Create feature set for stories"""
        features: List[str] = [
            *[f"genre:{g.strip()}" for g in row["genres"]],
            *[f"keyword:{k.strip()}" for k in row["keywords"]],
            f"language:{row['language']}",
            f"ageRating:{row['ageRating']}",
            f"authorLevel:{row['authorLevel']}",
            f"audioBook:{row['audioBook']}",
            f"comics:{row['comics']}",
        ]
        return features

    def _build_user_features(self, row: pd.Series) -> List[str]:
        """Create feature set for users"""
        features: List[str] = [
            *[f"favoriteGenre:{g.strip()}" for g in row["favoriteGenres"]],
            *[f"preferredKeyword:{k.strip()}" for k in row["preferredKeywords"]],
            f"preferredAuthorLevel:{row['preferredAuthorLevel']}",
            f"ratingLimitation:{row['ratingLimitation']}",
            f"gender:{row['gender']}",
            f"userType:{row['userType']}",
            f"preferredReadingLanguage:{row['preferredReadingLanguage']}",
            f"language:{row['language']}",
            f"country:{row['country']}",
        ]
        return features

    def _validate_languages(self) -> None:
        """Ensure all stories have valid language codes"""
        valid_languages: Set[str] = set(self.users["preferredReadingLanguage"].unique())
        self.stories = self.stories[self.stories["language"].isin(valid_languages)]
