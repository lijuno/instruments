"""
Utility functions
"""
import smtplib
import ConfigParser
import sys

def twoscomplement(int_in, bitsize):
    """
    Compute two's complement
    http://stackoverflow.com/a/1604701/1527875
    """
    return int_in- (1<<bitsize)
        
def split_string(str_in, stepsize):
    """
    Split a string every N charaters and store into an array 
    """
    str_out = [str_in[ii:ii+stepsize] for ii in range(0, len(str_in), stepsize)]
    return str_out
    

def write_data_n1(filename, arr1):
    """
    Write data to N-by-1 array
    """
    f = open(filename, 'w')
    for ii in range(len(arr1)):
        f.write('%s\n' % str(arr1[ii]))
    f.close()
    
def write_data_n2(filename, arr1, arr2):
    """
    Write data to N-by-2 array
    """
    f = open(filename, 'w')
    for ii in range(len(arr1)):
        f.write('%s\t%s\n' % (str(arr1[ii]), str(arr2[ii])))
    f.close()
   
def write_data_n3(filename, arr1, arr2, arr3):
    """
    Write data to N-by-3 array
    """
    f = open(filename, 'w')
    for ii in range(len(arr1)):
        f.write('%s\t%s\t%s\n' % (str(arr1[ii]), str(arr2[ii]), str(arr3[ii])))
    f.close()

def append_to_file_n2(filename, x1, x2, str_format):
    """
    Write to file in append mode; will not overwrite existing content
    """
    f = open(filename, 'a')
    if str_format == 'fe':
        f.write('%f\t%e\n' % (x1, x2))
    elif str_format == 'ff':
        f.write('%f\t%f\n' % (x1, x2))
    elif str_format == 'ss':
        f.write('%s\t%s\n' % (x1, x2))
    f.close()

def iprint(msg, verbose=True):
    """
    Add a on/off switch to print: when verbose is False, do nothing; when verbose is True, print as mormal
    """
    if verbose:
        print msg
    else:
        pass


def str2list(s):
    # Helper function for sendemail()
    # If input is a string, convert it to list.
    # If it is a list, keep it as is
    if type(s) is str:
        return [s]
    elif type(s) is list:
        return s
    else:
        print 'Input is neither str nor list. Something is wrong...'
        sys.exit(2)

def sendemail(to, subject, body, **kwargs):
    """
    Send email in Python
    Input args:
        to: destination email address(es), a string or a string list
        **kwargs, optional args: 
            cc: CC address(es), a string or a string list
            bcc: BCC address(es), a string or a string list
            profile: choose a profile in rcfile, a string; the default is 'aim'
            rcfile: the path for rcfile, a string
    Examples:
    send_email('user1@example.com', 'Test', 'This is a test'); 
    send_email('user1@example.com', 'Test', 'This is a test', profile='aim'); 
    send_email('user1@example.com', 'Test', 'This is a test', cc=['user2@example.com', 'user3@example.com'], bcc=['user3@example.com']);
    """
    # Default values
    to = str2list(to)
    cc = []
    bcc = []
    profile = 'aim'
    rcfile = '/home/ll3kx/.sendemailrc'
    
    for key, val in kwargs.iteritems():
        if key == 'cc':
            cc = str2list(val)
        elif key == 'bcc':
            bcc = str2list(val)
        elif key == 'rcfile':
            if not (type(val) is str):
                print 'rcfile should be str type'
                sys.exit(2)
            else: 
                rcfile = val
        elif key == 'profile':
            if not (type(val) is str):
                print 'profile should be str type'
                sys.exit(2)
            else: 
                profile = val
       
    config = ConfigParser.ConfigParser()
    config.read(rcfile)

    if not(profile in config.sections()):
        print 'Profile not in the configuration. Exiting...'
        sys.exit(2)
    
    sender= config.get(profile, 'from')
    username = config.get(profile, 'username')
    password = config.get(profile, 'password')
    smtphost = config.get(profile, 'smtphost')
    
    msg = '\r\n'.join([
          "From: %s" % sender, 
          "To: %s" % ','.join(to),
          "CC: %s" % ','.join(cc),
          "BCC: %s" % ','.join(bcc), 
          "Subject: %s" % subject,
          "",
          body])
    #print msg
    server = smtplib.SMTP(smtphost)
    server.login(username, password)
    server.sendmail(sender, to+cc+bcc, msg)
    server.quit()