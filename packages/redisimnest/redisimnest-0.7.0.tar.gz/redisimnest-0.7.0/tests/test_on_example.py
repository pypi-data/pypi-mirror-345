from datetime import datetime
from uuid import UUID
import pytest
from asyncio import run
from ..redisimnest.key import Key 
from ..redisimnest.base_cluster import BaseCluster
from ..redisimnest.utils import RedisManager, serialize, deserialize
from ..redisimnest.exceptions import AccessDeniedError, MissingParameterError
from redis.exceptions import DataError



class Message:
    __prefix__ = 'messages'
    __ttl__ = 50

    message = Key('message:{message_id}', "Unknown Message", 50)
    complex_data = Key('complex_data', {})


class Admin:
    __prefix__ = 'admin:{admin_id}'
    messages = Message
    fist_name = Key('fist_name')

class User:
    __prefix__ = 'user:{user_id}'
    __ttl__ = 120

    messages = Message
    fist_name = Key('firt_name')
    age = Key('age', 0)

    password = Key('password', 'simple_pass', is_password=True)
    sensitive_data = Key('sensitive_data', None, is_secret=True)

class App:
    __prefix__ = 'app'
    __ttl__ = 80

    pending_users = Key('pending_users')
    tokens = Key('tokens', [])


class RootCluster(BaseCluster):
    __prefix__ = 'root'
    __ttl__ = None

    app = App
    user = User
    admin = Admin

    project_name = Key('project_name')
    date = Key('the_date', "Unkown date")

redis_client = RedisManager.get_client()
root = RootCluster(redis_client=redis_client)



class TestSmoke:
    def test_child_cluster_access(self):
        user = root.user
        app = root.app
        admin = root.admin


    def test_key_access(self):
        admin_fist_name = root.admin(123).fist_name
        user_fist_name = root.user(123).fist_name


class TestPrefix:
    def test_cluster_prefix(self):
        admin = root.admin(123)
        assert admin.get_full_prefix() == 'root:admin:123'

    
    def test_child_cluster_prefix(self):
        with pytest.raises(MissingParameterError):
            message = root.admin.messages#.get_full_prefix()
        
        messages = root.admin(123).messages

        assert messages.get_full_prefix() == 'root:admin:123:messages'

        with pytest.raises(MissingParameterError):
            message = root.admin(123).messages.message()
        
        message = root.admin(123).messages.message(123)

        assert message.key == 'root:admin:123:messages:message:123'


class TestTTLDrilling:
    def test_key_level_ttl(self):
        key = root.admin(admin_id=1).messages.message(message_id=42)
        assert key.the_ttl == 50, "Key-level TTL should override all others"

    def test_subcluster_level_ttl(self):
        key = root.user(user_id=5).messages.message(message_id=99)
        assert key.the_ttl == 50, "Subcluster-level TTL should override parent clusters if key has no own TTL"

    def test_cluster_level_ttl(self):
        key = root.app.pending_users
        print(key.the_ttl)
        assert key.the_ttl == 80, "Cluster-level TTL should apply when key and subcluster TTL are not defined"

    def test_fallback_to_root_ttl(self):
        key = root.project_name
        assert key.the_ttl is None, "Fallback to root cluster TTL if no other TTL is defined"

    def test_no_ttl_set_defaults_to_none(self):
        key = root.admin(admin_id=1).fist_name
        assert key.the_ttl is None, "Keys without TTL and no inherited TTL should default to None"

    def test_overridden_in_subcluster_vs_parent(self):
        # root.user has TTL 120, but messages (as subcluster) defines TTL = 50
        key = root.user(user_id=42).messages.message(message_id=9)
        assert key.the_ttl == 50, "Subcluster TTL should take precedence over parent"

    def test_distinct_ttl_across_siblings(self):
        admin_key = root.admin(admin_id=1).messages.message(message_id=101)
        user_key = root.user(user_id=1).messages.message(message_id=202)
        assert admin_key.the_ttl == 50
        assert user_key.the_ttl == 50
        # Even though both keys share the same subcluster (`messages`), they resolve from different parents

    def test_root_ttl_does_not_leak(self):
        key = root.admin(admin_id=1).fist_name
        assert key.the_ttl is None, "Root TTL must not leak into fully defined children if TTLs aren't declared there"





async def main_test():
    await root.clear()
    await root.project_name.set("RedisimNest")
    assert await root.project_name.get() == "RedisimNest"

    await root.user(user_id=1).age.set(30)
    assert await root.user(1).age.get() == 30

    print(await root.app.tokens.get())
    # assert await root.app.tokens.get() == []

    key = root.user(123).fist_name
    await key.set("Ali")
    ttl = await key.ttl()
    print(ttl)
    assert 0 < ttl <= 120

    key = root.user(123).fist_name
    await key.set("Ali")
    await key.expire(10)
    ttl = await key.ttl()
    assert ttl <= 10
    await key.persist()
    assert await key.ttl() == -1  # TTL removed

    key = root.app.pending_users
    await key.set(["u1", "u2"])
    await key.unlink()
    assert not await key.exists()

    key = root.user(5).age
    try:
        await key.set("not an int")
    except DataError:
        pass
        
    await root.admin(admin_id="7").fist_name.set("Zahra")
    usage = await root.admin(7).fist_name.memory_usage()
    assert usage > 0

    key = root.app.tokens
    await key.set(["token1"])
    assert await key.exists()
    await key.touch()
    ttl = await key.ttl()
    assert ttl >= 0  # Confirm it's still a valid key

    await root.project_name.set("the project Name")
    app_keys = set(await root.app.subkeys())
    print('clear result: ', await root.app.clear())
    all_keys = set(await root.subkeys())
    assert all_keys is not None
    assert all_keys.intersection(app_keys) == set()

    now = datetime.now()
    await root.date.set(now)
    assert await root.date.get() == now

    
    
    # ==============______the_type method______=========================================================================================== the_type method
    the_type = await root.project_name.the_type
    assert the_type is str

    await root.project_name.delete()
    the_type = await root.project_name.the_type
    assert the_type is None

    await root.date.set(datetime.now())
    dt_type = await root.date.the_type
    assert dt_type is datetime

    
    
    # ==============______(de)serialize usage______=========================================================================================== serialize usage
    value = datetime.now()
    raw = serialize(value)
    value_type, restored_value = deserialize(raw, with_type=True)

    assert value_type is datetime
    assert restored_value == value



    original = UUID("12345678-1234-5678-1234-567812345678")
    original_type_str, raw = serialize(original, with_type=True, with_type_str=True)
    type_str, restored = deserialize(raw, with_type=True, with_type_str=True)

    assert type_str == original_type_str
    assert restored == original



    
    # ==============______CLEAR METHOD TEST______=========================================================================================== CLEAR METHOD TEST
    await root.admin(123).fist_name.set("Ali")
    name = await root.admin(123).fist_name.get()
    assert name == 'Ali'

    await root.admin(123).clear()

    name = await root.admin(123).fist_name.get()
    assert name is None



    await root.user(123).messages.message(123).set("the message")
    the_message = await root.user(123).messages.message(123).get()
    assert the_message == 'the message'

    await root.user(123).clear()

    the_message = await root.user(123).messages.message(123).get()
    assert the_message == "Unknown Message"


async def secret_password_test():
    await root.clear()
    user_key = root.user(user_id=42)

    
    
    # ==============______PASSWORD______=========================================================================================== PASSWORD

    # PASSWORD: Set and verify correct password
    await user_key.password.set("hunter2")
    assert await user_key.password.verify_password("hunter2") is True

    # PASSWORD: Reject wrong password
    assert await user_key.password.verify_password("not-hunter2") is False

    # PASSWORD: Verify without setting (should fail)
    await user_key.password.delete()
    assert await user_key.password.verify_password("anything") is None

    # PASSWORD: Set again and test it hashes (not stored as plain)
    await user_key.password.set("again123")
    hashed = await user_key.password.get(reveal=True)
    assert hashed != "again123"

    # PASSWORD: Should raise if trying to access directly
    try:
        await user_key.password.get()
        assert False, "Should raise TypeError"
    except AccessDeniedError:
        pass

    # PASSWORD: Reject non-string input
    try:
        await user_key.password.set(12345)
    except TypeError:
        pass

    # PASSWORD: Delete and confirm it's gone
    await user_key.password.set("temp_pass")
    await user_key.password.delete()
    assert await user_key.password.verify_password("temp_pass") is None

    # PASSWORD: Double set causes different hash (rehash)
    await user_key.password.set("same-pass")
    hash1 = await user_key.password.get(reveal=True)
    await user_key.password.set("same-pass")
    hash2 = await user_key.password.get(reveal=True)
    assert hash1 != hash2

    
    
    # ==============______SECRET______=========================================================================================== SECRET

    # SECRET: Set and retrieve
    await user_key.sensitive_data.set("some top secret")
    val = await user_key.sensitive_data.get()
    assert val == "some top secret"

    # SECRET: Setting None is allowed
    await user_key.sensitive_data.set(None)
    assert await user_key.sensitive_data.get() is None

    # SECRET: Reject non-string input
    try:
        await user_key.sensitive_data.set(999)
    except TypeError:
        pass

    # SECRET: Set twice, different ciphertext
    await user_key.sensitive_data.set("same secret")
    enc1 = await user_key.sensitive_data.raw()
    await user_key.sensitive_data.set("same secret")
    enc2 = await user_key.sensitive_data.raw()
    assert enc1 != enc2

    # SECRET: Delete removes value
    await user_key.sensitive_data.set("to be deleted")
    await user_key.sensitive_data.delete()
    assert await user_key.sensitive_data.get() is None

    # PASSWORD & SECRET: Confirm `repr()` includes names
    assert "password" in repr(user_key.password)
    assert "sensitive_data" in repr(user_key.sensitive_data)

    # PASSWORD & SECRET: Check `the_type`
    await user_key.sensitive_data.set("test type")
    assert await user_key.sensitive_data.the_type is str

    # PASSWORD & SECRET: Docs mention their roles
    assert "is_password" in user_key.password.__doc__
    assert "is_secret" in user_key.sensitive_data.__doc__


    # ==============______CHECK STALE DATA______=========================================================================================== CHECK STALE DATA  
    await root.user(123).age.set(25)
    data = await root.user(123).age.get()
    assert data == 25

    id_1 = id(data)

    non_existing_data = await root.user(321).age.get()
    assert non_existing_data == 0

    await root.user(321).age.set(52)
    data = await root.user(321).age.get()
    assert data == 52

    id_2 = id(data)

    assert id_1 != id_2




    await root.clear()
    await root.user(123).age.set(123)
    data = await root.user(123).age.get()
    await root.user(123).clear()
    data = await root.user(123).age.get()

    assert data == 0



    await root.clear()
    await root.user(123).age.set(123)
    data = await root.user(123).age.get()
    await root.user(123).age.set(321)
    data = await root.user(123).age.get()

    assert data == 321

    



    await root.clear()
    user = root.user(123)
    age = user.age

    await age.set(123)
    data = await age.get()
    await user.clear()
    data = await age.get()

    assert data == 0

    user = root.user(321)
    age = user.age

    assert await age.get() == 0





class TestHandlers:
    def test_main(self):
        async def run_subtests():
            await main_test()
            await secret_password_test()
        run(run_subtests())
    



