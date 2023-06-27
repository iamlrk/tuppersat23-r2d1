class MultiFileWriter:
    def __init__(self, filenames, write_type='a'):
        """
        Initializes a MultiFileWriter object.

        Args:
            filenames (list): A list of filenames to open for writing.
            write_type (str): The write mode to use. Default is 'a' for appending to the files.

        Attributes:
            filenames (list): A list of filenames to open for writing.
            write_type (str): The write mode to use. Default is 'a' for appending to the files.
            files (dict): A dictionary to store the opened file objects.

        Returns:
            None.
        """
        self.filenames = filenames
        self.write_type = write_type
        self.files = {}

    def __enter__(self):
        """
        Enters a with statement block and opens the files for writing.

        Args:
            None.

        Returns:
            files (dict): A dictionary of the opened file objects.

        Raises:
            None.
        """
        for filename in self.filenames:
            self.files[filename.split('.')[0].split('/')[-1]] = open(filename, self.write_type)
        return self.files

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits a with statement block and closes the files.

        Args:
            exc_type (type): The exception type, if any, that was raised.
            exc_val (exception): The exception object, if any, that was raised.
            exc_tb (traceback): The traceback object, if any, that was raised.

        Returns:
            None.

        Raises:
            None.
        """
        for file in self.files.values():
            file.close()


def main():
    filenames = ['/data/data.txt', '/data/telemetry.txt']
    writing_data = {
        'data': 'datapacket',
        'telemetry': 'telemetrypacket',
    }
    with MultiFileWriter(filenames) as files:
        print(files)
        for key, file in files.items():
            print(key)
            # writing_string = writing_data.get(key)
            # file.write(f'{writing_string}\n')
            pass


if __name__ == '__main__':
    main()
    # print(MultiFileWriter().__name__))

