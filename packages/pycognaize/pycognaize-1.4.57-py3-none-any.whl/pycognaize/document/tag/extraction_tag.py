import math

import bson
from datetime import datetime
from typing import Union

from pycognaize.common.confidence import Confidence
from pycognaize.common.enums import IqTagKeyEnum, ID
from pycognaize.document.tag.tag import BoxTag

from pycognaize.common.utils import convert_coord_to_num
from pycognaize.document.tag.cell import Cell
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pycognaize.document.page import Page


class ExtractionTag(BoxTag):
    """Represents field's coordinate data on document"""

    def __init__(self, left, right, top, bottom, page, raw_value,
                 raw_ocr_value, confidence: Confidence = None):
        super().__init__(left=left, right=right, top=top, bottom=bottom,
                         page=page, confidence=confidence)
        self._raw_value = raw_value
        self._raw_ocr_value = raw_ocr_value

    @classmethod
    def construct_from_raw(cls, raw: dict, page: 'Page') -> 'ExtractionTag':
        """Builds Tag object from pycognaize raw data
        :param raw: pycognaize field's tag info
        :param page: `Page` to which the tag belongs
        :return:
        """
        confidence = Confidence(raw.get(IqTagKeyEnum.
                                confidence.value, {}))
        left = convert_coord_to_num(raw['left'])
        top = convert_coord_to_num(raw['top'])
        height = convert_coord_to_num(raw['height'])
        width = convert_coord_to_num(raw['width'])
        right = left + width
        bottom = top + height
        raw_value = raw['value']
        raw_ocr_value = raw['ocrValue']
        tag = cls(left=left, right=right, top=top, bottom=bottom,
                  page=page, raw_value=raw_value, raw_ocr_value=raw_ocr_value,
                  confidence=confidence)
        return tag

    def hshift(self, by) -> 'ExtractionTag':
        """Shifts rectangle horizontally

        :param by: the amount by which the tag should be horizontally shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left + by, right=self.right + by,
                              top=self.top, bottom=self.bottom,
                              page=self.page, raw_value=self.raw_value,
                              raw_ocr_value=self.raw_ocr_value,
                              confidence=self.confidence)

    def horizontal_shift(self, by):
        return self.hshift(by)

    def vshift(self, by) -> 'ExtractionTag':
        """Shifts rectangle vertically
        :param by: the amount by which the tag should be vertically shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left, right=self.right,
                              top=self.top + by, bottom=self.bottom + by,
                              page=self.page, raw_value=self.raw_value,
                              raw_ocr_value=self.raw_ocr_value,
                              confidence=self.confidence)

    def vertical_shift(self, by):
        return self.vshift(by)

    def __add__(self, other: Union['BoxTag', Cell]) -> 'ExtractionTag':
        """Merge two rectangles into one"""
        if self.page.page_number == other.page.page_number:
            left = min(self.left, other.left)
            right = max(self.right, other.right)
            top = min(self.top, other.top)
            bottom = max(self.bottom, other.bottom)
            raw_value_joined = " ".join(
                [i.raw_value for i in sorted(
                    [self, other], key=lambda x: (x.left, x.top))])
            left_actual = left * self.page.image_width / 100
            right_actual = right * self.page.image_width / 100
            top_actual = top * self.page.image_height / 100
            bottom_actual = bottom * self.page.image_height / 100
            words_list = self.page.extract_area_words(left=left_actual,
                                                      right=right_actual,
                                                      top=top_actual,
                                                      bottom=bottom_actual)
            words = [text['ocr_text'] for text in words_list]
            raw_ocr_value_joined = " ".join(words)
            return ExtractionTag(
                left=left, right=right, top=top, bottom=bottom,
                page=self.page, raw_value=raw_value_joined,
                raw_ocr_value=raw_ocr_value_joined,
                confidence=self.confidence)
        else:
            raise ValueError("Tags are not on the same page.")

    @property
    def raw_value(self):
        return self._raw_value

    @property
    def raw_ocr_value(self):
        return self._raw_ocr_value

    def _validate_numeric(self):
        """Validate numerica data"""
        try:
            self.value = (float(self.raw_value) if self.raw_value is not None
                          else math.nan)
            self.has_value_exception = False
        except Exception as ValueException:
            self.has_value_exception = True
            self.value_exception_message = str(ValueException)

        try:
            self.ocr_value = (float(self.raw_ocr_value)
                              if self.raw_ocr_value is not None else math.nan)
            self.has_raw_value_exception = False
        except Exception as RawValueException:
            self.has_raw_value_exception = True
            self.raw_value_exception_message = str(RawValueException)

    def _validate_date(self, date_format):
        """Validate date data"""
        try:
            self.value = datetime.strptime(self.raw_value, date_format)
            self.has_value_exception = False
        except Exception as ValueException:
            self.has_value_exception = True
            self.value_exception_message = str(ValueException)

        try:
            self.ocr_value = datetime.strptime(self.raw_ocr_value, date_format)
            self.has_raw_value_exception = False
        except Exception as RawValueException:
            self.has_raw_value_exception = True
            self.raw_value_exception_message = str(RawValueException)

    def to_dict(self) -> dict:
        """Converts extraction tag to dict"""
        return {
            ID: str(bson.ObjectId()),
            IqTagKeyEnum.ocr_value.value: self.raw_ocr_value,
            IqTagKeyEnum.value.value: str(self.raw_value),
            IqTagKeyEnum.left.value: f"{self.left}%",
            IqTagKeyEnum.top.value: f"{self.top}%",
            IqTagKeyEnum.height.value: f"{self.bottom - self.top}%",
            IqTagKeyEnum.width.value: f"{self.right - self.left}%",
            IqTagKeyEnum.page.value: self.page.page_number,
            IqTagKeyEnum.confidence.value: self.confidence.get_confidence(),
        }
