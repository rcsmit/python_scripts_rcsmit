def sublist(orig_list, list_of_subs, max_items_per_list):
    # https://stackoverflow.com/questions/52111627/how-to-split-a-list-into-multiple-lists-with-certain-ranges

    def sublist_generator():
        for sublist in list_of_subs:
            yield sublist

    sublist = sublist_generator()
    current_sublist = next(sublist)
    for i, element in enumerate(orig_list):
        current_sublist.append(element)

        if len(current_sublist) == max_items_per_list and (i != len(orig_list)-1): # current list is full
            current_sublist = next(sublist) # so let current point to the next list

import random
start = 1
stop = random.randint(2, 85) # generate random int inclusively 2 and 85
codes = [x for x in range(1, 41)] # stop is exclusive: range(1, 85) == [1, 2, ..., 84]

a, b, c, d = [], [], [], []
sublists = [a, b, c, d] # *1
print (len(codes))
sublist(codes, sublists, 10)
for sublist in sublists:
    print(sublist)
print (b)