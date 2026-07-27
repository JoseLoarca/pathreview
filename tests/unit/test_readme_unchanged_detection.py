"""Tests reproducing missing content-hash-based skip detection in ingestion pipeline."""

from unittest.mock import Mock

import pytest

from ingestion.pipeline import IngestionPipeline


@pytest.mark.unit
class TestUnchangedDocumentDetection:
    """Reproduction suite for issue: re-embedding unchanged documents."""

    @pytest.fixture
    def mock_vector_db(self):
        """Create a mock vector database."""
        return Mock()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = Mock()
        session.query = Mock(side_effect=Exception("no such table: IngestedSource"))
        return session

    @pytest.fixture
    def mock_embedding_provider(self):
        """Create a mock embedding provider."""
        provider = Mock()
        provider.embed = Mock(return_value=[[0.1] * 1536])
        return provider

    @pytest.fixture
    def pipeline(self, mock_vector_db, mock_db_session, mock_embedding_provider):
        """Create an IngestionPipeline instance with mocked dependencies."""
        pipeline = IngestionPipeline(
            vector_db=mock_vector_db,
            db_session=mock_db_session,
            embedding_provider=mock_embedding_provider,
        )
        pipeline.batch_processor.process = Mock(return_value=[])
        return pipeline

    def test_reingesting_unchanged_readme_is_not_skipped(self, pipeline):
        """Re-submitting the exact same README content should skip re-embedding, but currently
        doesn't."""
        profile_id = "profile-123"
        repo_name = "my-repo"
        content = "# Hello World\nSame content every time"

        first_result = pipeline.ingest_readme(profile_id, repo_name, content)
        second_result = pipeline.ingest_readme(profile_id, repo_name, content)

        assert first_result.skipped is False
        # BUG: this currently fails because _check_skip never finds a
        # previously recorded source, so unchanged content is re-embedded.
        assert second_result.skipped is True

    def test_reingesting_unchanged_readme_calls_batch_processor_twice(self, pipeline):
        """Unchanged README content triggers embedding generation on every ingest call."""
        profile_id = "profile-123"
        repo_name = "my-repo"
        content = "# Hello World\nSame content every time"

        pipeline.ingest_readme(profile_id, repo_name, content)
        pipeline.ingest_readme(profile_id, repo_name, content)

        # BUG: batch_processor.process should only be called once for unchanged
        # content, but it currently runs on every ingestion.
        assert pipeline.batch_processor.process.call_count == 1

    def test_check_skip_never_finds_existing_source(self, pipeline):
        """_check_skip is a placeholder that never returns a match, so it never skips."""
        result = pipeline._check_skip("readme_profile-123_my-repo_abcdef", "readme")

        # BUG: with no real DB query/record in place, this always returns None.
        assert result is not None

    def test_record_ingested_source_does_not_persist_to_db(self, pipeline, mock_db_session):
        """_record_ingested_source is a placeholder that never writes to the database."""
        pipeline._record_ingested_source(
            "readme_profile-123_my-repo_abcdef", "readme", "profile-123", 3
        )

        # BUG: nothing is ever added or committed to the db_session.
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
