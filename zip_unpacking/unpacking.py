import zipfile

class Unpaking:
    def __init__(self, zippath:str) -> None:
        self.zippath = zippath
        self.file_zip = zipfile.ZipFile(f'{self.zippath}', 'r')

    def unpaking_zip(self, file_name, *, file_path:str = 'user_zip_data/'):
        try:
            self.file_zip.extractall(f'{file_path}/{file_name}')
            print('[UNPAKING] IS SUCCESSFULLY!!')
        except Exception as ex:
            return ex
        self.file_zip.close()

    def get_info(self) -> list:
        return [[i.filename, i.compress_size, i.date_time] for i in self.file_zip.infolist()]
        self.file_zip.close()

    def get_content_file(self, files_path:str, files:list) -> dict:
        data = {}
        try:
            for i in files:
                file_name = i[0]
                with open(f'{files_path}/{file_name}', 'r') as f:
                    file_content = f.read()
                data[file_name] = {'content':file_content if file_content else None}
        except Exception as ex:
            print(ex)
        self.file_zip.close()
        return data

    def get_file_name(self):
        return [i.filename for i in self.file_zip.infolist()]
        self.file_zip.close()

# if __name__=='__main__':
#     unp = Unpaking('pythonProject_Video_to_youtube_api.zip')
#     unp.unpaking_zip(file_path='file_data')
#     unp.get_content_file('file_data/', unp.get_info())