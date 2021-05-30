from thenewboston_node.core.utils.misc import humanize_camel_case


class HumanizedClassNameMixin:

    def get_humanized_class_name(self, apply_upper_first=True):
        return humanize_camel_case(self.__class__.__name__, apply_upper_first=apply_upper_first)

    @property
    def humanized_class_name(self):
        return self.get_humanized_class_name()

    @property
    def humanized_class_name_lowered(self):
        return self.get_humanized_class_name(apply_upper_first=False)
