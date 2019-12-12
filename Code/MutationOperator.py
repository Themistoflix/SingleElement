import numpy as np


class MutationOperator:
    def __init__(self, max_exchanges):
        self.max_exchanges = max_exchanges
        self.probability_distribution = np.array([1. / (n ** (3. / 2.)) for n in range(1, max_exchanges + 1, 1)])
        self.probability_distribution = self.probability_distribution / np.sum(self.probability_distribution)

    def random_mutation(self, particle):
        symbol1 = particle.atoms.getSymbols()[0]
        symbol2 = particle.atoms.getSymbols()[1]

        n_exchanges = 1 + np.random.choice(self.max_exchanges, p=self.probability_distribution)

        symbol1_indices = np.random.choice(particle.atoms.getIndicesBySymbol(symbol1), n_exchanges, replace=False)
        symbol2_indices = np.random.choice(particle.atoms.getIndicesBySymbol(symbol2), n_exchanges, replace=False)

        particle.atoms.swapAtoms(zip(symbol1_indices, symbol2_indices))

        return particle, zip(symbol1_indices, symbol2_indices)

    def revert_mutation(self, particle, swaps):
        symbol1_indices, symbol2_indices = zip(*swaps)
        particle.atoms.swapAtoms(zip(symbol2_indices, symbol1_indices))

        return particle

    def gradient_descent_mutation(self,  particle, energy_coefficients):
        # will only work for bimetallic nanoparticles
        def get_n_distinct_atomic_environments():
            feature_vector = particle.getFeatureVector()
            n_distinct_environments = int(len(feature_vector) / 2)

            return n_distinct_environments

        def get_feature_index_of_other_element(symbol1_feature_index):
            feature_vector = particle.getFeatureVector()
            n_distinct_environments = int(len(feature_vector) / 2)
            symbol2_feature_index = symbol1_feature_index + n_distinct_environments

            return symbol2_feature_index


        def compute_energy_gain_for_equal_env_swaps():
            n_distinct_environments = get_n_distinct_atomic_environments()

            energy_gains = list()
            for symbol1_feature_index in range(n_distinct_environments):
                symbol2_feature_index = get_feature_index_of_other_element(symbol1_feature_index)
                energy_gain_per_swap = energy_coefficients[symbol1_feature_index] - energy_coefficients[symbol2_feature_index]
                energy_gains.append(energy_gain_per_swap)  # positive entries mean energy gain

            return energy_gains

        def expectation_value_of_dice(n):
            return np.cumsum(np.array(range(n + 1))) / n

        energy_gains = compute_energy_gain_for_equal_env_swaps()

        features_as_index_lists = particle.getFeaturesAsIndexLists()
        n_distinct_environments = get_n_distinct_atomic_environments()

        expected_energy_gains = list()
        for symbol1_feature_index in range(n_distinct_environments):
            symbol2_feature_index = get_feature_index_of_other_element(symbol1_feature_index)
            max_swaps = min(len(features_as_index_lists[symbol1_feature_index]), len(features_as_index_lists[symbol2_feature_index]))
            expected_energy_gain = expectation_value_of_dice(max_swaps)*energy_gains[symbol1_feature_index]
            expected_energy_gains.append(expected_energy_gain)

        symbol1_feature_index = expected_energy_gains.index(max(expected_energy_gains))
        symbol2_feature_index = get_feature_index_of_other_element(symbol1_feature_index)
        max_swaps = min(len(features_as_index_lists[symbol1_feature_index]), len(features_as_index_lists[symbol2_feature_index]))
        n_swaps = np.random.randint(1, max_swaps + 1)  # randint upper limit is exclusive

        symbol1_indices = np.random.choice(features_as_index_lists[symbol1_feature_index], n_swaps, replace=False)
        symbol2_indices = np.random.choice(features_as_index_lists[symbol2_feature_index], n_swaps, replace=False)

        swaps = zip(symbol1_indices, symbol2_indices)
        particle.atoms.swapAtoms(swaps)

        return particle, swaps


            





