import enum
from django.utils.functional import Promise


class EnumChoicesMixin:
    @classmethod
    def get_choices_for_forms(cls):
        return [(value, label) for value, label in cls.choices]


class AdditionalDataChoicesMeta(enum.EnumMeta):
    """Additional data field to django enum choices metaclass
    Added new field `data`, this field may keep any data.
    """

    def __new__(metacls, classname, bases, classdict, **kwds):
        labels = []
        datas = []
        for key in classdict._member_names:
            value = classdict[key]
            if (
                isinstance(value, (list, tuple)) and
                len(value) > 1 and
                isinstance(value[-1], (Promise, str))
            ):
                *value, label, data = value
                value = tuple(value)
            else:
                label = key.replace('_', ' ').title()
                data = key.replace('_', ' ').title()
            labels.append(label)
            datas.append(data)
            dict.__setitem__(classdict, key, value)
        cls = super().__new__(metacls, classname, bases, classdict, **kwds)
        cls._value2label_map_ = dict(zip(cls._value2member_map_, labels))
        cls._value2data_map_ = dict(zip(cls._value2member_map_, datas))
        cls.label = property(lambda self: cls._value2label_map_.get(self.value))
        cls.data = property(lambda self: cls._value2data_map_.get(self.value))
        cls.do_not_call_in_templates = True
        return enum.unique(cls)

    def __contains__(cls, member):
        if not isinstance(member, enum.Enum):
            # Allow non-enums to match against member values.
            return any(x.value == member for x in cls)
        return super().__contains__(member)

    @property
    def names(cls):
        empty = ['__empty__'] if hasattr(cls, '__empty__') else []
        return empty + [member.name for member in cls]

    @property
    def choices(cls):
        empty = [(None, cls.__empty__)] if hasattr(cls, '__empty__') else []
        return empty + [(member.value, member.label) for member in cls]

    @property
    def labels(cls):
        return [label for _, label, _ in cls.choices]

    @property
    def values(cls):
        return [value for value, _, _ in cls.choices]

    @property
    def datas(cls):
        return [data for _, _, data in cls.choices]


class AdditionalDataChoices(enum.Enum, metaclass=AdditionalDataChoicesMeta):
    """Additional data django choices base class."""

    def __str__(self):
        return str(self.value)


class AdditionalDataTextChoices(str, AdditionalDataChoices):
    """Additional data django text choices."""

    def _generate_next_value_(name, start, count, last_values):
        return name
