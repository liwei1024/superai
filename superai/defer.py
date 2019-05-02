from functools import wraps


def defer(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        deferred = []
        defer = lambda f: deferred.append(f)
        try:
            return func(*args, defer=defer, **kwargs)
        finally:
            deferred.reverse()
            for f in deferred:
                f()

    return func_wrapper


# @defer
# def main(defer):
#     file = open('test.txt', 'w+')
#     defer(lambda: (file.close(),
#                    print(123)))
#
#     defer(lambda: print(456))
#
#
# if __name__ == "__main__":
#     main()
