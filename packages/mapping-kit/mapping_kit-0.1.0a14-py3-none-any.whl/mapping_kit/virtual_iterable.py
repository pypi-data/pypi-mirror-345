class VirtualIterable:
    def __init__(self, *args):
        self._real_iterables = args
        self._max_iterables_index = len(args) - 1
        self._curr_iterable_index = 0
        self._curr_iterable_iterator = None

    def __bool__(self):
        return self._max_iterables_index >= 0

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self._curr_iterable_index > self._max_iterables_index:
                self._reset_curr_iterable_vars()
                raise StopIteration

            if self._curr_iterable_iterator is None:
                curr_iterable = self._real_iterables[self._curr_iterable_index]
                if (isinstance(curr_iterable, str)
                        or not hasattr(curr_iterable, "__iter__")):
                    curr_iterable = [curr_iterable]
                self._curr_iterable_iterator = iter(curr_iterable)

            try:
                return next(self._curr_iterable_iterator)
            except StopIteration:
                self._curr_iterable_iterator = None
                self._curr_iterable_index += 1
                continue

    def __len__(self):
        save_curr_iterable_index = self._curr_iterable_index
        save_curr_iterable_iterator = self._curr_iterable_iterator
        self._reset_curr_iterable_vars()

        len_self = 0
        for _ in self:
            len_self += 1

        self._curr_iterable_index = save_curr_iterable_index
        self._curr_iterable_iterator = save_curr_iterable_iterator

        return len_self

    def _reset_curr_iterable_vars(self):
        self._curr_iterable_index = 0
        self._curr_iterable_iterator = None
