from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class CephRadosgwProvider(RelationBase):
    scope = scopes.UNIT

    @hook('{provides:ceph-radosgw}-relation-{joined,changed}')
    def changed(self):
        self.set_state('{relation_name}.connected')
        # service = hookenv.remote_service_name()
        conversation = self.conversation()
        if conversation.get_remote('broker_req'):
            self.set_state('{relation_name}.broker_requested')

    def provide_auth(self, service, key, fsid, auth_supported, public_address):
        """
        Provide a token to a requesting service.
        :param str service: The service which requested the key
        :param str key: The key to access Ceph
        :param str fsid: FSID for the Ceph cluster
        :param str auth_supported: Supported auth methods
        :param str public_address: Ceph's public address
        """
        conversation = self.conversation(scope=service)
        opts = {
            'radosgw_key': key,
            'fsid': fsid,
            'auth': auth_supported,
            'ceph-public-address': public_address,
        }
        conversation.set_remote(**opts)

    def requested_keys(self):
        """
        Return a list of tuples mapping a service name to the key name
        requested by that service.
        Example usage::
            for service, key in ceph.requested_keys():
                ceph.provide_auth(service, key, auth, public_address)
        """
        for conversation in self.conversations():
            service = conversation.scope
            key = self.requested_key(service)
            if key is None:
                yield service

    def requested_key(self, service):
        """
        Return the key provided to the requesting service.
        """
        return self.conversation(scope=service).get_remote('key')

    def provide_broker_token(self, service, unit_response_key, token):
        """
        Provide a token to a requesting service.
        :param str service: The service which requested the key
        :param str unit_response_key: The unique key for the unit
        :param str token: Broker token top provide
        """
        conversation = self.conversation(scope=service)
        conversation.set_remote(**{
            unit_response_key: token,
        })

    def requested_tokens(self):
        """
        Return a list of tuples mapping a service name to the token name
        requested by that service.
        Example usage::
            for service, token in ceph.requested_tokens():
                ceph.provide_auth(service, token, auth, public_address)
        """
        for conversation in self.conversations():
            service = conversation.scope
            token = self.requested_token(service)
            if token is None:
                yield service, token

    def requested_token(self, service):
        """
        Return the token provided to the requesting service.
        """
        return self.conversation(scope=service).get_remote('broker_req')
