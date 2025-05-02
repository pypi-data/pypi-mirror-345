from dataclasses import dataclass


@dataclass
class SubtitleLine:
    """
    Class to represent a line of a subtitles file.
    """
    
    text: str
    """
    The text that is displayed in the subtitle line.
    """
    start_time: int
    """
    The time moment (in ms) in which the subtitle 
    line starts being displayed.
    """
    duration: int
    """
    The time (in ms) that the subtitle line last
    being displayed.
    """

    @property
    def end_time(self) -> int:
        """
        The time moment (in ms) in which the subtitle
        line ends being displayed.
        """
        return self.start_time + self.duration

    def __init__(
        self,
        text: str,
        start_time: int,
        duration: int
    ):
        self.text = text
        self.start_time = start_time
        self.duration = duration

@dataclass
class Subtitles:
    """
    Class to represent the subtitles of a file.
    """

    subtitles: list[SubtitleLine]
    """
    The list of subtitles line.
    """

    @property
    def text(
        self
    ) -> str:
        """
        Get the whole subtitles text by concatenating
        all the subtitle lines.
        """
        return '\n'.join([
            subtitle.text.strip()
            for subtitle in self.subtitles
        ])

    def __init__(
        self,
        subtitles: list[SubtitleLine] = []
    ):
        self.subtitles = subtitles

    def add_subtitle(
        self,
        subtitle: SubtitleLine
    ):
        self.subtitles.append(subtitle)