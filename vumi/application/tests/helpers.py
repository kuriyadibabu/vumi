from vumi.tests.helpers import (
    MessageHelper, WorkerHelper, MessageDispatchHelper, generate_proxies,
)


class ApplicationHelper(object):
    # TODO: Decide if we actually want to pass the test case in here.
    #       We currently do this for two reasons:
    #       1. We need to get at .mk_config from the persistence mixin. This
    #          should be going away soon when the persistence stuff becomes a
    #          helper.
    #       2. We look at all the test setup class attributes (.transport_name,
    #          .application_class, etc.) to avoid passing them into various
    #          methods. This can probably be avoided with a little effort.
    def __init__(self, test_case, msg_helper_args=None):
        self._test_case = test_case
        self.worker_helper = WorkerHelper(self._test_case.transport_name)
        msg_helper_kw = {
            'transport_name': self._test_case.transport_name,
        }
        if msg_helper_args is not None:
            msg_helper_kw.update(msg_helper_args)
        self.msg_helper = MessageHelper(**msg_helper_kw)
        self.dispatch_helper = MessageDispatchHelper(
            self.msg_helper, self.worker_helper)

        # Proxy methods from our helpers.
        generate_proxies(self, self.msg_helper)
        generate_proxies(self, self.worker_helper)
        generate_proxies(self, self.dispatch_helper)

    def cleanup(self):
        return self.worker_helper.cleanup()

    def get_application(self, config, cls=None, start=True):
        """
        Get an instance of a worker class.

        :param config: Config dict.
        :param cls: The Application class to instantiate.
                    Defaults to :attr:`application_class`
        :param start: True to start the application (default), False otherwise.

        Some default config values are helpfully provided in the
        interests of reducing boilerplate:

        * ``transport_name`` defaults to :attr:`self.transport_name`
        """

        if cls is None:
            cls = self._test_case.application_class
        config = self._test_case.mk_config(config)
        config.setdefault('transport_name', self._test_case.transport_name)
        return self.get_worker(cls, config, start)