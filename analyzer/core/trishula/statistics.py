"""
  Module generate simple statistics
"""
import logging

import matplotlib.pyplot as plot
import numpy as np


import backend_operations
    
def prepare_matrix():
    """     
    reads results of learning into database and returns them as a matrix
    suitable for further processing
    
    Method should be called  when database is in consistent state.
    
    Produced matrix has format [M + 1, N + 1]
    
    M is count of emails in database, first two rows contains rule codes.
    Firs column of each of M rows contains derived status (1 for phishing, 0 for spam)
    
    
    Entries [0][0], [1][0] are constant with no practical meaning
    
    Matrix format:
    
    
    [ '_code'         , code1          , code2           ... codeN           ]
    [ derived_status1 , rule_1_1_result, rule_1_2_result ... rule_1_N_result ]
    [ derived_status2 , rule_2_1_result, rule_2_2_result ... rule_2_N_result ]
    .                   .                .                   .
    .                   .                .                   .
    .                   .                .                   .
    [ derived_statusM , rule_M_1_result, rule_M_2_result ... rule_M_N_result ] 
    """     
    matrix = []
    
    # indicator of walkthrough 
    first_loop = True;
    
    for email_id in backend_operations.get_email_ids():
        
        email_result = backend_operations.get_results_of_email(email_id)
        if 'rules' in email_result:
            
            #sort rules to ensure same order in all rows of matrix
            sorted_rules = sorted(email_result['rules'],key=lambda a: a['code'])
            
            #add first row into matrix (codes) during first walkthrough
            if first_loop:
                first_row = ['_derived_result']
                first_row.extend(map(lambda a: a['code'], sorted_rules))
                
                matrix.append(first_row)
                first_loop = False
            
            
            # append row of matrix
            sorted_resuls_vector = [1] if email_result['derivedStatus'] else [0]
            sorted_resuls_vector.extend(map(lambda a: a['result'], sorted_rules))
            matrix.append(sorted_resuls_vector)
         
    # write matrix to file   
    out_file = open('../../../web/learning_output.csv','w')
    if out_file:
        for row in matrix:
            out_file.write(','.join(map(lambda a: str(a), row)))
            out_file.write('\n')
        out_file.close()
            
    return matrix

def generate_rules_graph(data={}, title='', filename=''):
    """
    generate graph of rule matching percentage based on email sensors 
    for input format description, see 
    """
    
    color_list = 'rgbcmyk'
    color_index = 0
    rule_codes = data['_rule_codes']   
    
    for sensor, rule_vals in data.iteritems():
        if sensor.startswith('_rule') or sensor.startswith('_total'):
            continue
        current_color = color_list[color_index % 7]
        color_index += 1
        sensor_total = data['_total_' + sensor]

        logging.critical(str(rule_vals))

        plot.plot(np.arange(len(rule_vals)) + 0.5, map(lambda a: (a / float(sensor_total)) * 100, rule_vals), 
                label=sensor + ' ({})'.format(sensor_total), 
                linestyle='-',
                linewidth=0.8,
                color=current_color,
                markerfacecolor=current_color,
                markersize=12, 
                marker='o', 
                antialiased=True)
    
    plot.xticks(np.arange(len(rule_codes)) + 0.5, rule_codes)
    plot.legend(loc='upper center', bbox_to_anchor=(0.5,-0.2))
    
    
    plot.grid(True)
    plot.xlabel('Rules',fontsize=18)
    plot.ylabel('Percentage of matching rules',fontsize=18)
    
    final_title = 'Statistics of rules matching by source of email\n'
    if title:
        final_title = title + "\n"
    plot.title(final_title, fontsize=20)
    
    final_filename = 'rules_graph.png'
    if filename:
        final_filename = filename
        
    fig = plot.gcf()
    fig.set_size_inches(15, 8)
    plot.savefig('../../../web/images/' + final_filename, bbox_inches='tight')
    plot.close()
    
def generate_roc_graph(data=[]):
    """
    generate ROC curve of detection True positive/False negative rate
    """
    from sklearn import metrics
    
    if not data:
        return

    shiva_score_probs = map(lambda a: a[0], data)
    spamass_score_probs = map(lambda a: a[1], data) 
    derived_results = map(lambda a: a[2], data)

    fpr_shiva, tpr_shiva, _ = metrics.roc_curve(derived_results, shiva_score_probs, pos_label=1)
    fpr_spamass, tpr_spamass, _= metrics.roc_curve(derived_results, spamass_score_probs, pos_label=1)
    
    roc_auc_shiva = metrics.auc(fpr_shiva, tpr_shiva)
    roc_auc_spamass = metrics.auc(fpr_spamass, tpr_spamass)
 
    plot.figure()
    plot.plot(fpr_shiva, tpr_shiva, label='ROC curve SHIVA (area = %0.2f)' % roc_auc_shiva)
    plot.plot(fpr_spamass, tpr_spamass, label='ROC curve spamassassin (area = %0.2f)' % roc_auc_spamass)
    plot.plot([0, 1], [0, 1], 'k--')
    plot.xlim([0.0, 1.0])
    plot.ylim([0.0, 1.05])
    plot.xlabel('False Positive Rate')
    plot.ylabel('True Positive Rate')
    plot.title('Shiva honeypot classification ROC')
    plot.legend(loc="lower right")
    plot.savefig('../../../web/images/roc_graph.png', bbox_inches='tight')
    plot.close()
    

         
            
    
        

