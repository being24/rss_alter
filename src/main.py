from most_recently_created import MostRecentlyCreated
from criticism_in import CriticismIn
from new_threads import NewThreads

if __name__ == "__main__":
    mrc = MostRecentlyCreated()
    ci = CriticismIn()
    nt = NewThreads()

    mrc.main()
    ci.main()
    nt.main()
