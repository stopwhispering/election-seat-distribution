from election_seats_distribution.distributors import Distributor


class Comparator:
    """
    Compare different Distribution Algorithms
    """
    def __init__(self, distributors: tuple[Distributor, ...]):
        self.distributors = distributors

    def compare(self,
                candidates_votes_input: tuple[tuple[str, int], ...],
                seats_count_input: int,
                threshold_input: float):
        print(f'Votes per candidate:   {candidates_votes_input}')
        print(f'Seats to be allocated: {seats_count_input}')
        print(f'Threshold:             {threshold_input} %')
        for distributor in self.distributors:
            distributor.calc(candidates_votes_input, seats_count_input, threshold_input)
            print(f'{type(distributor).__name__ :12} -> {distributor.seats}')