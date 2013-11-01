def underscore_to_mixedcase(value):
    def mixedcase():
        while True:
            yield str.capitalize
    c = mixedcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))
