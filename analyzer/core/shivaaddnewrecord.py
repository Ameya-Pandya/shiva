"""This module inserts spam's details into a temporary list. This gets called 
everytime our analyzer come across a new/distinct spam. First, all the parser 
fields are stored as a dictionary and then, that dictionary is appended into
the list. 
"""

import logging
import server
import shutil
import datetime

from learning import check_mail

def main(mailFields, key, msgMailRequest):
    """Main function. 
    Stores the parsed fields as dictionary and then appends it to our
    temporary list.
    """
    logging.info("Inside shivaaddnewrecord Module.")

    rawspampath = server.shivaconf.get('analyzer', 'rawspampath')
    queuepath = server.shivaconf.get('global', 'queuepath')    
    relay_enabled = server.shivaconf.getboolean('analyzer', 'relay')
    
    records = server.QueueReceiver.records
    source = queuepath + "/new/" + key
    filename = mailFields['s_id'] + "-" + key
    
    phish_flag = checkphishing(mailFields, key, msgMailRequest)

    logging.info("ADD NEW RECORD RETURN")
    """ TEMPORARY, DON'T ADD ANY NEW RECORDS """
    return

    if phish_flag:
        destination = rawspampath + "/phish/" + filename
    else:
        destination = rawspampath + "/spam/" + filename
        
    shutil.copy2(source, destination) # shutil.copy2() copies the meta-data too

    newRecord = { 'headers':mailFields['headers'], 
                'to':mailFields['to'], 
                'from':mailFields['from'], 
                'subject':mailFields['subject'], 
                'date':mailFields['date'], 
                'firstSeen':mailFields['firstSeen'], 
                'lastSeen':mailFields['lastSeen'], 
                'firstRelayed':mailFields['firstRelayed'], 
                'lastRelayed':mailFields['lastRelayed'], 
                'sourceIP':mailFields['sourceIP'], 
                'sensorID':mailFields['sensorID'], 
                'text':mailFields['text'], 
                'html':mailFields['html'], 
                'inlineFileName':mailFields['inlineFileName'], 
                'inlineFile':mailFields['inlineFile'], 
                'inlineFileMd5':mailFields['inlineFileMd5'], 
                'attachmentFileName': mailFields['attachmentFileName'],
                'attachmentFile':mailFields['attachmentFile'], 
                'attachmentFileMd5':mailFields['attachmentFileMd5'], 
                'links':mailFields['links'], 
                'ssdeep':mailFields['ssdeep'], 
                's_id':mailFields['s_id'], 
                'len':mailFields['len'], 
                'phishingHumanCheck': phish_flag,
                'counter':1, 
                'relayed':0 }
    logging.info(str(newRecord))
    if relay_enabled is True:
        relaycounter = server.shivaconf.getint('analyzer', 'globalcounter')

        if (int(server.QueueReceiver.totalRelay) > relaycounter):
            logging.info("[+]shivaaddnewrecord Module: Limit reached. No relay.")
            
        elif next((i for i, sublist in enumerate([myval for myval in server.whitelist_ids.values()]) if mailFields['to'] in sublist), -1) > -1:
            logging.info("[+]shivaaddnewrecord Module: Recipient found in white list - relaying")
            
	    # Following 3 lines does the relaying
	    queuePath = server.shivaconf.get('global', 'queuepath')
	    processMessage = server.QueueReceiver(queuePath)
	    processMessage.process_message(msgMailRequest)

            newRecord['relayed'] += 1
            server.QueueReceiver.totalRelay += 1
        else:
            logging.info("[+]shivaaddnewrecord Module: Adding recipient to whitelist and relaying")
                            
            server.whitelist_ids[mailFields['s_id']] = mailFields['to'].split()
       
            for key, value in server.whitelist_ids.items():
                logging.info("key: %s, value: %s" % (key, value))
            
            # Following 3 lines does the relaying
            queuePath = server.shivaconf.get('global', 'queuepath')
            processMessage = server.QueueReceiver(queuePath)
            processMessage.process_message(msgMailRequest)

            newRecord['relayed'] += 1
            server.QueueReceiver.totalRelay += 1
           
            
    records.insert(0, newRecord) #Inserting new record at the first position.
    del newRecord
    
def checkphishing(mailFields, key, msgMailRequest):
    """ return True if email is considered as phishing, False otherwise"""
    prob = check_mail(mailFields)
    logging.info("Computed probability: " + str(prob))
    
    """ TODO handle computing of boundary """
    
    return False
