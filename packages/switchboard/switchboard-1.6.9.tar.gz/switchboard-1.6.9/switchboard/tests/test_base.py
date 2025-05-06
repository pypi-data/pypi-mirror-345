"""
switchboard.tests.test_base
~~~~~~~~~~~~~~~

:copyright: (c) 2015 Kyle Adams.
:license: Apache License 2.0, see LICENSE for more details.
"""

import time
import threading

import pytest
import pytest as pytest
from unittest.mock import Mock, patch
from blinker import Signal

from ..base import MongoModelDict, CachedDict
from ..models import VersioningMongoModel
from ..signals import request_finished


class MockModel(VersioningMongoModel):

    def __init__(self, *args, **kwargs):
        self._attrs = []
        for k, v in kwargs.items():
            if not hasattr(self, k):
                self._attrs.append(k)
                setattr(self, k, v)

    def to_bson(self):
        data = {}
        for a in self._attrs:
            data[a] = getattr(self, a)
        return data

    def __eq__(self, other):
        for a in self._attrs:
            # don't really care if IDs match, at least not for the tests
            if a == '_id':
                continue
            if not hasattr(other, a):
                return False
            if getattr(self, a) != getattr(other, a):
                return False
        return True


class TestMongoModelDict:

    def teardown_method(self):
        MockModel.c.drop()

    def test_api(self):
        base_count = MockModel.count()

        mydict = MongoModelDict(MockModel, key='key', value='value')
        mydict['foo'] = MockModel(key='foo', value='bar')
        assert isinstance(mydict['foo'], MockModel)
        assert mydict['foo']._id
        assert mydict['foo'].value == 'bar'
        assert MockModel.get(key='foo').value == 'bar'
        assert MockModel.count() == base_count + 1
        old_id = mydict['foo']._id
        mydict['foo'] = MockModel(key='foo', value='bar2')
        assert isinstance(mydict['foo'], MockModel)
        assert mydict['foo']._id == old_id
        assert mydict['foo'].value == 'bar2'
        assert MockModel.get(key='foo').value == 'bar2'
        assert MockModel.count() == base_count + 1

        # test deletion
        mydict['foo'].delete()
        assert 'foo' not in mydict

    def test_expirey(self):
        base_count = MockModel.count()

        mydict = MongoModelDict(MockModel, key='key', value='value')

        assert mydict._cache is None

        instance = MockModel(key='test_expirey', value='hello')
        mydict['test_expirey'] = instance

        assert len(mydict._cache) == base_count + 1
        assert mydict['test_expirey'] == instance

        request_finished.send(Mock())

        assert mydict._last_updated is None
        assert mydict['test_expirey'] == instance
        assert len(mydict._cache) == base_count + 1

    def test_no_auto_create(self):
        # without auto_create
        mydict = MongoModelDict(MockModel, key='key', value='value')
        with pytest.raises(KeyError):
            mydict['hello']
        assert MockModel.count() == 0

    def test_auto_create_no_value(self):
        # with auto_create and no value
        mydict = MongoModelDict(MockModel, key='key', value='value',
                                auto_create=True)
        repr(mydict['hello'])
        assert MockModel.count() == 1
        assert not hasattr(MockModel.get(key='hello'), 'value'), ''

    def test_auto_create(self):
        # with auto_create and value
        mydict = MongoModelDict(MockModel, key='key', value='value',
                                auto_create=True)
        mydict['hello'] = MockModel(key='hello', value='foo')
        assert MockModel.count() == 1
        assert MockModel.get(key='hello').value == 'foo'

    def test_save_behavior(self):
        mydict = MongoModelDict(MockModel, key='key', value='value',
                                auto_create=True)
        mydict['hello'] = 'foo'
        for n in range(10):
            mydict[str(n)] = 'foo'
        assert len(mydict) == 11
        assert MockModel.count() == 11

        mydict = MongoModelDict(MockModel, key='key', value='value',
                                auto_create=True)
        m = MockModel.get(key='hello')
        m.value = 'bar'
        m.save()

        assert MockModel.count() == 11
        assert len(mydict) == 11
        assert mydict['hello'].value == 'bar'

        mydict = MongoModelDict(MockModel, key='key', value='value',
                                auto_create=True)
        m = MockModel.get(key='hello')
        m.value = 'bar2'
        m.save()

        assert MockModel.count() == 11
        assert len(mydict) == 11
        assert mydict['hello'].value == 'bar2'

    def test_signals_are_connected(self):
        MongoModelDict(MockModel, key='key', value='value',
                       auto_create=True)
        post_save = VersioningMongoModel.post_save
        post_delete = VersioningMongoModel.post_delete
        assert post_save.has_receivers_for(MockModel)
        assert post_delete.has_receivers_for(MockModel)
        assert request_finished.has_receivers_for(Signal.ANY)


class TestCacheIntegration:
    def setup_method(self):
        self.cache = Mock()
        self.cache.get.return_value = {}
        self.mydict = MongoModelDict(MockModel, key='key', value='value',
                                     auto_create=True)
        self.mydict.cache = self.cache

    def teardown_method(self):
        MockModel.c.drop()

    def test_model_creation(self):
        instance = MockModel(key='hello', value='foo')
        self.mydict['hello'] = instance
        assert self.cache.get.call_count == 0
        assert self.cache.set.call_count == 2
        self.cache.set.assert_any_call(self.mydict.cache_key,
                                       dict(hello=instance))
        last_updated_key = self.mydict.last_updated_cache_key
        self.cache.set.assert_any_call(last_updated_key,
                                       self.mydict._last_updated)

    def test_model_change(self):
        self.mydict['hello'] = MockModel(key='hello', value='foo')
        self.cache.reset_mock()
        instance = MockModel(key='hello', value='bar')
        self.mydict['hello'] = instance
        assert self.cache.get.call_count == 0
        assert self.cache.set.call_count == 2
        self.cache.set.assert_any_call(self.mydict.cache_key,
                                       dict(hello=instance))
        last_updated_key = self.mydict.last_updated_cache_key
        self.cache.set.assert_any_call(last_updated_key,
                                       self.mydict._last_updated)

    def test_model_delete(self):
        self.mydict['hello'] = MockModel(key='hello', value='foo')
        self.cache.reset_mock()
        del self.mydict['hello']
        assert self.cache.get.call_count == 0
        assert self.cache.set.call_count == 2
        self.cache.set.assert_any_call(self.mydict.cache_key, {})
        last_updated_key = self.mydict.last_updated_cache_key
        self.cache.set.assert_any_call(last_updated_key,
                                       self.mydict._last_updated)

    def test_model_access(self):
        self.mydict['hello'] = MockModel(key='hello', value='foo')
        self.cache.reset_mock()
        foo = self.mydict['hello']
        foo = self.mydict['hello']
        foo = self.mydict['hello']
        foo = self.mydict['hello']
        assert foo.value == 'foo'
        assert self.cache.get.call_count == 0
        assert self.cache.set.call_count == 0

    def test_model_access_without_cache(self):
        spec = dict(key='hello', value='foo')
        self.mydict['hello'] = MockModel(**spec)
        self.mydict._cache = None
        self.mydict._last_updated = None
        self.cache.reset_mock()
        foo = self.mydict['hello']
        assert foo.value == 'foo'
        assert self.cache.get.call_count == 2
        assert self.cache.set.call_count == 0
        self.cache.get.assert_any_call(self.mydict.cache_key)
        self.cache.reset_mock()
        foo = self.mydict['hello']
        foo = self.mydict['hello']
        foo = self.mydict['hello']
        assert self.cache.get.call_count == 0
        assert self.cache.set.call_count == 0

    def test_model_access_with_expired_local_cache(self):
        spec = dict(key='hello', value='foo')
        self.mydict['hello'] = MockModel(**spec)
        self.mydict._last_updated = None
        self.cache.reset_mock()
        foo = self.mydict['hello']
        assert foo.value == 'foo'
        assert self.cache.get.call_count == 1
        assert self.cache.set.call_count == 0
        self.cache.get.assert_any_call(self.mydict.last_updated_cache_key)
        self.cache.reset_mock()
        foo = self.mydict['hello']
        foo = self.mydict['hello']
        assert self.cache.get.call_count == 0
        assert self.cache.set.call_count == 0


class TestCachedDict:
    def setup_method(self):
        self.cache = Mock()
        self.mydict = CachedDict(timeout=100)
        self.mydict.cache =self.cache

    @patch('switchboard.base.CachedDict._update_cache_data')
    @patch('switchboard.base.CachedDict.is_local_expired',
           Mock(return_value=True))
    @patch('switchboard.base.CachedDict.has_global_changed',
           Mock(return_value=True))
    def test_error_causes_reset(self, _update_cache_data):
        self.cache.get.return_value = 1
        self.mydict._cache = {}
        self.mydict._last_updated = time.time()
        self.mydict._populate()

        assert _update_cache_data.called

    @patch('switchboard.base.CachedDict._update_cache_data')
    @patch('switchboard.base.CachedDict.is_local_expired',
           Mock(return_value=True))
    @patch('switchboard.base.CachedDict.has_global_changed',
           Mock(return_value=False))
    def test_expired_does_update_data(self, _update_cache_data):
        self.mydict._cache = {}
        self.mydict._last_updated = time.time()
        self.mydict._populate()

        assert not _update_cache_data.called

    @patch('switchboard.base.CachedDict._update_cache_data')
    @patch('switchboard.base.CachedDict.is_local_expired',
           Mock(return_value=False))
    @patch('switchboard.base.CachedDict.has_global_changed',
           Mock(return_value=True))
    def test_reset_does_expire(self, _update_cache_data):
        self.mydict._cache = {}
        self.mydict._last_updated = time.time()
        self.mydict._populate(reset=True)

        _update_cache_data.assert_called_once_with()

    @patch('switchboard.base.CachedDict._update_cache_data')
    @patch('switchboard.base.CachedDict.is_local_expired',
           Mock(return_value=False))
    @patch('switchboard.base.CachedDict.has_global_changed',
           Mock(return_value=True))
    def test_does_not_expire_by_default(self, _update_cache_data):
        self.mydict._cache = {}
        self.mydict._last_updated = time.time()
        self.mydict._populate()

        assert not _update_cache_data.called

    def test_is_expired_missing_last_updated(self):
        self.mydict._last_updated = None
        assert self.mydict.is_local_expired()
        assert not self.cache.get.called

    def test_is_expired_last_updated_beyond_timeout(self):
        self.mydict._last_updated = time.time() - 101
        assert self.mydict.is_local_expired()

    def test_is_expired_within_bounds(self):
        self.mydict._last_updated = time.time()

    def test_is_not_expired_if_remote_cache_is_old(self):
        # set it to an expired time
        self.mydict._last_updated = time.time() - 101
        self.cache.get.return_value = self.mydict._last_updated

        result = self.mydict.has_global_changed()

        last_updated = self.mydict.last_updated_cache_key
        self.cache.get.assert_called_once_with(last_updated)
        assert result is False

    def test_is_expired_if_remote_cache_is_new(self):
        # set it to an expired time
        self.mydict._last_updated = time.time() - 101
        self.cache.get.return_value = time.time()

        result = self.mydict.has_global_changed()

        last_updated = self.mydict.last_updated_cache_key
        self.cache.get.assert_called_once_with(last_updated)
        assert result is True

    def test_is_expired_if_never_updated(self):
        # _last_updated None
        self.mydict._last_updated = None
        self.cache.get.return_value = time.time()

        result = self.mydict.has_global_changed()

        assert result is True

    @patch('switchboard.base.CachedDict._populate')
    @patch('switchboard.base.CachedDict.get_default')
    def test_returns_default_if_no_local_cache(self, get_default, populate):
        get_default.return_value = 'bar'
        value = self.mydict['foo']
        assert get_default.called
        assert value == 'bar'


class TestCacheConcurrency:

    def setup_method(self):
        self.mydict = CachedDict()
        self.exc = None

    @patch('switchboard.base.CachedDict.get_cache_data')
    def test_cache_reset_race(self, get_cache_data):
        '''
        Test race conditions when populating a cache.

        Setup a situation where the cache is cleared immediately after being
        populated, to simulate the race condition of one thread resetting it
        just after another has populated it.
        '''
        get_cache_data.return_value = dict(key='test')
        t2 = threading.Thread(target=self.mydict.clear_cache)

        def verify_dict_access():
            self.mydict._populate()
            # Fire up the second thread and wait for it to clear the cache.
            t2.start()
            t2.join()
            # Verify that the first thread's cache is still populated.
            # Note: we don't call self.mydict['key'] because we don't want to
            # re-trigger cache population.
            # Note: Any errors (assertion or otherwise) must be surfaced up to
            # the parent thread in order for nose to see that something went
            # wrong.
            try:
                assert self.mydict._cache, 'The cache was reset between threads'
                assert self.mydict._cache['key'] == 'test'
            except Exception as e:
                self.exc = e

        t1 = threading.Thread(target=verify_dict_access)
        t1.start()
        t1.join()
        if self.exc:
            raise self.exc
