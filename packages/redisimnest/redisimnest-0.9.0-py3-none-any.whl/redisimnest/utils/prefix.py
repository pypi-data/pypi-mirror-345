import string

from ..exceptions import InvalidPrefixTemplateError
from ..settings import ENFORCE_PREFIX_START_WITH_PLACEHOLDER



# ==============______VALIDATE PREFIX______=========================================================================================== VALIDATE PREFIX
def validate_prefix(template: str, cluster_name: str):
    formatter = string.Formatter()
    try:
        parsed = list(formatter.parse(template))

        if not parsed:
            return  # Empty prefix is technically allowed

        for i, (literal_text, field_name, _, _) in enumerate(parsed):
            if field_name and not field_name.isidentifier():
                raise InvalidPrefixTemplateError(
                    f"Invalid placeholder '{{{field_name}}}' in prefix '{template}' "
                    f"for cluster '{cluster_name}'"
                )

            if ENFORCE_PREFIX_START_WITH_PLACEHOLDER:
                if i == 0 and not literal_text and field_name:
                    raise InvalidPrefixTemplateError(
                        f"Prefix '{template}' in cluster '{cluster_name}' must not start with a parameter. "
                        f"Start with a literal or use a format like 'type:{{param}}'."
                    )
    except ValueError as e:
        raise InvalidPrefixTemplateError(
            f"Malformed prefix string in cluster '{cluster_name}': {template}"
        ) from e
    return template
