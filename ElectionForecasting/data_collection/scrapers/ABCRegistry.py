from abc import ABCMeta


class ABCRegistry(ABCMeta):
    """
    Extends the ABCMeta class to include a registry. Registering all subclasses allow us to run the same template
    tests on all scrapers to make sure they give properly formatted outputs.

    Adapted from this gist: https://gist.github.com/semodi/2a5248f2ff7a55900722545403c25a02#file-abcregistry-py
    """
    REGISTRY = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if not hasattr(new_cls, '_registry_name'):
            raise TypeError('Any class with ABCRegistry as metaclass has to define the class attribute _registry_name')
        cls.REGISTRY[new_cls._registry_name] = new_cls
        return ABCMeta.__new__(cls, name, bases, attrs)

    @classmethod
    def get_registry(cls):
        return dict(cls.REGISTRY)