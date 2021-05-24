def get_generator(iterable):

    def generator():
        for item in iterable:
            yield item

    return generator
