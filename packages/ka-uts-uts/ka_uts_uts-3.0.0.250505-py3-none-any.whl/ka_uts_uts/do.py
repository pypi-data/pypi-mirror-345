import sys
from ka_uts_com.com import Com
from ka_uts_uts.parms import Parms
from ka_uts_uts.task import Task


class Do:

    @classmethod
    def do(cls) -> None:
        Task.do(Com.sh_kwargs(cls, Parms.d_eq, sys.argv))


if __name__ == "__main__":
    Do.do()
