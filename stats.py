import os
import ast
import numpy as np

from natural_lang.tree import *
from config import parser
from utils.io import deserialize_from_file

splits = [
    'train',
    'test',
    'dev'
]


def number_of_ast_nodes_rec(node):
    return 1 + sum(map(number_of_ast_nodes_rec, ast.iter_child_nodes(node)))


def number_of_ast_nodes(code):
    root_node = ast.parse(code)
    return number_of_ast_nodes_rec(root_node)


def avg_and_max_number_of_ast_nodes(data_dir):
    nodes_numbers = []
    for split in splits:
        file = os.path.join(data_dir, '{}/{}.out.bin'.format(split, split))
        codes = deserialize_from_file(file)
        for code in codes:
            nodes_numbers.append(number_of_ast_nodes(code))

    return np.mean(nodes_numbers), max(nodes_numbers), nodes_numbers


def avg_and_max_number_char_in_code(data_dir):
    char_len = []
    for split in splits:
        file = os.path.join(data_dir, '{}/{}.out.bin'.format(split, split))
        codes = deserialize_from_file(file)
        for code in codes:
            char_len.append(len(code))

    return np.mean(char_len), max(char_len), char_len


def avg_and_max_number_of_actions(data_dir):
    nodes_numbers = []
    for split in splits:
        file = os.path.join(data_dir, '{}/{}.out.bin'.format(split, split))
        codes = deserialize_from_file(file)
        for code in codes:
            nodes_numbers.append(number_of_ast_nodes(code))

    return np.mean(nodes_numbers), max(nodes_numbers), nodes_numbers


def avg_and_max_nodes(file):
    with open(file, 'r') as f:
        lines = f.readlines()
        count = len(lines)
        lens = [len(line.split()) for line in lines]
        max_nodes = max(lens)
        count_nodes = sum(lens)
    return count, count_nodes, max_nodes, lens


def collect_description_stats(data_dir):
    nodes = [1.e-7, 0.0]
    for split in splits:
        token_file = os.path.join(data_dir, '{}/{}.in.tokens'.format(split, split))
        count, tokens_count, tokens_max, lens = avg_and_max_nodes(token_file)
        nodes[0] += count
        nodes[1] += tokens_count
    tokens_avg = nodes[1]/nodes[0]
    return tokens_avg, tokens_max, lens


def read_line_from_file(file, line):
    with open(file, 'r') as f:
        _ = [f.readline() for _ in range(line)]
        return f.readline()


def draw_tree(parents_path, cat_path, token_path, line, out_path):
    hs_tree_line = read_line_from_file(parents_path, line)
    hs_tokens = read_line_from_file(token_path, line).split()
    hs_categories = read_line_from_file(cat_path, line).split()

    hs_labels = []
    for i in range(len(hs_categories)):
        label = hs_categories[i]
        if len(hs_tokens) > i and label != hs_tokens[i]:
            label += ' - ' + hs_tokens[i]
        hs_labels.append(label)

    hs_tree = read_tree(hs_tree_line, hs_labels)
    hs_tree.savefig(out_path)


def draw_trees(data_dir, line):
    hs_tree_path = os.path.join(data_dir, 'dev/dev.in.constituency_parents')
    hs_category_path = os.path.join(data_dir, 'dev/dev.in.constituency_categories')
    hs_tokens_path = os.path.join(data_dir, 'dev/dev.in.tokens')
    out_path = os.path.join(data_dir, 'dev/pcfg_tree_example.png')

    draw_tree(hs_tree_path, hs_category_path, hs_tokens_path, line, out_path)

    hs_tree_path = os.path.join(data_dir, 'dev/dev.in.dependency_parents')
    hs_category_path = os.path.join(data_dir, 'dev/dev.in.dependency_rels')
    out_path = os.path.join(data_dir, 'dev/dependency_tree_example.png')

    draw_tree(hs_tree_path, hs_category_path, hs_tokens_path, line, out_path)

    hs_tree_path = os.path.join(data_dir, 'dev/dev.in.ccg_parents')
    hs_category_path = os.path.join(data_dir, 'dev/dev.in.ccg_categories')
    out_path = os.path.join(data_dir, 'dev/ccg_tree_example.png')

    draw_tree(hs_tree_path, hs_category_path, hs_tokens_path, line, out_path)


def avg_nodes_dataset(data_dir, parents):
    count, count_nodes = 0.0, 0.0
    for split in splits:
        file = os.path.join(data_dir, '{}/{}.in.{}_parents'.format(split, split, parents))
        count_, count_nodes_, max_, lens = avg_and_max_nodes(file)
        count += count_
        count_nodes += count_nodes_

    avg = count_nodes/count

    return avg, max_, lens


if __name__ == '__main__':
    args = parser.parse_args()
    # draw_trees(args.data_dir)

    tokens_avg, tokens_max, lens = collect_description_stats(args.data_dir)
    print("Avg. tokens: {},\n"
          "Max. tokens: {}.".format(tokens_avg, tokens_max))

    dependency_avg, dependency_max, dependency_lens = avg_nodes_dataset(args.data_dir, "dependency")
    pcfg_avg, pcfg_max, pcfg_lens = avg_nodes_dataset(args.data_dir, "constituency")
    ccg_avg, ccg_max, ccg_lens = avg_nodes_dataset(args.data_dir, "ccg")

    print("Average nodes in dependency trees: {}\n"
          "Average nodes in constituency trees: {}\n"
          "Average nodes in CCG trees: {}".format(dependency_avg, pcfg_avg, ccg_avg))

    print("Max nodes in dependency trees: {}\n"
          "Max nodes in constituency trees: {}\n"
          "Max nodes in CCG trees: {}".format(dependency_max, pcfg_max, ccg_max))

    # limit = 70
    # dependency_gt = len(list(filter(lambda l: l > limit, dependency_lens)))
    # pcfg_gt = len(list(filter(lambda l: l > limit, pcfg_lens)))
    # ccg_gt = len(list(filter(lambda l: l > limit, ccg_lens)))
    #
    # print("Number of dependency trees longer than {}: {}.".format(limit, dependency_gt))
    # print("Number of pcfg trees longer than {}: {}.".format(limit, pcfg_gt))
    # print("Number of ccg trees longer than {}: {}.".format(limit, ccg_gt))

    ast_avg, ast_max, ast_all = avg_and_max_number_of_ast_nodes(args.data_dir)

    print("Avg. number of nodes: {}.".format(ast_avg))
    print("Max. number of nodes: {}.".format(ast_max))

    char_avg, char_max, char_all = avg_and_max_number_char_in_code(args.data_dir)

    print("Avg. number of char. in code: {}.".format(char_avg))
    print("Max. number of char. in code: {}.".format(char_max))

    # actions_avg, actions_max, actions_all = avg_and_max_number_of_actions(args.data_dir)
