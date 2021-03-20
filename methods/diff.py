def diff_merge(list1: list, list2: list, check, prio):
    sorted_merge = sorted([*list1, *list2], key=lambda k: (k[check], k[prio]), reverse=True)
    # pprint(sorted_merge)
    return [j for i, j in enumerate(sorted_merge)
            if (i > 0) and (sorted_merge[i][check] != sorted_merge[i - 1][check])
            or ((i + 1 < len(sorted_merge))
                and (sorted_merge[i][check] == sorted_merge[i + 1][check])
                and (sorted_merge[i][prio] != sorted_merge[i + 1][prio]))
            ]


def diff_removal(list1: list, list2: list, check, prio):
    sorted_merge = sorted([*list1, *list2], key=lambda k: (k[check], k[prio]))
    # pprint(sorted_merge)
    return [j for i, j in enumerate(sorted_merge)
            if (i > 0) and (sorted_merge[i][check] == sorted_merge[i - 1][check])
            and (sorted_merge[i][prio] != sorted_merge[i - 1][prio])]


'''
downloadable = [url for url in hrefs
                if not url['path'].endswith("/")
                and not any(url['path'].startswith(path) for path in config.data['ignore'])
                and (any(url['path'] == file["path"] and url["time"] > file["time"] for file in self.cache)
                     or not os.path.exists('/'.join([config.data['path'], url['path']]).replace("/", "\\")))]
'''
# import timeit
# left = [{"a": "A", "a2": 111},{"a": "C", "a2": 332},
#         {"a": "B", "a2": 222},
#         ]
# right = [{"a": "A", "a2": 111},
# {"a": "B", "a2": 223},
#          {"a": "C", "a2": 333},
#
#          ]
# ans1 = [{"a": "C", "a2": 333}]
# ans2 = [{"a": "A", "a2": 111},
#         {"a": "B", "a2": 222}]
# #
# print(timeit.timeit(f'{diff_merge(left, right, "a", "a2")}', number=1000000))
# print(timeit.timeit(f'{diff_removal(left, right, "a", "a2")}', number=1000000))
# pprint(diff_merge( right,left, "a", "a2"))
# pprint(diff_removal(right,left,  "a", "a2"))
