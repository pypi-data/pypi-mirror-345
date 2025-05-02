
from collections import defaultdict
from typing import DefaultDict, List

from generalized_geography.common.CDEG_graph import BipartiteNode, CDEGGraph

from .rule import Rule


class WordDict:

    word_dict = DefaultDict[str, DefaultDict[str, List[int]]]
    rule: Rule

    def __init__(self, rule: Rule, words: List[str]):

        self.word_dict = defaultdict(lambda: defaultdict(list))
        self.rule = rule
        for word in words:
            first_char = word[rule.first_index]
            last_char = word[rule.last_index]
            self.word_dict[first_char][last_char].append(word)

    def get_words(self, first_char, last_char) -> List[str]:
        return self.word_dict[first_char][last_char]

    def make_graph(self) -> CDEGGraph:
        graph = CDEGGraph()
        chars = set()

        for char1 in self.word_dict:
            for char2 in self.word_dict[char1]:
                chars.update(char1, char2)

        chan_edges = sum([
            [(BipartiteNode(char, 0), BipartiteNode(chan, 1))
             for chan in self.rule.change_rule(char) if chan in chars]
            for char in chars], [])

        words = [item for subdict in self.word_dict.values()
                 for lst in subdict.values() for item in lst]

        word_edges = [(BipartiteNode(word[0], 1), BipartiteNode(word[-1], 0))
                      for word in words]

        graph.add_edges_from(chan_edges + word_edges)
        return graph
