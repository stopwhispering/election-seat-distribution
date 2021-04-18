from abc import ABC
from collections import Counter


class Distributor(ABC):
    _seats: dict[str, int] = {}

    @property
    def seats(self) -> dict[str, int]:
        return self._seats

    def calc(self,
             candidates_votes: tuple[tuple[str, int], ...],
             seats_count: int,
             threshold: float):
        pass

    @staticmethod
    def get_votes_sorted(candidates_votes: tuple[tuple[str, int], ...],
                         threshold: float) -> list[tuple[str, int], ...]:
        # Calc total, sort out candidates failing minimum, and sort by number of votes
        votes_total = sum(c[1] for c in candidates_votes)
        votes_minimum = (votes_total * threshold / 100) - 1
        candidates_meeting_minimum = [c for c in candidates_votes if c[1] >= votes_minimum]
        return sorted(candidates_meeting_minimum, key=lambda x: x[1], reverse=True)


class ExactQuotas(Distributor):
    def calc(self,
             candidates_votes: tuple[tuple[str, int], ...],
             seats_count: int,
             threshold: float):
        # Get candidates matching minimum votes and sorted by number of votes
        candidates_sorted = self.get_votes_sorted(candidates_votes, threshold)

        # Just return the percentages, considering only candidates meeting minimum number of votes
        votes_total_meeting_minimum = sum(c[1] for c in candidates_sorted)

        self._seats = {c[0]: round(c[1] / votes_total_meeting_minimum * seats_count, 2) for c in candidates_sorted}
        return self._seats


class Dhondt(Distributor):
    """
    Calculate Candidate Seats using d'Hondt Algorithm
    """

    def calc(self,
             candidates_votes: tuple[tuple[str, int], ...],
             seats_count: int,
             threshold: float):
        """Perform the calculation"""
        # Get candidates matching minimum votes and sorted by number of votes
        candidates_sorted = self.get_votes_sorted(candidates_votes, threshold)

        # determine seats by calculating the highest quotients ...
        quotients: list[tuple[str, float], ...] = []
        for r in range(1, seats_count + 1):
            for candidate in candidates_sorted:
                quotients.append((candidate[0], candidate[1] / r))

        # and distributing one by one
        quotients_sorted = sorted(quotients, key=lambda x: x[1], reverse=True)
        candidates_seats = [q[0] for q in quotients_sorted[:seats_count]]
        self._seats = dict(Counter(candidates_seats))

        return self._seats


class SainteLague(Distributor):
    """
    Calculate Candidate Seats using Sainte-Laguë Algorithm
    (similar to d'Hondt but calculating quotients with different divisors)
    """

    def calc(self,
             candidates_votes: tuple[tuple[str, int], ...],
             seats_count: int,
             threshold: float):
        """Perform the calculation"""
        # Get candidates matching minimum votes and sorted by number of votes
        candidates_sorted = self.get_votes_sorted(candidates_votes, threshold)

        # determine seats by calculating the highest quotients ... (e.g. 0.5, 1.5, 2.5, 3.5 for 3 seats)
        divisors = [s + .5 for s in range(seats_count)]
        quotients: list[tuple[str, float], ...] = []
        for r in divisors:
            for candidate in candidates_sorted:
                quotients.append((candidate[0], candidate[1] / r))

        # and distributing one by one
        quotients_sorted = sorted(quotients, key=lambda x: x[1], reverse=True)
        candidates_seats = [q[0] for q in quotients_sorted[:seats_count]]
        self._seats = dict(Counter(candidates_seats))

        return self._seats


class HareNiemeyer(Distributor):
    """
    Calculate Candidate Seats using Hare-Niemeyer Algorithm
    (quota algorithm, unlike d'Hondt and Sainte-Laguë)
    """

    def calc(self,
             candidates_votes: tuple[tuple[str, int], ...],
             seats_count: int,
             threshold: float):
        """Perform the calculation"""
        # Get candidates matching minimum votes and sorted by number of votes
        candidates_sorted = self.get_votes_sorted(candidates_votes, threshold)

        # determine quotas and seats (first round) by rounding down
        votes_total_meeting_minimum = sum(c[1] for c in candidates_sorted)
        seats_first_round = {c[0]: (c[1] * seats_count) // votes_total_meeting_minimum
                             for c in candidates_sorted}
        remainders = ((c[0], (c[1] * seats_count) % votes_total_meeting_minimum)
                      for c in candidates_sorted)

        # distribute remaining seats by highest remainders
        seats_remaining = seats_count - sum(seats_first_round.values())
        remainders_sorted = sorted(remainders, key=lambda x: x[1], reverse=True)
        remaining_seats_allocated = [r[0] for r in remainders_sorted[:seats_remaining]]
        seats = {candidate: seats + (1 if candidate in remaining_seats_allocated else 0)
                 for candidate, seats in seats_first_round.items()}
        self._seats = {c: s for c, s in seats.items() if s > 0}
        return self._seats