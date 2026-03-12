from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evoting.domain.state import SystemState
from evoting.repository.storage import JsonStorageRepository
from evoting.services.audit_service import AuditService
from evoting.services.results_service import ResultsService
from evoting.ui.console import Console


class StorageAndResultsTests(unittest.TestCase):
    def test_storage_round_trip_preserves_integer_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JsonStorageRepository(Path(temp_dir) / "evoting_data.json")
            state = SystemState()
            state.candidates[7] = {"id": 7, "full_name": "Alice"}
            state.candidate_id_counter = 8
            state.votes.append({"vote_id": "v1", "poll_id": 1, "position_id": 2})

            storage.save(state)
            reloaded = storage.load()

        self.assertIn(7, reloaded.candidates)
        self.assertEqual(reloaded.candidate_id_counter, 8)
        self.assertEqual(reloaded.votes[0]["vote_id"], "v1")

    def test_tally_votes_for_position_counts_votes_and_abstentions(self) -> None:
        state = SystemState()
        state.votes = [
            {
                "vote_id": "a",
                "poll_id": 1,
                "position_id": 10,
                "candidate_id": 100,
                "voter_id": 1,
                "station_id": 5,
                "timestamp": "now",
                "abstained": False,
            },
            {
                "vote_id": "b",
                "poll_id": 1,
                "position_id": 10,
                "candidate_id": 100,
                "voter_id": 2,
                "station_id": 5,
                "timestamp": "now",
                "abstained": False,
            },
            {
                "vote_id": "c",
                "poll_id": 1,
                "position_id": 10,
                "candidate_id": 101,
                "voter_id": 3,
                "station_id": 6,
                "timestamp": "now",
                "abstained": False,
            },
            {
                "vote_id": "d",
                "poll_id": 1,
                "position_id": 10,
                "candidate_id": None,
                "voter_id": 4,
                "station_id": 6,
                "timestamp": "now",
                "abstained": True,
            },
        ]
        results_service = ResultsService(
            state=state,
            console=Console(),
            storage=JsonStorageRepository(Path(tempfile.gettempdir()) / "unused.json"),
            audit=AuditService(state),
        )

        tally = results_service.tally_votes_for_position(1, 10)
        station_tally = results_service.tally_votes_for_position(1, 10, station_id=5)

        self.assertEqual(tally["counts"], {100: 2, 101: 1})
        self.assertEqual(tally["abstentions"], 1)
        self.assertEqual(tally["total"], 4)
        self.assertEqual(station_tally["counts"], {100: 2})
        self.assertEqual(station_tally["abstentions"], 0)
        self.assertEqual(station_tally["total"], 2)


if __name__ == "__main__":
    unittest.main()
