class cout:
    def __lshift__(self, value):
        print(value, end="")
        return self


class cin:
    def __rshift__(self, value):
        input()
        return self


endl = "\n"
