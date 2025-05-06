import argparse
import numpy as np
import pandas as pd

from cp2025.algorithms.AggregationKAnonymityTimeOptimal import AggregationKAnonymityTimeOptimal
from cp2025.algorithms.AggregationLDiversityTimeOptimal import AggregationLDiversityTimeOptimal
from cp2025.algorithms.Datafly import Datafly
from cp2025.algorithms.GeneralizationGreedyByOneEqualSizedGroups import GeneralizationGreedyByOneEqualSizedGroups
from cp2025.algorithms.GeneralizationKAnonymityTimeOptimal import GeneralizationKAnonymityTimeOptimal
from cp2025.algorithms.GeneralizationLDiversityTimeOptimal import GeneralizationLDiversityTimeOptimal
from cp2025.algorithms.groupjoin import *
from cp2025.algorithms.IdentifierHasher import IdentifierHasher
from cp2025.algorithms.RandomizationDepersonalizator import RandomizationBaselineDepersonalizator
from cp2025.algorithms.Shuffler import Shuffler
from cp2025.algorithms.ShufflerInBatches import ShufflerInBatches
from cp2025.algorithms.SuppressionKAnonymityBaseline import SuppressionKAnonymityBaseline
from cp2025.algorithms.SuppressionKAnonymityTimeOptimal import SuppressionKAnonymityTimeOptimal
from cp2025.algorithms.SuppressionLDiversityBaseline import SuppressionLDiversityBaseline
from cp2025.algorithms.SuppressionLDiversityTimeOptimal import SuppressionLDiversityTimeOptimal
from cp2025.algorithms.SuppressionTClosenessBaseline import SuppressionTClosenessBaseline

class AlgorithmRunner:
    def __init__(self, df, i_ids, qi_ids, s_ids):
        self.df = df
        self.i_ids = i_ids
        self.qi_ids = qi_ids
        self.s_ids = s_ids

    def run(self, algorithm):
        return algorithm.depersonalize(self.df, identifiers_ids=self.i_ids, quasi_identifiers_ids=self.qi_ids, sensitives_ids=self.s_ids)[0]

def main():

    parser = argparse.ArgumentParser(description='Depersonalization script')

    parser.add_argument('-i','--input', help='input csv file with dataset',required=True)
    parser.add_argument('-f','--header', help='input file stores table with header', action="store_true")
    parser.add_argument('-o','--output', help='output csv file (console by default)')
    parser.add_argument('-a','--algorithm', help='algorithm name from: baseline, time_optimal, datafly, greedy, group_join, hasher, randomization, shuffler, batch_shuffler (group_join by default)')
    parser.add_argument('-m','--metric', choices=['k', 'l', 't'], help='metric from k, l, t corresponding to k-anonymity, l-diversity and t-closeness (k-anonymity by default)')
    parser.add_argument('-r','--method', choices=['s', 'g', 'a'], help='method from s, g, f corresponding to suppression, generalization, aggregation (suppression by default)')
    parser.add_argument('-k', help='k for k-anonymity')
    parser.add_argument('-l', help='l for l-diversity')
    parser.add_argument('-t', help='t for t-closeness')
    parser.add_argument('--qi_ids', help='quasi-identifiers ids separated by comma ("1,3,5") or "left"')
    parser.add_argument('--i_ids', help='identifiers ids separated by comma ("1,3,5") or "left"')
    parser.add_argument('--s_ids', help='sensitives ids separated by comma ("1,3,5") or "left"')
    parser.add_argument('--types', help='quasi-identifiers types, for example: "rour" for "real, ordered, unordered, real"')
    parser.add_argument('--s_types', help='sensitives types, for example: "rour" for "real, ordered, unordered, real" (is used in t-closeness algorithms)')
    parser.add_argument('-s','--seed', help='random seed')
    parser.add_argument('--k_suppressed_lines', help='maximal number of suppressed lines for Datafly algorithm')
    parser.add_argument('--scale', help='scale for randomization algorithm')
    parser.add_argument('--cols2shuffle', help='columns to shuffle with shuffler, separated by comma ("1,3,5")')

    args = parser.parse_args()

    header_flag = args.header
    if not header_flag:
        header_flag = None

    df = np.genfromtxt(args.input, delimiter=',', names=header_flag)

    header = None
    if args.header:
        header = df.dtype.names

    if header_flag is not None:
        df = np.array(df.tolist())

    qi_types = None
    if args.types is not None:
        qi_types = []
        for c in args.types:
            if c == 'r':
                qi_types.append('real')
            elif c == 'o':
                qi_types.append('ordered')
            elif c == 'u':
                qi_types.append('unordered')
            else:
                raise ValueError('Unknown column type')

    s_types = None
    if args.s_types is not None:
        s_types = []
        for c in args.s_types:
            if c == 'r':
                s_types.append('real')
            elif c == 'o':
                s_types.append('ordered')
            elif c == 'u':
                s_types.append('unordered')
            else:
                raise ValueError('Unknown column type')

    i_ids = None
    if args.i_ids is not None:
        if args.i_ids == 'left':
            i_ids = 'left'
        else:
            i_ids = []
            for i_id in args.i_ids.split(','):
                i_ids.append(int(i_id))

    qi_ids = None
    if args.qi_ids is not None:
        if args.qi_ids == 'left':
            qi_ids = 'left'
        else:
            qi_ids = []
            for qi_id in args.qi_ids.split(','):
                qi_ids.append(int(qi_id))
    else:
        qi_ids = "left"

    s_ids = None
    if args.s_ids is not None:
        if args.s_ids == 'left':
            s_ids = 'left'
        else:
            s_ids = []
            for s_id in args.s_ids.split(','):
                s_ids.append(int(s_id))

    cols2shuffle = None
    if args.cols2shuffle is not None:
        cols2shuffle = []
        for col2shuffle in args.cols2shuffle.split(','):
            cols2shuffle.append(int(col2shuffle))

    metric = args.metric
    if metric is None:
        metric = 'k'

    method = args.method
    if method is None:
        method = 's'

    if args.metric == 'k':
        if args.k is None:
            raise ValueError('k for k-anonymity must be specified')

    if args.metric == 'l':
        if args.l is None or args.k is None:
            raise ValueError('k and l for l-diversity must be specified')

    if args.metric == 't':
        if args.t is None or args.k is None:
            raise ValueError('k and t for t-closeness must be specified')

    seed = None
    if args.seed is not None:
        seed = int(args.seed)

    k_suppressed_lines = None
    if args.k_suppressed_lines is not None:
        k_suppressed_lines = int(args.k_suppressed_lines)

    scale = None
    if args.scale is not None:
        scale = float(args.scale)

    runner = AlgorithmRunner(df, i_ids, qi_ids, s_ids)

    match args.algorithm:
        case "baseline":
            match metric:
                case "k":
                    depersonalized_df = runner.run(SuppressionKAnonymityBaseline(int(args.k)))
                case "l":
                    depersonalized_df = runner.run(SuppressionLDiversityBaseline(int(args.k), int(args.l)))
                case "t":
                    depersonalized_df= runner.run(SuppressionTClosenessBaseline(int(args.k), float(args.t), sensitives_types=s_types))
        case "time_optimal":
            match metric:
                case "k":
                    match method:
                        case "s":
                            depersonalized_df = runner.run(SuppressionKAnonymityTimeOptimal(int(args.k)))
                        case "g":
                            depersonalized_df = runner.run(GeneralizationKAnonymityTimeOptimal(int(args.k), quasi_identifiers_types=qi_types))
                        case "a":
                            depersonalized_df = runner.run(AggregationKAnonymityTimeOptimal(int(args.k), quasi_identifiers_types=qi_types))
                case "l":
                    match method:
                        case "s":
                            depersonalized_df = runner.run(SuppressionLDiversityTimeOptimal(int(args.k), int(args.l)))
                        case "g":
                            depersonalized_df = runner.run(GeneralizationLDiversityTimeOptimal(int(args.k), int(args.l), quasi_identifiers_types=qi_types))
                        case "a":
                            depersonalized_df = runner.run(AggregationLDiversityTimeOptimal(int(args.k), int(args.l), quasi_identifiers_types=qi_types))
                case "t":
                    raise ValueError("Time optimal cannot be implemented for t-closeness")
        case "datafly":
            depersonalized_df = runner.run(Datafly(int(args.k), quasi_identifiers_types=qi_types, k_suppressed_lines=k_suppressed_lines))
        case "greedy":
            depersonalized_df = runner.run(GeneralizationGreedyByOneEqualSizedGroups(int(args.k), quasi_identifiers_types=qi_types))
        case "group_join":
            match method:
                case "s":
                    gjmth = GroupJoinSuppression()
                case "g":
                    gjmth = GroupJoinGeneralization(qi_types)
                case "a":
                    gjmth = GroupJoinAggregation(qi_types)
            match metric:
                case "k":
                    gjmtc = GroupJoinKAnonymity(int(args.k), seed = seed)
                case "l":
                    gjmtc = GroupJoinLDiversity(int(args.k), int(args.l), seed = seed)
                case "t":
                    gjmtc = GroupJoinTCloseness(int(args.k), int(args.t), sensitives_types = s_types, seed = seed)
            depersonalized_df = runner.run(GroupJoinDepersonalizator(gjmth, gjmtc))
        case "hasher":
            depersonalized_df = runner.run(IdentifierHasher())
        case "randomization":
            depersonalized_df = runner.run(RandomizationBaselineDepersonalizator(quasi_identifiers_types=qi_types, seed=seed, scale=scale))
        case "shuffler":
            depersonalized_df = runner.run(Shuffler(seed=seed, columns_ids_to_shuffle=cols2shuffle))
        case "batch_shuffler":
            depersonalized_df = runner.run(ShufflerInBatches(seed=seed, columns_ids_to_shuffle=cols2shuffle))
        case _:
            raise ValueError(f"Unrecognized algorithm: {args.algorithm}")

    if args.output is None:
        if args.header:
            print(pd.DataFrame(depersonalized_df.astype(np.dtype(str)), columns=header))
        else:
            print(pd.DataFrame(depersonalized_df.astype(np.dtype(str))))
    else:
        if args.header:
            np.savetxt(args.output, depersonalized_df, delimiter=",", header=",".join(header), comments='', fmt="%s")
        else:
            np.savetxt(args.output, depersonalized_df, delimiter=",", fmt="%s")

if __name__ == "__main__":
    main()