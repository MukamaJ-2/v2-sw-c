from e_voting.models.voting_station import VotingStation


class StationService:
    """Business logic for voting station management."""

    def __init__(self, store):
        self._store = store

    def create(self, name, location, region, capacity, supervisor, contact,
               opening_time, closing_time, created_by):
        station_id = self._store.next_id("station")
        station = VotingStation(
            station_id=station_id,
            name=name,
            location=location,
            region=region,
            capacity=capacity,
            supervisor=supervisor,
            contact=contact,
            opening_time=opening_time,
            closing_time=closing_time,
            created_by=created_by,
        )
        self._store.voting_stations[station_id] = station
        self._store.log_action(
            "CREATE_STATION", created_by,
            f"Created station: {name} (ID: {station_id})"
        )
        self._store.save()
        return station

    def get_all(self):
        return self._store.voting_stations

    def get(self, station_id):
        return self._store.voting_stations.get(station_id)

    def get_active(self):
        return {
            sid: s for sid, s in self._store.voting_stations.items()
            if s.is_active
        }

    def get_registered_voter_count(self, station_id):
        return sum(
            1 for v in self._store.voters.values()
            if v.station_id == station_id
        )

    def update(self, station_id, updates, updated_by):
        station = self._store.voting_stations.get(station_id)
        if not station:
            return None
        for key, value in updates.items():
            if value is not None and hasattr(station, key):
                setattr(station, key, value)
        self._store.log_action(
            "UPDATE_STATION", updated_by,
            f"Updated station: {station.name} (ID: {station_id})"
        )
        self._store.save()
        return station

    def deactivate(self, station_id, deactivated_by):
        station = self._store.voting_stations.get(station_id)
        if not station:
            return False
        station.deactivate()
        self._store.log_action(
            "DELETE_STATION", deactivated_by,
            f"Deactivated station: {station.name}"
        )
        self._store.save()
        return True
