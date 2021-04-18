from election_seats_distribution.comparator import Comparator
from election_seats_distribution.distributors import ExactQuotas, Dhondt, SainteLague, HareNiemeyer

if __name__ == '__main__':
    comp = Comparator((ExactQuotas(), Dhondt(), SainteLague(), HareNiemeyer()))
    comp.compare((('A', 517), ('B', 133), ('C', 350)), 20, 5.0)  # d'Hondt != Sainte-Lague/Hare-Niemeyer
    comp.compare((('A', 43), ('B', 33), ('C', 12), ('D', 8), ('E', 4)), 10, 0.)  # all different
