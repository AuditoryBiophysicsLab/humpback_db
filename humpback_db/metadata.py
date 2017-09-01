import bs4
from bs4 import BeautifulSoup as bs
import attr
from attr.validators import instance_of
from typing import Tuple, Optional
import inspect
from logging import info, error
from enum import Enum
from datetime import datetime
from dateutil import parser


def ensure_cls(cl):
    """If the attribute is an instance of cls, pass, else try constructing."""

    def converter(val):
        if isinstance(val, cl):
            return val
        else:
            return cl(**val)

    return converter


def ensure_enum(cl):
    """If the attribute is an instance of cls, pass, else try constructing."""

    def converter(val):
        if isinstance(val, cl):
            return val
        else:
            return cl[val]

    return converter

class SideOfHead(Enum):
    RIGHT = 0
    LEFT = 1

@attr.s
class Point:
    x = attr.ib()
    y = attr.ib()

@attr.s
class ROI:
    top_left = attr.ib(validator=ensure_cls(Point))
    bottom_right =attr.ib(validator=ensure_cls(Point))

    @property
    def area(self):
        height = self.top_left.y - self.bottom_right.y
        width = self.top_left.x - self.bottom_right.x
        return height*width

@attr.s
class Metadata:
    """POPO to hold information about the image in question"""
    id = attr.ib()
    notes = attr.ib()
    side_of_head = attr.ib()
    depth = attr.ib(validator=instance_of(int))
    digitization_date = attr.ib(validator=instance_of(datetime))

    def __attrs_post_init__(self):
        self.roi = None
        self.last_modified = None


def get_id(s:bs4.element.Tag) -> str:
    """Get the animal ID string"""
    try:
        return s.title.contents[0].split('_')[0].upper()
    except AttributeError as a:
        error(f'animal ID not found: \n\t{a}')
        return None

def get_notes(s:bs4.element.Tag) -> str:
    """Get any notes entered during scanning"""
    try:
        return s.comment.contents[0]
    except AttributeError as a:
        error(f'notes not found: \n\t{a}')
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
        error(f'side of head cannot be determined from:\n\ttitle:{title}\n\t description:{description}')
        return None

def get_depth(s:bs4.element.Tag) -> int :
    """Get the slide number, which is also the depth in um"""
    title = s.title.contents[0].lower()
    try:
        return int(title.split('_')[1])
    except ValueError as v:
        error(f'could not determine depth from title:{title}: \n\t{v}')
        return None

def get_digitization_date(s:bs4.element.Tag) -> datetime:
    """Get the date the slide was digitized"""
    try:
        datestr = s.acquisitiondateandtime.contents[0]
        return parser.parse(datestr)
    except:
        error(f'could not determine datetime from str:{datestr}')



def tryparse(metadata_file:str) -> Tuple[Optional[Metadata],bool]:
    s = bs(open(metadata_file, 'r').read(), 'lxml')
    document = s.information.document
    image = s.information.image
    del s

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
        error(f"could not extract metadata from {metadata_file}: {str(e)}")
    return retval, retval == None




if __name__ == "__main__":
    meta, success = tryparse('C:/Users/Graham Voysey/Downloads/PP21_321_Rt.tiff_metadata.xml')
    print(meta)