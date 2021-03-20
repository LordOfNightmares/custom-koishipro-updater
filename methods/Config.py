import yaml


class Config:
    ignore = None
    url = None
    path = "."

    @classmethod
    def __attrs__(cls):
        return {k: v for k, v in vars(cls).items() if not k.startswith("__")}


class Temp:

    progress = None

    @classmethod
    def __attrs__(cls):
        return {k: v for k, v in vars(cls).items() if not k.startswith("__")}



class YamlManager:
    def __init__(self, path_to_file):
        self.file = path_to_file
        self.data = None

    def write(self, data=None, append=False):
        if data:
            if type(data) == str:
                with open(self.file, 'w') as file_object:
                    file_object.write(data)
                return
            else:
                self.data = data
        if append:
            yaml.dump(self.data, open(self.file, 'a'))
        else:
            yaml.dump(self.data, open(self.file, 'w'))

    def load(self):
        try:
            self.data = yaml.load(open(self.file), Loader=yaml.FullLoader)
            if self.data is None:
                self.data = {}
            return self.data
        except FileNotFoundError:
            with open(self.file, 'w') as fp:
                pass
            return self.load()
        except:
            raise


class FileConfig(YamlManager):
    def __init__(self, path_to_file):
        super().__init__(path_to_file)
        self.load()
        if self.data == {}:
            self.write(data=Config.__attrs__())
            self.load()
        # self.store_temp_cbs = create_folder('ygocdbs')
