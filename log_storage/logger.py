import os
import shutil
from datetime import datetime


class Logger:
    storage_path = "./log_storage"

    def __init__(self, parameters):
        self.algorithm = parameters["algorithm"]
        self.log_name = parameters["log_name"]
        self.debug_name = parameters["debug_name"]
        self.conf_path = parameters["configuration"]
        self.src_dump = parameters["src_dump"]
        self.description = parameters["description"]
        self.name = "%s-?" % self.__now()

        self.paths = self.__start()
        self.__copy()

    def __start(self):
        paths = {"alg": "%s/%s" % (self.storage_path, self.algorithm)}
        paths["main"] = "%s/%s" % (paths["alg"], self.name)
        paths["src"] = "%s/src" % paths["main"]

        if not os.path.isdir(paths["alg"]):
            os.mkdir(paths["alg"])

        os.mkdir(paths["main"])
        if len(self.description) > 0:
            open("%s/DESCRIPTION" % paths["main"], 'w+').write(self.description)

        if len(self.src_dump) > 0:
            os.mkdir(paths["src"])

        return paths

    def __copy(self):
        shutil.copy(self.conf_path, self.paths["main"])

        for src_path in self.src_dump:
            shutil.copy(src_path, self.paths["src"])

    def get_log_path(self):
        return "%s/%s" % (self.paths["main"], self.log_name)

    def get_debug_path(self):
        return "%s/%s" % (self.paths["main"], self.debug_name)

    def end(self):
        if self.name.find("?") < 0:
            raise Exception("Logger already ended")

        new_name = self.name.replace("?", self.__now())
        new_path = "%s/%s" % (self.paths["alg"], new_name)
        os.rename(self.paths["main"], new_path)

        self.name = new_name
        self.paths["main"] = new_path
        self.paths["src"] = "%s/src" % new_path

    def __now(self):
        now = datetime.today()
        z = lambda n: ("0%s" if n <= 9 else "%s") % n

        date = "%s.%s.%s" % (now.year, z(now.month), z(now.day))
        time = "%s:%s:%s" % (z(now.hour), z(now.minute), z(now.second))
        return "%s_%s" % (date, time)
