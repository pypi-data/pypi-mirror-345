import json
import random
from importlib import import_module

from django.urls import reverse
from sdh.redis import RedisConn

"""
Module for generate one time link with handler in redirects
or direct call djnago views
"""


class OneTimeLink:
    """ One time link implementation.
    Member Vars:
       ALPHABET: source chargs for generate token
    """

    ALPHABET = 'abcdefghjkmnpqrstuvwxyz123456789'
    PREFIX = 'otl_'
    ATTEMPTS = 5
    KEYSIZE = 6

    def __init__(self, key,
                 resolve_name=None, resolve_kwargs=None,
                 url_redirect=None):
        """ Initialization of one time link.

        Args:
           key: link access token
           resolve_name: name of back-resolve view alias (for resolve)
           resolve_kwargs: kwargs for resolve
           url_redirect: ready to use, full formatted function for redirect
           use_redirect: use redirect or processing view in place

        If you'd like to use build in token generator - pls
        use OneTimeLink.create constructor
        """

        self.key = key
        self.resolve_name = resolve_name or ''
        self.resolve_kwargs = resolve_kwargs or dict()
        self.url_redirect = url_redirect or ''
        self.context = {}
        self.counter = None
        self.expire = None
        self.cb_function = None

    def __setitem__(self, key, value):
        self.context[key] = value

    def __getitem__(self, key):
        return self.context[key]

    @classmethod
    def build_key(cls):
        """ Generate random token based on ALPHABET and KEYSIZE
        """
        key = ''
        for i in range(cls.KEYSIZE):
            key += random.choice(cls.ALPHABET)
        return key

    @classmethod
    def create(cls, **kwargs):
        """ Create instance of OneTimeLink with valid token.
        Token validated over storage for unique

        Args:
           resolve_name: name of back-resolve view alias (for resolve)
           resolve_kwargs: kwargs for resolve
           url_redirect: ready to use, full formatted function for redirect
           use_redirect: use redirect or processing view in place

        Returns:
           instance of the OneTimeLink

        Raises:
           KeyError: if no way to generate unique key over storage

        """
        with RedisConn() as redis:
            attempts = cls.ATTEMPTS
            while attempts:
                key = cls.build_key()
                if not redis.hsetnx('%s%s' % (cls.PREFIX, key), 'key', key):
                    attempts -= 1
                    continue
                return cls(key, **kwargs)
        # FixMe: need to add exception
        raise KeyError

    def save(self, callback=None, expire=None, counter=None):
        """ Save state of object to the storage

        Args:
           callback: callback or view function, that should be run before redirect.
               If callback return value - it will be rendered instead of processing redirect.
           expire: link expire time in secunds, default no expire
           counter: number of activation for this link, default no limit
        """
        data = {'resolve_name': self.resolve_name,
                'resolve_kwargs': json.dumps(self.resolve_kwargs),
                'url_redirect': self.url_redirect,
                'context': json.dumps(self.context)}
        if callback:
            data['module'] = callback.__module__
            data['function'] = callback.__name__

        redis_key = self.redis_key(self.key)
        with RedisConn() as redis:
            redis.hmset(redis_key, data)
            if counter:
                redis.hset(redis_key, 'counter', counter)

            if expire:
                redis.expire(redis_key, expire)

    @classmethod
    def redis_key(cls, key):
        return '%s%s' % (cls.PREFIX, key)

    @classmethod
    def get(cls, key):
        """ Lookup key over storage and retrieve information about OneTimeLink

        Args:
            key: requested key

        Returns:
            retrieved instance of the OneTimeLink

        Raises:
            KeyError: if no key founds
        """

        redis_key = cls.redis_key(key)
        with RedisConn() as redis:
            data = redis.hgetall(redis_key)
            if not data:
                raise KeyError

            otl = cls(key,
                      resolve_name=data['resolve_name'],
                      resolve_kwargs=json.loads(data['resolve_kwargs']),
                      url_redirect=data['url_redirect'])
            otl.context = json.loads(data['context'])

            if 'module' in data:
                module = import_module(data['module'])
                otl.cb_function = getattr(module, data['function'])

            if 'counter' in data:
                otl.counter = int(data['counter'])
                if otl.counter <= 0:
                    redis.delete(redis_key)
                    raise KeyError
                redis.hincrby(redis_key, 'counter', -1)
        return otl

    @property
    def url(self):
        return reverse('one-time-link', args=(self.key,))

    @property
    def redirect_url(self):
        if self.url_redirect:
            return self.url_redirect

        return reverse(self.resolve_name,
                       kwargs=self.resolve_kwargs)

    @classmethod
    def delete(cls, key):
        """ Immediately delete the counter data """
        with RedisConn() as redis:
            redis.delete(cls.redis_key(key))
