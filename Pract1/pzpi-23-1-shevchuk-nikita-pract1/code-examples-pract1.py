from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class Document:
    def __init__(self) -> None:
        self.text: str = ""

    def write(self, words: str) -> None:
        self.text += words

    def erase_last(self, length: int) -> None:
        if len(self.text) >= length:
            self.text = self.text[:-length]

    def get_text(self) -> str:
        return self.text

class WriteCommand(Command):
    def __init__(self, document: Document, text_to_write: str) -> None:
        self._document = document
        self._text_to_write = text_to_write

    def execute(self) -> None:
        self._document.write(self._text_to_write)

    def undo(self) -> None:
        self._document.erase_last(len(self._text_to_write))

class EditorInvoker:
    def __init__(self) -> None:
        self._history: list[Command] = []

    def execute_command(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo_last_command(self) -> None:
        if self._history:
            command = self._history.pop()
            command.undo()

if __name__ == "__main__":
    doc = Document()
    invoker = EditorInvoker()

    write_hello = WriteCommand(doc, "Hello ")
    write_world = WriteCommand(doc, "World!")

    invoker.execute_command(write_hello)
    invoker.execute_command(write_world)
    print(doc.get_text())  # Виведе: Hello World!

    invoker.undo_last_command()
    print(doc.get_text())  # Виведе: Hello
