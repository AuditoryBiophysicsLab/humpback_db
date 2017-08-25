import bs4
from bs4 import BeautifulSoup as bs
import attr
from attr.validators import instance_of
from typing import Tuple, Optional
import inspect
from enum import Enum
from datetime import datetime
from dateutil import parser

class SideOfHead(Enum):
    RIGHT = 0
    LEFT = 1


@attr.s
class Metadata:
    """POPO to hold information about the image in question"""
    id = attr.ib()
    notes = attr.ib()
    side_of_head = attr.ib()
    depth = attr.ib(validator=instance_of(int))
    digitization_date = attr.ib(validator=instance_of(datetime))

def get_id(s:bs4.element.Tag) -> str:
    """Get the animal ID string"""
    return s.title.contents[0].split('_')[0].upper()

def get_notes(s:bs4.element.Tag) -> str:
    """Get any notes entered during scanning"""
    try:
        return s.comment.contents[0]
    except AttributeError as a:
        return None

def get_side_of_head(s:bs4.element.Tag) -> SideOfHead:
    """Get which side of the head this image is from"""
    title = s.title.contents[0].lower()
    description = s.description.contents[0].lower()
    if 'rt' in title or 'right' in description:
        return SideOfHead.RIGHT
    elif 'lt' in title or 'left' in description:
        return SideOfHead.LEFT
    else:
        return None

def get_depth(s:bs4.element.Tag) -> int :
    """Get the slide number, which is also the depth in um"""
    title = s.title.contents[0].lower()
    try:
        return int(title.split('_')[1])
    except ValueError:
        return None

def get_digitization_date(s:bs4.element.Tag) -> datetime:
    """Get the date the slide was digitized"""
    return parser.parse(s.acquisitiondateandtime.contents[0])



def tryparse(metadata_file:str) -> Tuple[Optional[Metadata],bool, str]:
    s = bs(open(metadata_file, 'r').read(), 'lxml')
    document = s.information.document
    image = s.information.image
    del s
    message = ''
    contents = {'id' : get_id(document)
                , 'notes' : get_notes(document)
                , 'side_of_head': get_side_of_head(document)
                , 'depth' : get_depth(document)
                , 'digitization_date' : get_digitization_date(image)
                }
    try:
        retval = Metadata(**contents)
    except TypeError as e:
        retval = None
        message += f"could not extract metadata from {metadata_file}: {str(e)}"
    return retval, message == '', message




if __name__ == "__main__":
    meta, success, msg = tryparse('C:/Users/Graham Voysey/Downloads/PP21_321_Rt.tiff_metadata.xml')
    print(meta)