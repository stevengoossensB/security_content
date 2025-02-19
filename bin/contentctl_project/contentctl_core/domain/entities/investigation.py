import enum
import uuid
import string
import re
import requests

from pydantic import BaseModel, validator, ValidationError
from dataclasses import dataclass
from datetime import datetime

from bin.contentctl_project.contentctl_core.domain.entities.security_content_object import SecurityContentObject
from bin.contentctl_project.contentctl_core.domain.entities.enums.enums import AnalyticsType
from bin.contentctl_project.contentctl_core.domain.entities.enums.enums import DataModel
from bin.contentctl_project.contentctl_core.domain.entities.investigation_tags import InvestigationTags


class Investigation(BaseModel, SecurityContentObject):
    # investigation spec
    name: str
    id: str
    version: int
    date: str
    author: str
    type: str
    datamodel: list
    description: str
    search: str
    how_to_implement: str
    known_false_positives: str
    references: list
    inputs: list = None
    tags: InvestigationTags

    # enrichment
    lowercase_name: str = None


    @validator('name')
    def name_max_length(cls, v):
        if len(v) > 75:
            raise ValueError('name is longer then 75 chars: ' + v)
        return v

    @validator('name')
    def name_invalid_chars(cls, v):
        invalidChars = set(string.punctuation.replace("-", ""))
        if any(char in invalidChars for char in v):
            raise ValueError('invalid chars used in name: ' + v)
        return v

    @validator('id')
    def id_check(cls, v, values):
        try:
            uuid.UUID(str(v))
        except:
            raise ValueError('uuid is not valid: ' + values["name"])
        return v

    @validator('date')
    def date_valid(cls, v, values):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except:
            raise ValueError('date is not in format YYYY-MM-DD: ' + values["name"])
        return v

    @validator('datamodel')
    def datamodel_valid(cls, v, values):
        for datamodel in v:
            if datamodel not in [el.name for el in DataModel]:
                raise ValueError('not valid data model: ' + values["name"])
        return v

    @validator('description', 'how_to_implement')
    def encode_error(cls, v, values, field):
        try:
            v.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError('encoding error in ' + field.name + ': ' + values["name"])
        return v

    @validator('references')
    def references_check(cls, v, values):
        for reference in v:
            try:
                get = requests.get(reference)
                if not get.status_code == 200:
                    raise ValueError('Reference ' + reference + ' is not reachable: ' + values["name"])
            except requests.exceptions.RequestException as e:
                raise ValueError('Reference ' + reference + ' is not reachable: ' + values["name"])

        return v

    @validator('search')
    def search_validate(cls, v, values):
        # write search validator
        return v