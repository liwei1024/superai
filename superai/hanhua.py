import random


def Getyulu():
    # https://www.zhihu.com/question/50987790
    yulus = [
        "A man can be destroyed but not defeated.",
        "Love means never having to say you're sorry.",
        "Life was like a box of chocolates, you never know what you’re gonna get.",
        "Death is just a part of life, something we're all destined to do.",
        "Anakin, this path has been placed before you. The choice is yours alone.",
        "We become the most familiar strangers.",
        "It takes a strong man to save himself, and a great man to save another.",
        "Everything that has a begin has an end.",
        "The truth is out there.",
        "Stupid is as stupid does.",
        "The things you own, end up owing you.",
        "Get busy living or get busy dying.",
        "Keep your friends close and your enemies closer.",
    ]

    idx = random.randint(0, len(yulus) - 1)

    return yulus[idx]


def main():
    print(Getyulu())


if __name__ == '__main__':
    main()
