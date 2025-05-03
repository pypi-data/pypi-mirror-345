import os
import pytest
from models.recommendation import Recommendation
from src.recommender.data_manager import DataManager
from src.recommender.recommender_system import RecommenderSystem

# Constants for test data paths
TESTS_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TESTS_DIR, "data")
STORY_PATH = os.path.join(TEST_DATA_DIR, "story_dataset.csv")
USER_PATH = os.path.join(TEST_DATA_DIR, "user_dataset.csv")
RATING_PATH = os.path.join(TEST_DATA_DIR, "simple_rating_dataset.csv")
BEHAVIOR_PATH = os.path.join(TEST_DATA_DIR, "behavioral_dataset.csv")


@pytest.fixture
def data_manager() -> DataManager:
    """Create and load the DataManager with test data"""
    dm = DataManager(
        story_path=STORY_PATH,
        user_path=USER_PATH,
        rating_path=RATING_PATH,
        behavior_path=BEHAVIOR_PATH,
    )
    dm.load_data()
    return dm


@pytest.fixture
def trained_recomender(data_manager) -> RecommenderSystem:
    recommender = RecommenderSystem(data_manager)
    recommender.prepare_dataset()
    recommender.train_model(epochs=3)
    return recommender


def test_data_manager_loads_data(data_manager):
    """Test that DataManager loads data correctly"""
    assert data_manager.stories is not None
    assert data_manager.users is not None
    assert data_manager.ratings is not None
    assert data_manager.behavior is not None
    assert len(data_manager.stories) > 0
    assert len(data_manager.users) > 0


def test_recommender_initialization(data_manager):
    """Test that RecommenderSystem initializes correctly"""
    recommender = RecommenderSystem(data_manager)
    assert recommender.dm is not None
    assert recommender.model is None  # Not trained yet


def test_prepare_dataset(data_manager):
    """Test that dataset preparation works"""
    recommender = RecommenderSystem(data_manager)
    recommender.prepare_dataset()

    # Check that dataset components were created
    assert recommender.interactions is not None
    assert recommender.user_id_map is not None
    assert recommender.item_id_map is not None


def test_model_save_and_load(tmpdir, trained_recomender):
    """Test that model can be saved and loaded"""

    save_path = trained_recomender.save_model(save_dir=str(tmpdir))
    assert os.path.exists(save_path)

    loaded_recommender = RecommenderSystem.load_model(save_path)
    assert isinstance(loaded_recommender, RecommenderSystem)
    assert loaded_recommender.model is not None


def test_recommendations_for_known_user(data_manager, trained_recomender):
    """Test getting recommendations for a known user"""

    known_user_id = data_manager.users["userId"].iloc[0]
    recommendations = trained_recomender.recommend(known_user_id, top_n=3)

    # Check recommendations format
    assert isinstance(recommendations, list)
    assert all(isinstance(rec, Recommendation) for rec in recommendations)
    assert len(recommendations) <= 3


def test_recommendations_for_unknown_user(data_manager, trained_recomender):
    """Test getting recommendations for an unknown user"""

    # Get recommendations for unknown user
    recommendations = trained_recomender.recommend("UNKNOWN", top_n=3)

    # Check recommendations format
    assert isinstance(recommendations, list)
    assert all(isinstance(rec, Recommendation) for rec in recommendations)
    assert len(recommendations) <= 3


def test_language_filtered_recommendations(data_manager, trained_recomender):
    """Test that language filtering works in recommendations"""

    known_user_id = data_manager.users["userId"].iloc[0]
    user_lang = data_manager.users[data_manager.users["userId"] == known_user_id][
        "preferredReadingLanguage"
    ].iloc[0]

    recommendations = trained_recomender.recommend(
        known_user_id, top_n=3, filter_language=True
    )

    if recommendations:
        assert all(rec.language == user_lang for rec in recommendations)
