# -*- test-case-name: vumi.workers.ttc.tests.test_ttc -*-

from twisted.python import log
from twisted.internet.defer import inlineCallbacks

from vumi.application import ApplicationWorker
from vumi.message import Message

from vumi.database.base import setup_db, get_db, close_db, UglyModel

class ParticipantModel(UglyModel):
    TABLE_NAME = 'participant_items'
    fields = (
        ('id', 'SERIAL PRIMARY KEY'),
        ('phone_number','int8 UNIQUE NOT NULL'),
        )
    indexes = ('phone_number',)
    
    @classmethod
    def get_items(cls, txn):
        items = cls.run_select(txn,'')
        if items:
            items[:] = [cls(txn,*item) for item in items]
            return items
            #return cls(txn, *items[0])
        return None
    
    @classmethod
    def create_item(cls, txn, number):
        params = {'phone_number': number}
        txn.execute(cls.insert_values_query(**params),params)
        txn.execute("SELECT lastval()")
        return txn.fetchone()[0]

class TtcGenericWorker(ApplicationWorker):
    
    @inlineCallbacks
    def startWorker(self):
        super(TtcGenericWorker, self).startWorker()
        self.control_consumer = yield self.consume(
            '%(transport_name)s.control' % self.config,
            self.consume_control,
            message_class=Message)
        self.record = []
        self.setup_db = setup_db(ParticipantModel)
        self.db = setup_db('test', database='test',
                 user='vumi',
                 password='vumi',
                 host='localhost')
        self.db.runQuery('SELECT 1')
    
    def consume_user_message(self, message):
        log.msg("User message: %s" % message['content'])
        
    def consume_control(self, message):
        log.msg("Control message!")
        #data = message.payload['data']
        program = message.get('program', {})
        self.record.append(message)
         
        self.db.runInteraction(ParticipantModel.create_item,68473)        
        #name = program.get('name')
        #group = program.get('group',{})
        #number = group.get('number')
        #log.msg("Control message %s to be add %s" % (number,name))
    
    def dispatch_event(self, message):
        log.msg("Event message!")
    