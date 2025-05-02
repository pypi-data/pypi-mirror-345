from yta_general_utils.file.enums import SubtitleFileExtension
from yta_general_utils.file.filename import get_file_extension
from yta_general_utils.file.reader import FileReader
from yta_general_utils.subtitles.dataclasses import SubtitleLine, Subtitles
from datetime import timedelta

import xml.etree.ElementTree as ET
import re
import json


class SubtitlesParser:
    """
    Class to simplify the way we parse subtitles.
    """

    @staticmethod
    def parse_from_filename(
        filename: str
    ):
        """
        Parse the subtitles file with the provided
        'filename'.
        """
        extension = SubtitleFileExtension.to_enum(get_file_extension(filename))
        content = FileReader.read(filename)

        return SubtitlesParser.parse_from_content(content, extension)

    @staticmethod
    def parse_from_content(
        text: str,
        extension: SubtitleFileExtension
    ):
        """
        Parse the provided 'text' content of a subtitles
        file with the given 'extension' format.
        """
        extension = SubtitleFileExtension.to_enum(extension)

        parse_fn = {
            SubtitleFileExtension.SRV1: lambda text: parse_srv1(text),
            SubtitleFileExtension.SRV2: lambda text: parse_srv2(text),
            SubtitleFileExtension.SRV3: lambda text: parse_srv3(text),
            SubtitleFileExtension.JSON3: lambda text: parse_json3(json.loads(text)),
            SubtitleFileExtension.VTT: lambda text: parse_vtt(text),
            SubtitleFileExtension.TTML: lambda text: parse_ttml(text)
        }.get(extension, None)

        return parse_fn(text) if parse_fn else None
    

def parse_srv1(
    text: str
) -> Subtitles:
    """
    Parse the content of a SRV1 subtitles file.

    A srv1 file looks like this:
    <transcript>
    <text start="2.906" dur="3">TEXT 1</text>
    <text start="7.907" dur="3.914">TEXT 2</text>
    """
    subtitles = [
        SubtitleLine(
            text = text_element.text.strip() if text_element.text else '',
            start_time = round(float(text_element.get('start', 0)), 3),
            duration = round(float(text_element.get('dur', 0)), 3)
        ) for text_element in ET.fromstring(text).findall('.//text')
    ]

    return Subtitles(subtitles)

def parse_srv2(
    text: str
) -> Subtitles:
    """
    Parse the content of a SRV2 subtitles file.

    A srv2 file looks like this:
    <transcript>
    <text t="2.906" d="3">TEXT 1</text>
    <text t="7.907" d="3.914">TEXT 2</text>
    """
    subtitles = [
        SubtitleLine(
            text = text_element.text.strip() if text_element.text else '',
            start_time = int(text_element.get('t', 0)),
            duration = int(text_element.get('d', 0))
        ) for text_element in ET.fromstring(text).findall('.//text')
    ]

    return Subtitles(subtitles)

def parse_srv3(
    text: str
) -> Subtitles:
    """
    Parse the content of a SRV3 subtitles file.

    A srv3 file looks like this:
    TODO: Put example
    """
    subtitles = []
    for paragraph in ET.fromstring(text).findall('.//p'):
        paragraph_start_time = int(paragraph.attrib['t'])
        duration = int(paragraph.attrib['d'])
        
        for word in paragraph.findall('s'):
            # Words with no 't' are the first ones and
            # its start_time is the paragraph start_time
            # and the ones with 't', that 't' is the 
            # 'start_time' relative to the paragraph
            relative_word_start_time = int(word.attrib['t']) if 't' in word.attrib else 0
            text = word.text

            subtitles.append(
                SubtitleLine(
                    text = text,
                    start_time = paragraph_start_time + relative_word_start_time,
                    # This duration will be changed it later in
                    # post-processing based on the next word
                    # 'start_time'
                    duration = duration
                )
            )

    for index, subtitle in enumerate(subtitles[1:], start = 1):
        subtitles[index - 1].duration = subtitle.start_time - subtitles[index - 1].start_time

    return Subtitles(subtitles)

def parse_json3(
    json: dict
) -> Subtitles:
    """
    Parse the content of a JSON3 subtitles file.

    A json3 file looks like this:
    TODO: Put example
    """
    subtitles = []
    for paragraph in json.get('events', []):
        paragraph_start_time = paragraph.get('tStartMs', 0)
        paragraph_duration = paragraph.get('dDurationMs', 0)
        for word in paragraph.get('segs', []):
            relative_word_start_time = int(word['tOffsetMs']) if 'tOffsetMs' in word else 0
            text = word['utf8']
            # We drop any '\n' word as we don't care
            if text == '\n':
                continue

            subtitles.append(
                SubtitleLine(
                    text = text,
                    start_time = paragraph_start_time + relative_word_start_time,
                    # This duration will be changed it later in
                    # post-processing based on the next word
                    # 'start_time'
                    duration = paragraph_duration
                )
            )

    for index, subtitle in enumerate(subtitles[1:], start = 1):
        subtitles[index - 1].duration = subtitle.start_time - subtitles[index - 1].start_time

    return Subtitles(subtitles)

def parse_vtt(
    text: str
) -> Subtitles:
    """
    Parse the content of a VTT subtitles file.

    A vtt file looks like this:
    TODO: Put example
    """
    # TODO: We need to fix an error with the processing
    # that ends generating an empty line followed by a
    # line without blank spaces. Both of them should not
    # be there, but they are (see Notion for more info)
    def clean_text_tags(text: str):
        return re.sub(r'<[^>]+>', '', text).strip()
        #return re.sub(r'<.*?>', '', text).strip()
    
    # We remove the first 3 header lines
    text = '\n'.join(text.splitlines()[3:])
    
    # Remove comments, empty lines or headers and a
    # text we don't want nor need
    text = text.strip()
    text = text.replace(' align:start position:0%', '')

    # Split the content in blocks according to time line
    subtitle_blocks = re.split(r'\n(?=\d{2}:\d{2}:\d{2}\.\d{3})', text)
    
    subtitles = []
    for block in subtitle_blocks:
        lines = block.splitlines()

        # First row is time
        time_range = lines[0].split(' --> ')
        start_time_str = time_range[0].strip()
        end_time_str = time_range[1].strip()

        start_time = _time_to_ms(start_time_str)
        end_time = _time_to_ms(end_time_str)
        duration = end_time - start_time
        
        # Next rows are the text
        text_segments = [
            line.strip()
            for line in lines[1:]
        ]

        # Clean tags and unify
        full_text = ' '.join([clean_text_tags(text) for text in text_segments])

        # The sentences with duration 10 are the ones 
        # that contain the new sentence that is said
        # in the video, so those texts are the ones we
        # must keep for our purpose.
        if duration == 10:
            subtitles[-1] = SubtitleLine(full_text, subtitles[-1].start_time, subtitles[-1].duration + 10)
        else:
            subtitles.append(SubtitleLine(full_text, start_time, duration))
    
    return Subtitles(subtitles)

def parse_ttml(
    text: str
) -> Subtitles:
    # This is the namespace used in this kind of file
    namespace = {'tt': 'http://www.w3.org/ns/ttml'}

    # Look for paragraphs containing it
    subtitles = []
    for p in ET.fromstring(text).findall('.//tt:body//tt:div//tt:p', namespace):
        start_time_str = p.get('begin')
        end_time_str = p.get('end')
        
        if start_time_str and end_time_str:
            start_time = _time_to_ms(start_time_str)
            end_time = _time_to_ms(end_time_str)
            duration = end_time - start_time

            text = ' '.join(p.itertext()).strip()

            # Guardamos el subtítulo como un objeto
            subtitles.append(SubtitleLine(text, start_time, duration))
    
    return Subtitles(subtitles)

# TODO: This should be in a 'date' helper but
# this is very specific so we can't reuse it,
# we need a more general method
def _time_to_ms(
    time_str: str
):
    """
    Transform a HH:MM:SS:ssss date string to a time
    in milliseconds.
    """
    return int(timedelta(
        hours = int(time_str[:2]),
        minutes = int(time_str[3:5]),
        seconds = int(time_str[6:8]),
        milliseconds = int(time_str[9:])
    ).total_seconds() * 1000)