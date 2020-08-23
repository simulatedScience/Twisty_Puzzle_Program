#write to file

class fileWrite():
    def __init__(self):
        self.write()
    def write(self):
        file = open("newFile.txt", "a")
        for i in range(5):
            file.write("\ncontent"+str(i))
        file.close()

if __name__=="__main__":
    F = fileWrite()