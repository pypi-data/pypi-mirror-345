from random import choice


def rand_missing_seq(n=10):
    assert type(n) is int, "n must be integer"
    if n <= 1:
        my_list = [1]
    else:
        from random import randint, shuffle
        my_list = [i for i in range(1, n+1)]
        missing = randint(0, n-1)
        del my_list[missing]
        shuffle(my_list)
    return my_list


def rand_bitstring(n=20):
    assert type(n) is int, "n must be integer"
    return "".join([choice("01") for _ in range(n)])


def rand_word():
    return choice(["racecar", "level", "radar", "deified", "civic", "refer", "rotor", "wow", "otto",
                   "madam", "noon", "kayak", "reviver", "tenet", "stats", "pop", "eve", "eye", "mom", "dad"
                   "physics", "science", "apple", "banana", "cherry", "dog", "elephant", "flower", "guitar",
                   "house", "island", "jungle", "kite", "lemon", "mountain", "notebook", "ocean", "pencil",
                   "quartz", "rainbow", "sunshine", "tiger"])


def rand_word_pair():
    return choice([("listen", "silent"), ("earth", "heart"),  ("angel", "glean"), ("stressed", "desserts"),
                   ("rat", "tar"), ("dusty", "study"), ("evil", "vile"), ("night", "thing"), ("save", "vase"),
                   ("brag", "grab"), ("spot", "stop"), ("arc", "car"), ("flow", "wolf"), ("elbow", "below"),
                   ("cinema", "iceman"), ("race", "care"), ("fate", "feat"), ("pale", "leap"), ("meat", "team"),
                   ("shore", "horse"), ("stone", "tones"), ("spare", "pears"), ("alert", "alter"), ("dear", "read"),
                   ("fried", "fired"), ("inlets", "listen"), ("pat", "tap"), ("god", "dog"), ("rescue", "secure"),
                   ("bored", "robed"), ("opt", "top"), ("slope", "poles"), ("mode", "dome"), ("tired", "tried"),
                   ("stain", "saint"), ("lapse", "pales"), ("files", "flies"), ("cider", "cried"), ("spear", "parse"),
                   ("rental", "learnt"), ("cider", "cedar"), ("cat", "bat"), ("moon", "mood"), ("train", "trait"),
                   ("house", "horse"), ("table", "cable"), ("flame", "frame"), ("stone", "stove"), ("plant", "plane"),
                   ("chair", "chain"), ("grape", "graph"), ("smile", "spike"), ("brave", "grave"), ("cloud", "clout"),
                   ("miles", "tiles"), ("drive", "drift"), ("brush", "brash"), ("spare", "spire"), ("crane", "crave"),
                   ("flash", "flesh"), ("sword", "sworn")])


def rand_statuses(n=50):
    assert type(n) is int, "n must be integer"
    from faker import Faker
    return {Faker().name(): choice(["online", "offline"]) for _ in range(n)}
