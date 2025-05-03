import os
from src.recommender.data_manager import DataManager
from src.recommender.recommender_system import RecommenderSystem

# Constants for test data paths
TESTS_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TESTS_DIR, "data")
STORY_PATH = os.path.join(TEST_DATA_DIR, "story_dataset.csv")
USER_PATH = os.path.join(TEST_DATA_DIR, "user_dataset.csv")
RATING_PATH = os.path.join(TEST_DATA_DIR, "simple_rating_dataset.csv")
BEHAVIOR_PATH = os.path.join(TEST_DATA_DIR, "behavioral_dataset.csv")


def test_full_workflow():
    """Test the complete workflow as used in the main script"""
    # Initialize DataManager
    dm = DataManager(
        story_path=STORY_PATH,
        user_path=USER_PATH,
        rating_path=RATING_PATH,
        behavior_path=BEHAVIOR_PATH,
    )
    dm.load_data()

    recommender = RecommenderSystem(dm)
    recommender.prepare_dataset()
    recommender.train_model(epochs=5)

    # Save the model to a temporary directory
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        path = recommender.save_model(save_dir=tmpdir)
        assert os.path.exists(path)

    # Get recommendations for known user
    known_user_id = "00b0024f-d2e1-4b04-b10f-93764e049e90"
    recommendations = recommender.recommend(known_user_id, filter_language=True)
    assert recommendations is not None
    assert len(recommendations) > 0
    print(f"Known user recommendations: {recommendations}")

    model_path = recommender.save_model(save_dir=tmpdir)
    loaded_recommender = RecommenderSystem.load_model(model_path)
    # Compare recommendations for a sample user
    sample_user_id = "00b0024f-d2e1-4b04-b10f-93764e049e90"
    original_recommendations = recommender.recommend(
        sample_user_id, filter_language=True
    )
    loaded_recommendations = loaded_recommender.recommend(
        sample_user_id, filter_language=True
    )

    # Check if recommendations are the same
    assert original_recommendations == (loaded_recommendations)

    # Get recommendations for unknown user
    unknown_recommendations = recommender.recommend("UNKNOWN", filter_language=True)
    assert unknown_recommendations is not None
    assert len(recommendations) > 0
    print(f"Unknown user recommendations: {unknown_recommendations}")
