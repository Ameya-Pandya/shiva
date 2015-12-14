"""
The majority of the server related things Lamson needs to run, like receivers, 
relays, and queue processors.

SHIVA - QueueReceiver module has been amended to
* Read to configuration file
* Start the scheduler
* Initializing the relay counter and spam list
* And, making call to our customised module shivamailparser
"""

import smtplib
import smtpd
import asyncore
import threading
import socket
import logging
import queue
import mail
import routing
import time
import traceback
import ConfigParser
import os

from lamson.bounce import PRIMARY_STATUS_CODES, SECONDARY_STATUS_CODES, COMBINED_STATUS_CODES

import shivascheduler
import shivamailparser
import shivadbconfig
import trishula.learning as learning
import trishula.web as web
import MySQLdb as mdb

confpath = os.path.dirname(os.path.realpath(__file__)) + "/../../../../../shiva.conf"
shivaconf = ConfigParser.ConfigParser()
shivaconf.read(confpath)

# Global dictionary to store whitelist email ids
whitelist_ids = {'spammers_email':[]}


def undeliverable_message(raw_message, failure_type):
    """
    Used universally in this file to shove totally screwed messages
    into the routing.Router.UNDELIVERABLE_QUEUE (if it's set).
    """
    if routing.Router.UNDELIVERABLE_QUEUE:
        key = routing.Router.UNDELIVERABLE_QUEUE.push(raw_message)

        logging.error("Failed to deliver message because of %r, put it in "
                      "undeliverable queue with key %r", failure_type, key)

class SMTPError(Exception):
    """
    You can raise this error when you want to abort with a SMTP error code to
    the client.  This is really only relevant when you're using the
    SMTPReceiver and the client understands the error.

    If you give a message than it'll use that, but it'll also produce a
    consistent error message based on your code.  It uses the errors in
    lamson.bounce to produce them.
    """
    def __init__(self, code, message=None):
        self.code = code
        self.message = message or self.error_for_code(code)

        Exception.__init__(self, "%d %s" % (self.code, self.message))

    def error_for_code(self, code):
        primary, secondary, tertiary = str(code)
        
        primary = PRIMARY_STATUS_CODES.get(primary, "")
        secondary = SECONDARY_STATUS_CODES.get(secondary, "")
        combined = COMBINED_STATUS_CODES.get(primary + secondary, "")

        return " ".join([primary, secondary, combined]).strip()


class Relay(object):
    """
    Used to talk to your "relay server" or smart host, this is probably the most 
    important class in the handlers next to the lamson.routing.Router.
    It supports a few simple operations for sending mail, replying, and can
    log the protocol it uses to stderr if you set debug=1 on __init__.
    """
    def __init__(self, host='127.0.0.1', port=25, username=None, password=None,
                 ssl=False, starttls=False, debug=0):
        """
        The hostname and port we're connecting to, and the debug level (default to 0).
        Optional username and password for smtp authentication.
        If ssl is True smtplib.SMTP_SSL will be used.
        If starttls is True (and ssl False), smtp connection will be put in TLS mode.
        It does the hard work of delivering messages to the relay host.
        """
        self.hostname = host
        self.port = port
        self.debug = debug
        self.username = username
        self.password = password
        self.ssl = ssl
        self.starttls = starttls

    def configure_relay(self, hostname):
        if self.ssl:
            relay_host = smtplib.SMTP_SSL(hostname, self.port)
        else:
            relay_host = smtplib.SMTP(hostname, self.port)

        relay_host.set_debuglevel(self.debug)

        if self.starttls:
            relay_host.starttls()
        if self.username and self.password:
            relay_host.login(self.username, self.password)

        assert relay_host, 'Code error, tell Zed.'
        return relay_host

    def deliver(self, message, To=None, From=None):
        """
        Takes a fully formed email message and delivers it to the
        configured relay server.

        You can pass in an alternate To and From, which will be used in the
        SMTP send lines rather than what's in the message.
        """
        recipient = To or message['To']
        sender = From or message['From']

        hostname = self.hostname or self.resolve_relay_host(recipient)

        try:
            relay_host = self.configure_relay(hostname)
        except socket.error:
            logging.exception("Failed to connect to host %s:%d" % (hostname, self.port))
            return

        relay_host.sendmail(sender, recipient, str(message))
        #relay_host.sendmail(sender, recipient.split(","), str(message))	# Shiva - sendmail needs 'list' of recipients not strings. Fixed in lamson now.
        relay_host.quit()

    def resolve_relay_host(self, To):
        import DNS
        address, target_host = To.split('@')
        mx_hosts = DNS.mxlookup(target_host)

        if not mx_hosts:
            logging.debug("Domain %r does not have an MX record, using %r instead.", target_host, target_host)
            return target_host
        else:
            logging.debug("Delivering to MX record %r for target %r", mx_hosts[0], target_host)
            return mx_hosts[0][1]


    def __repr__(self):
        """Used in logging and debugging to indicate where this relay goes."""
        return "<Relay to (%s:%d)>" % (self.hostname, self.port)


    def reply(self, original, From, Subject, Body):
        """Calls self.send but with the from and to of the original message reversed."""
        self.send(original['from'], From=From, Subject=Subject, Body=Body)

    def send(self, To, From, Subject, Body):
        """
        Does what it says, sends an email.  If you need something more complex
        then look at lamson.mail.MailResponse.
        """
        msg = mail.MailResponse(To=To, From=From, Subject=Subject, Body=Body)
        self.deliver(msg)



class SMTPReceiver(smtpd.SMTPServer):
    """Receives emails and hands it to the Router for further processing."""

    def __init__(self, host='127.0.0.1', port=8825):
        """
        Initializes to bind on the given port and host/ipaddress.  Typically
        in deployment you'd give 0.0.0.0 for "all internet devices" but consult
        your operating system.

        This uses smtpd.SMTPServer in the __init__, which means that you have to 
        call this far after you use python-daemonize or else daemonize will
        close the socket.
        """
        self.host = host
        self.port = port
        smtpd.SMTPServer.__init__(self, (self.host, self.port), None)

    def start(self):
        """
        Kicks everything into gear and starts listening on the port.  This
        fires off threads and waits until they are done.
        """
        logging.info("SMTPReceiver started on %s:%d." % (self.host, self.port))
        self.poller = threading.Thread(target=asyncore.loop,
                kwargs={'timeout':0.1, 'use_poll':True})
        self.poller.start()

    def process_message(self, Peer, From, To, Data):
        """
        Called by smtpd.SMTPServer when there's a message received.
        """

        try:
            logging.debug("Message received from Peer: %r, From: %r, to To %r." % (Peer, From, To))
            routing.Router.deliver(mail.MailRequest(Peer, From, To, Data))
        except SMTPError, err:
            # looks like they want to return an error, so send it out
            return str(err)
            undeliverable_message(Data, "Handler raised SMTPError on purpose: %s" % err)
        except:
            logging.exception("Exception while processing message from Peer: %r, From: %r, to To %r." %
                          (Peer, From, To))
            undeliverable_message(Data, "Error in message %r:%r:%r, look in logs." % (Peer, From, To))


    def close(self):
        """Doesn't do anything except log who called this, since nobody should.  Ever."""
        logging.error(traceback.format_exc())


class QueueReceiver(object):
    """
    Rather than listen on a socket this will watch a queue directory and
    process messages it recieves from that.  It works in almost the exact
    same way otherwise.
    """
    
    records = []  # Global list that will hold spam records till they're pushed to db.
    deep_records = []   # Copy of records
    totalRelay = 0  # Global relay counter
    
    
    def __init__(self, queue_dir, sleep=10, size_limit=0, oversize_dir=None):
        """
        The router should be fully configured and ready to work, the
        queue_dir can be a fully qualified path or relative.
        """
        self.queue = queue.Queue(queue_dir, pop_limit=size_limit,
                                 oversize_dir=oversize_dir)
        self.queue_dir = queue_dir
        self.sleep = sleep

    def start(self, one_shot=False):
        """
        Start simply loops indefinitely sleeping and pulling messages
        off for processing when they are available.

        If you give one_shot=True it will run once rather than do a big
        while loop with a sleep.
        """

        """setup web interface and api"""
        if not one_shot: 
            web.main()
        
        """ remove possible lock file from previous learning """
        learning.free_learning_lock()

        logging.info("Queue receiver started on queue dir %s" %
                     (self.queue_dir))
        logging.debug("Sleeping for %d seconds..." % self.sleep)
        
        
        
        shivascheduler.schedule()
        inq = queue.Queue(self.queue_dir)
        
        # Get email-id's of spammers. Mail must get relayed to them.
        mainDb = shivadbconfig.dbconnectmain()
        whitelist = "SELECT `recipients` from `whitelist`"
        
        try:
            mainDb.execute(whitelist)
            record = mainDb.fetchone()

            global whitelist_ids
            
                  
            if ((record is None) or (record[0] is None)):
                whitelist_ids['spammers_email'] = []
            else:
                whitelist_ids['spammers_email'] = (record[0].encode('utf-8')).split(",")[-100:]
                whitelist_ids['spammers_email'] = list(set(whitelist_ids['spammers_email']))
                
                logging.info("[+] server Module: whitelist recipients:")
                for key, value in whitelist_ids.items():
                    logging.info("key: %s, value: %s" % (key, value))
            mainDb.close()
        except mdb.Error, e:
            logging.critical("[-] Error (Module server.py) - some issue obtaining whitelist: %s" % e)
            

        while True:
            keys = inq.keys()
            for key in keys:
                msg = inq.get(key)

                if msg:
                    logging.debug("Pulled message with key: %r off", key)
                    
                    # Shiva - Interupting normal flow execution of QueueReceiver here and calling our
                    # customized module shivamailparser to deal with mails retrieved from the queue.
                    # Send "key", which is actually the name of spam file in queue, 
                    # msg", is actually complete mail body, is in MailRequest format
	
                    shivamailparser.main(key, msg)
                                        
                    # Irrespective of mail relayed or not, it has to be cleared from queue. 
                    # Hence, whether process_message executes or not,
                    # the control comes back to this point and ultimately spam gets removed from queue
                    logging.debug("Removed %r key from queue.\n\n", key)
		
	        inq.remove(key)

            if one_shot: 
                return
            else:
                time.sleep(self.sleep)
                
    # Function gets called only when a spam has to be relayed            
    def process_message(self, msg):
        """
        Exactly the same as SMTPReceiver.process_message but just designed for the queue's
        quirks.
        """
        #self.msg = self.start.msg

        try:
            Peer = self.queue_dir
            From = msg['from']
            To = [msg['to']]

            logging.debug("Message received from Peer: %r, From: %r, to To %r." % (Peer, From, To))
            routing.Router.deliver(msg)
        except SMTPError, err:
            # looks like they want to return an error, so send it out
            logging.exception("Raising SMTPError when running in a QueueReceiver is unsupported.")
            undeliverable_message(msg.original, err.message)
        except:
            logging.exception("Exception while processing message from Peer: "
                              "%r, From: %r, to To %r." % (Peer, From, To))
            undeliverable_message(msg.original, "Router failed to catch exception.")
