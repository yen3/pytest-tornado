import pytest
from tornado import gen
from tornado.process import Subprocess

_used_fixture = False


@gen.coroutine
def dummy(io_loop):
    yield gen.Task(io_loop.add_callback)
    raise gen.Return(True)


@gen.coroutine
def echo_hello_world():
    subproc = Subprocess(args=["echo", "hello", "world"])

    if hasattr(subproc, 'wait_for_exit'):
        yield subproc.wait_for_exit()
    else:
        from tornado.concurrent import Future
        future = Future()

        def callback(ret):
            future.set_result(ret)

        subproc.set_exit_callback(callback)
        yield future


@pytest.fixture(scope='module')
def preparations():
    global _used_fixture
    _used_fixture = True


pytestmark = pytest.mark.usefixtures('preparations')


@pytest.mark.xfail(pytest.__version__ < '2.7.0',
                   reason='py.test 2.7 adds hookwrapper, fixes collection')
@pytest.mark.gen_test
def test_uses_pytestmark_fixtures(io_loop):
    assert (yield dummy(io_loop))
    assert _used_fixture


@pytest.mark.gen_test
def test_gen_test_with_subprocess():
    yield echo_hello_world()


@pytest.mark.gen_test
def test_gen_test_with_subprocess_no_hang():
    yield echo_hello_world()


@pytest.mark.gen_test_current
def test_gen_test_current():
    yield echo_hello_world()
    # yield gen.sleep(1)
