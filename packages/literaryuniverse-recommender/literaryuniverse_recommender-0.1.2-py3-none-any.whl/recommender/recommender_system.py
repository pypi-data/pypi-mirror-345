from functools import lru_cache
import os
from uuid import UUID
import joblib
import pandas as pd
import numpy as np
from lightfm import LightFM
from lightfm.data import Dataset
from datetime import datetime
from typing import Annotated, Optional, List, Tuple, Dict, Any, Set

from .data_manager import DataManager
from models.recommendation import Recommendation


class RecommenderSystem:
    """Main recommendation system with strict language enforcement"""

    def __init__(self, data_manager: DataManager) -> None:
        self.dm: DataManager = data_manager
        self.dataset: Optional[Dataset] = None
        self.model: Optional[LightFM] = None
        self.user_id_map: Optional[Dict[str, int]] = None
        self.item_id_map: Optional[Dict[str, int]] = None
        self.user_features: Optional[Any] = None
        self.item_features: Optional[Any] = None
        self.interactions: Optional[Any] = None
        self.weights: Optional[Any] = None

    @classmethod
    def load_model(cls, path: str) -> "RecommenderSystem":
        """
        Alternative constructor to load a RecommenderSystem from disk.

        Args:
            path: Path to the saved model file (e.g., 'model.joblib')

        Returns:
            An instance of RecommenderSystem.
        """
        obj: Any = joblib.load(path)
        if not isinstance(obj, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__} instance")
        return obj

    def save_model(self, save_dir: str = ".") -> str:
        """
        Save the current state of the recommender system to disk using joblib.
        Args:
            save_dir: Directory where the model should be saved.
        Returns:
            The full path to the saved model file.
        """
        os.makedirs(save_dir, exist_ok=True)
        model_path = os.path.join(save_dir, "model.joblib")
        joblib.dump(self, model_path)
        return model_path

    def prepare_dataset(self) -> None:
        """Prepare LightFM dataset with language-aware interactions"""
        interactions: pd.DataFrame = self._create_interactions()
        self._build_lightfm_dataset(interactions)

    def _create_interactions(self) -> pd.DataFrame:
        """Create interaction matrix considering language preferences"""
        interactions: List[Dict[str, Any]] = []

        # Add explicit ratings
        if self.dm.ratings is not None:
            for _, row in self.dm.ratings.iterrows():
                if self._is_language_compatible(row["userId"], row["publicationId"]):
                    interactions.append(
                        {
                            "user_id": row["userId"],
                            "item_id": row["publicationId"],
                            "weight": float(row["rating"]),
                            "timestamp": row["timestamp"],
                        }
                    )

        # Add behavioral data
        if self.dm.behavior is not None:
            interactions.extend(self._process_behavioral_data())

        return pd.DataFrame(interactions)

    def _is_language_compatible(self, user_id: str, item_id: str) -> bool:
        """Verify user's language preference matches item language with validation"""
        try:
            user_lang: str = self.dm.users[self.dm.users["userId"] == user_id][
                "preferredReadingLanguage"
            ].iloc[0]
            story_match: pd.DataFrame = self.dm.stories[
                self.dm.stories["storyId"] == item_id
            ]
            if story_match.empty:
                return False
            item_lang: str = story_match["language"].iloc[0]
            return user_lang == item_lang
        except IndexError:
            return False

    def _parse_read_entry(
        self, entry: str
    ) -> Tuple[Optional[str], Optional[str], float]:
        # Splitting the story-language-read_percentage
        # Format: 'story-uuid-Language-0.61'
        parts = entry.split("-")
        if len(parts) >= 3:
            story_id: str = "-".join(parts[:-2])
            language: str = parts[-2]
            try:
                percent: float = float(parts[-1])
            except ValueError:
                percent = 0.0
            return story_id, language, percent
        return None, None, 0.0

    def _process_behavioral_data(self) -> List[Dict[str, Any]]:
        """Process reads and impressions with enhanced validation"""
        interactions: List[Dict[str, Any]] = []
        valid_story_ids: Set[str] = set(self.dm.stories["storyId"])

        for _, row in self.dm.behavior.iterrows():
            user_id: str = row["userId"]
            user_lang: str = self.dm.users[self.dm.users["userId"] == user_id][
                "preferredReadingLanguage"
            ].iloc[0]
            for read_item in row["reads"]:
                story_id, story_lang, percent = self._parse_read_entry(read_item)
                if story_id and story_id in valid_story_ids:
                    story_record: pd.DataFrame = self.dm.stories[
                        self.dm.stories["storyId"] == story_id
                    ]
                    if (
                        not story_record.empty
                        and story_lang == story_record["language"].iloc[0]
                        and user_lang == story_lang
                    ):
                        interactions.append(
                            {
                                "user_id": user_id,
                                "item_id": story_id,
                                "weight": percent,  # Completion percentage as weight
                                "timestamp": row["timestamp"],
                            }
                        )
            for impression_item in row["impressions"]:
                pub_id: Optional[str] = self._extract_publication_id(impression_item)
                if pub_id and pub_id in valid_story_ids:
                    interactions.append(
                        {
                            "user_id": user_id,
                            "item_id": pub_id,
                            "weight": 0.1,  # TODO how much we want the impressions to be impactful
                            "timestamp": row["timestamp"],
                        }
                    )
        return interactions

    def _extract_publication_id(self, item_str: str) -> Optional[str]:
        """Extract publication ID from behavioral data strings"""
        if isinstance(item_str, str):
            return item_str.split("-")[0]
        return None

    def _build_lightfm_dataset(self, interactions: pd.DataFrame) -> None:
        """Build LightFM dataset with language-enforced interactions"""
        self.dataset = Dataset()
        self.dataset.fit(
            users=self.dm.users["userId"].unique(),
            items=self.dm.stories["storyId"].unique(),
            user_features=[f for feats in self.dm.users["features"] for f in feats],
            item_features=[f for feats in self.dm.stories["features"] for f in feats],
        )

        # Build interaction matrix with time-based weights
        interaction_tuples: List[Tuple[str, str, float]] = []
        for _, row in interactions.iterrows():
            time_weight: float = self._calculate_time_weight(row["timestamp"])
            final_weight: float = row["weight"] * 0.7 + time_weight * 0.3
            interaction_tuples.append((row["user_id"], row["item_id"], final_weight))

        self.interactions, self.weights = self.dataset.build_interactions(
            interaction_tuples
        )

        # Build feature matrices
        self.user_features = self.dataset.build_user_features(
            [(row["userId"], row["features"]) for _, row in self.dm.users.iterrows()]
        )
        self.item_features = self.dataset.build_item_features(
            [(row["storyId"], row["features"]) for _, row in self.dm.stories.iterrows()]
        )

        # Store mappings
        self.user_id_map, _, self.item_id_map, _ = self.dataset.mapping()

    def _calculate_time_weight(
        self, timestamp: pd.Timestamp, max_age_days: int = 365
    ) -> float:
        """Calculate time-based decay for interactions"""
        age_days: int = (datetime.now() - timestamp).days
        return max(0.1, 1.0 - (0.9 * age_days / max_age_days))

    def train_model(self, epochs: int = 30) -> None:
        """Train the recommendation model"""
        self.model = LightFM(loss="warp", learning_schedule="adagrad")
        self.model.fit(
            self.interactions,
            sample_weight=self.weights,
            user_features=self.user_features,
            item_features=self.item_features,
            epochs=epochs,
            num_threads=4,
            verbose=True,
        )

    @lru_cache(maxsize=128, typed=False)
    def get_popular_recommendations(
        self, top_n: int = 5, language: Optional[str] = "English"
    ) -> List[Recommendation]:
        """Get popular items as fallback recommendations

        Args:
            top_n: Number of recommendations to return
            language: Optional language filter

        Returns:
            DataFrame of popular item recommendations
        """
        # Calculate popularity scores from interaction data
        item_counts = {}
        for _, row in self.dm.ratings.iterrows():
            item_id = row["publicationId"]
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

        # Filter by language if specified
        candidates = self.dm.stories
        if language:
            candidates = candidates[candidates["language"] == language]

        # Sort by popularity
        popular_items = sorted(
            [
                (item_id, item_counts.get(item_id, 0))
                for item_id in candidates["storyId"]
            ],
            key=lambda x: x[1],
            reverse=True,
        )

        # Get top N popular items
        top_items = [item_id for item_id, _ in popular_items[:top_n]]
        recommendations_df = self.dm.stories[self.dm.stories["storyId"].isin(top_items)]

        recommendations = []
        for _, row in recommendations_df.iterrows():
            recommendations.append(
                Recommendation(
                    storyId=UUID(row["storyId"]),
                    title=row["title"],
                    genres=row["genres"],
                    language=row["language"],
                    ageRating=row["ageRating"],
                )
            )

        return recommendations

    def recommend(
        self,
        user_id: str,
        top_n: int = 5,
        filter_language: bool = True,
        language: Annotated[str, None] = None,
    ) -> List[Recommendation]:
        """Generate recommendations with language enforcement"""
        if user_id not in self.user_id_map:
            return self.get_popular_recommendations(top_n, language)

        user_idx: int = self.user_id_map[user_id]
        user_lang: str = self.dm.users[self.dm.users["userId"] == user_id][
            "preferredReadingLanguage"
        ].iloc[0]

        # Filter items by language
        if filter_language:
            candidate_items = self.dm.stories[self.dm.stories["language"] == user_lang][
                "storyId"
            ]
        else:
            candidate_items = self.dm.stories["storyId"]

        # Remove already interacted items
        known_items: Set[str] = self._get_known_items(user_id)
        candidate_items = candidate_items[~candidate_items.isin(known_items)]

        # Get scores
        item_indices: List[int] = [
            self.item_id_map[item]
            for item in candidate_items
            if item in self.item_id_map
        ]
        scores: np.ndarray = self.model.predict(
            user_idx,
            item_indices,
            user_features=self.user_features,
            item_features=self.item_features,
        )

        # Get top recommendations
        top_indices: np.ndarray = np.argsort(-scores)[:top_n]
        recommendations_df: pd.DataFrame = self.dm.stories[
            self.dm.stories["storyId"].isin(
                [candidate_items.iloc[i] for i in top_indices]
            )
        ]
        recommendations = []
        for _, row in recommendations_df.iterrows():
            recommendations.append(
                Recommendation(
                    storyId=UUID(row["storyId"]),
                    title=row["title"],
                    genres=row["genres"],
                    language=row["language"],
                    ageRating=row["ageRating"],
                )
            )

        return recommendations

    def _get_known_items(self, user_id: str) -> Set[str]:
        """Retrieve items the user has already interacted with"""
        rated: Set[str] = set()
        if self.dm.ratings is not None:
            rated = set(
                self.dm.ratings[self.dm.ratings["userId"] == user_id]["publicationId"]
            )
        read: Set[str] = set()
        if self.dm.behavior is not None:
            read = set(
                self.dm.behavior[self.dm.behavior["userId"] == user_id]["reads"]
                .explode()
                .apply(self._extract_publication_id)
            )
        return rated | read
