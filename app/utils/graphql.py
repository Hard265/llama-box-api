from dataclasses import fields as dataclass_fields




class FromModelMixin:
    @classmethod
    def from_model(cls, model_obj, exclude: set[str] = None, include: dict[str, type] = None):
        """
        Convert model to GraphQL type, safely avoiding unloaded fields.
        :param exclude: fields to exclude
        :param include: manually specified fields to force (e.g. computed properties)
        """
        exclude = exclude or set()
        include = include or {}

        
        constructor_fields = {f.name for f in dataclass_fields(cls) if f.init}
        constructor_fields |= set(include.keys())

        kwargs = {}
        for field in constructor_fields:
            if field in exclude:
                continue

            try:
                value = getattr(model_obj, field)

                # Recursively call from_model if type is provided
                expected_type = include.get(field) or cls.__annotations__.get(field)
                if hasattr(expected_type, "from_model") and value is not None:
                    value = expected_type.from_model(value)

                kwargs[field] = value

            except Exception:
                kwargs[field] = None

        return cls(**kwargs)
