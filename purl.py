#!/usr/bin/env python3.5

'''

pman - curl module

'''


# import  threading
import  argparse
from    _colors     import  Colors
import  crunner
import  time
import  sys
import  json
import  pprint
import  socket
import  pycurl
import  io
import  os
# import  uu
# import  zipfile
# import  base64
# import  uuid
# import  shutil
import  pfioh
import  urllib
import  datetime
import  codecs

class Purl():

    ''' Represents an example client. '''

    def qprint(self, msg, **kwargs):

        str_comms  = ""
        for k,v in kwargs.items():
            if k == 'comms':    str_comms  = v

        if not self.b_quiet:
            if str_comms == 'status':   print(Colors.PURPLE,    end="")
            if str_comms == 'error':    print(Colors.RED,       end="")
            if str_comms == "tx":       print(Colors.YELLOW + "---->")
            if str_comms == "rx":       print(Colors.GREEN  + "<----")
            print('%s' % datetime.datetime.now() + " | ",       end="")
            print(msg)
            if str_comms == "tx":       print(Colors.YELLOW + "---->")client
            if str_comms == "rx":       print(Colors.GREEN  + "<----")
            print(Colors.NO_COLOUR, end="")

    def col2_print(self, str_left, str_right):
        print(Colors.WHITE +
              ('%*s' % (self.LC, str_left)), end='')
        print(Colors.LIGHT_BLUE +
              ('%*s' % (self.RC, str_right)) + Colors.NO_COLOUR)

    def __init__(self, **kwargs):
        # threading.Thread.__init__(self)

        # self.str_cmd        = ""
        self.str_ip         = ""
        self.str_port       = ""
        self.str_msg        = ""
        self.str_protocol   = "http"
        self.pp             = pprint.PrettyPrinter(indent=4)
        self.b_man          = False
        self.str_man        = ''
        self.b_quiet        = False
        self.b_pycurl       = False
        self.LC             = 40
        self.RC             = 40

        for key,val in kwargs.items():
            # if key == 'cmd':        self.str_cmd        = val
            if key == 'msg':        self.str_msg        = val
            if key == 'ip':         self.str_ip         = val
            if key == 'port':       self.str_port       = val
            if key == 'b_quiet':    self.b_quiet        = val
            if key == 'man':        self.str_man        = val

        if len(self.str_man):
            print(self.man(on = self.str_man))
            sys.exit(0)

        self.shell_reset()

        if not self.b_quiet:

            print(Colors.LIGHT_GREEN)
            print("""
            \t\t\t+---------------------------+
            \t\t\t| Welcome to purl.py        |
            \t\t\t+---------------------------+
            """)
            print(Colors.CYAN + """
            This program sends CURL type communication to a remote server.

            See 'purl.py --man commands' for more help.

            """)

            if len(sys.argv) == 1: sys.exit(1)

            self.col2_print("Will transmit to",     '%s://%s:%s' % (self.str_protocol, self.str_ip, self.str_port))
            self.col2_print("Inter-transmit delay:",'%d second(s)' % (self.txpause))

    def man(self, **kwargs):
        """
        Print some man for each understood command
        """

        str_man     = 'commands'
        str_amount  = 'full'

        for k, v in kwargs.items():
            if k == 'on':       str_man     = v
            if k == 'amount':   str_amount  = v

        if str_man == 'commands':
            str_commands = Colors.CYAN + """
            The following commands are serviced by this script:
            """ + "\n" + \
            self.man_push(          description =   "short")      + "\n" + \
            self.man_pull(          description =   "short")      + "\n" + \
            Colors.YELLOW + \
            """
            To get detailed help on any of the above commands, type
            """ + Colors.LIGHT_CYAN + \
            """
                ./pman_client.py --man <command>
            """

            return str_commands

        if str_man  == 'push':          return self.man_push(       description  =   str_amount)
        if str_man  == 'pull':          return self.man_pull(       description  =   str_amount)

    def man_push(self, **kwargs):
        """
        """

        b_fullDescription   = False
        str_description     = "full"

        for k,v in kwargs.items():
            if k == 'description':  str_description = v
        if str_description == "full":   b_fullDescription   = True

        str_manTxt =   Colors.LIGHT_CYAN        + \
                       "\t\t%-20s" % "push"       + \
                       Colors.LIGHT_PURPLE      + \
                       "%-60s" % "push data over HTTP." + \
                       Colors.NO_COLOUR

        if b_fullDescription:
            str_manTxt += """

                This pushes a file over HTTP. The 'meta' dictionary
                can be used to specifiy content specific information
                and other information.

                Note that the "file" server is typically *not* on the
                same port as the pman.py process. Usually a prior call
                must be made to pman.py to start a one-shot listener
                on a given port. This port then accepts the file transfer
                from the 'push' method.
                
                The "meta" dictionary consists of several nested 
                dictionaries. In particular, the "remote/path"
                field can be used to suggest a location on the remote
                filesystem to save the transmitted data. Successful
                saving to this path depends on whether or not the
                remote server process actually has permission to
                write in that location.

                """ + Colors.YELLOW + """EXAMPLE:
                """ + Colors.LIGHT_GREEN + """
                ./pman_client.py --ip %s --port %s  --msg  \\
                    '{  "action": "push",
                        "meta":
                            {
                                "local":
                                    {
                                        "path":         "/path/on/client"
                                    },
                                "remote":
                                    {
                                        "path":         "/path/on/server"
                                    },
                                "transport":
                                    {
                                        "mechanism":    "compress",
                                        "compress": {
                                            "encoding": "base64",
                                            "archive":  "zip",
                                            "unpack":   true,
                                            "cleanup":  true
                                        }
                                    }
                            }
                    }'
                """ % (self.str_ip, self.str_port) + Colors.NO_COLOUR  + """
                """ + Colors.YELLOW + """ALTERNATE -- using copy/symlink:
                """ + Colors.LIGHT_GREEN + """
                ./pman_client.py --ip %s --port %s --msg  \\
                    '{  "action": "push",
                        "meta":
                            {
                                "local":
                                    {
                                        "path":         "/path/on/client"
                                    },
                                "remote":
                                    {
                                        "path":         "/path/on/server"
                                    },
                                "transport":
                                    {
                                        "mechanism":    "copy",
                                        "copy": {
                                            "symlink": true
                                        }
                                    }
                            }
                    }'
                """ % (self.str_ip, self.str_port) + Colors.NO_COLOUR

        return str_manTxt

    def man_pull(self, **kwargs):
        """
        """

        b_fullDescription   = False
        str_description     = "full"

        for k,v in kwargs.items():
            if k == 'description':  str_description = v
        if str_description == "full":   b_fullDescription   = True

        str_manTxt =   Colors.LIGHT_CYAN        + \
                       "\t\t%-20s" % "pull"       + \
                       Colors.LIGHT_PURPLE      + \
                       "%-60s" % "pull data over HTTP." + \
                       Colors.NO_COLOUR

        if b_fullDescription:
            str_manTxt += """

                This pulls data over HTTP from a remote server.
                The 'meta' dictionary can be used to specifiy content
                specific information and other detail.

                Note that the "file" server is typically *not* on the
                same port as the pman.py process. Usually a prior call
                must be made to pman.py to start a one-shot listener
                on a given port. This port then accepts the file transfer
                from the 'pull' method.

                The "meta" dictionary consists of several nested
                dictionaries. In particular, the "remote/path"
                field can be used to specify a location on the remote
                filesystem to pull. Successful retrieve from this path
                depends on whether or not the remote server process actually
                has permission to read in that location.

                """ + Colors.YELLOW + """EXAMPLE -- using zip:
                """ + Colors.LIGHT_GREEN + """
                ./pman_client.py --ip %s --port %s  --msg  \\
                    '{  "action": "pull",
                        "meta":
                            {
                                "local":
                                    {
                                        "path":         "/path/on/client"
                                    },
                                "remote":
                                    {
                                        "path":         "/path/on/server"
                                    },
                                "transport":
                                    {
                                        "mechanism":    "compress",
                                        "compress": {
                                            "encoding": "base64",
                                            "archive":  "zip",
                                            "unpack":   true,
                                            "cleanup":  true
                                        }
                                    }
                            }
                    }'
                """ % (self.str_ip, self.str_port) + Colors.NO_COLOUR + """
                """ + Colors.YELLOW + """ALTERNATE -- using copy/symlink:
                """ + Colors.LIGHT_GREEN + """
                ./pman_client.py --ip %s --port %s --msg  \\
                    '{  "action": "pull",
                        "meta":
                            {
                                "local":
                                    {
                                        "path":         "/path/on/client"
                                    },
                                "remote":
                                    {
                                        "path":         "/path/on/server"
                                    },
                                "transport":
                                    {
                                        "mechanism":    "copy",
                                        "copy": {
                                            "symlink": true
                                        }
                                    }
                            }
                    }'
                """ % (self.str_ip, self.str_port) + Colors.NO_COLOUR

        return str_manTxt

    def pull_core(self, d_msg, **kwargs):
        """
        Just the core of the pycurl logic.
        """

        d_meta              = d_msg['meta']
        str_query           = urllib.parse.urlencode(d_msg)
        response            = io.BytesIO()

        d_remote            = d_meta['remote']
        str_ip              = self.str_ip
        str_port            = self.str_port
        if 'ip' in d_remote:
            str_ip          = d_remote['ip']
        if 'port' in d_remote:
            str_port        = d_remote['port']

        self.qprint("http://%s:%s/api/v1/file?%s" % (str_ip, str_port, str_query),
                    comms  = 'tx')

        c                   = pycurl.Curl()
        c.setopt(c.URL, "http://%s:%s/api/v1/file?%s" % (str_ip, str_port, str_query))
        # c.setopt(c.VERBOSE, 1)
        c.setopt(c.FOLLOWLOCATION,  1)
        c.setopt(c.WRITEFUNCTION,   response.write)
        self.qprint("Waiting for PULL response...", comms = 'status')
        c.perform()
        c.close()
        try:
            str_response        = response.getvalue().decode()
        except:
            str_response        = response.getvalue()
        if len(str_response) < 300:
            # It's possible an error occurred for the response to be so short.
            # Try and json load, and examine for 'status' field.
            b_response      = False
            try:
                d_response  = json.loads(str_response)
                b_response  = True
            except:
                pass
            if b_response:
                if not d_response['status']:
                    self.qprint('Some error occurred at remote location:',
                                comms = 'error')
                    return {'status':       False,
                            'mag':          'PULL unsuccessful',
                            'response':     d_response,
                            'timestamp':    '%s' % datetime.datetime.now(),
                            'size':         "{:,}".format(len(str_response))}
                else:
                    return {'status':       d_response['status'],
                            'msg':          'PULL successful',
                            'response':     d_response,
                            'timestamp':    '%s' % datetime.datetime.now(),
                            'size':         "{:,}".format(len(str_response))}

        self.qprint("Received " + Colors.YELLOW + "{:,}".format(len(str_response)) +
                    Colors.PURPLE + " bytes..." ,
                    comms = 'status')

        return {'status':       True,
                'msg':          'PULL successful',
                'response':     str_response,
                'timestamp':    '%s' % datetime.datetime.now(),
                'size':         "{:,}".format(len(str_response))}

    def pull_compress(self, d_msg, **kwargs):
        """
        Handle the "compress" pull operation
        """

        # Parse "header" information
        d_meta                  = d_msg['meta']
        d_local                 = d_meta['local']
        str_localPath           = d_local['path']
        d_remote                = d_meta['remote']
        d_transport             = d_meta['transport']
        d_compress              = d_transport['compress']
        d_ret                   = {}
        d_ret['remoteServer']   = {}
        d_ret['localOp']        = {}

        if 'cleanup' in d_compress:
            b_cleanZip      = d_compress['cleanup']

        # Pull the actual data into a dictionary holder
        d_pull                  = self.pull_core(d_msg)
        d_ret['remoteServer']   = d_pull

        if not d_pull['status']:
            return {'stdout': json.dumps(d_pull['stdout'])}

        str_localStem       = os.path.split(d_remote['path'])[-1]
        str_fileSuffix      = ""
        if d_compress['archive']     == "zip":       str_fileSuffix   = ".zip"

        str_localFile       = "%s/%s%s" % (d_meta['local']['path'], str_localStem, str_fileSuffix)
        str_response        = d_pull['response']
        d_pull['response']  = '<truncated>'


        if d_compress['encoding'] == 'base64':
            self.qprint("Decoding base64 encoded text stream to %s..." % \
                        str_localFile, comms = 'status')
            d_fio = pfioh.base64_process(
                action          = 'decode',
                payloadBytes    = str_response,
                saveToFile      = str_localFile
            )
            d_ret['localOp']['decode']   = d_fio
        else:
            self.qprint("Writing byte stream to %s..." % str_localFile,
                        comms = 'status')
            with open(str_localFile, 'wb') as fh:
                fh.write(str_response)
                fh.close()
            d_ret['localOp']['stream']                  = {}
            d_ret['localOp']['stream']['status']        = True
            d_ret['localOp']['stream']['fileWritten']   = str_localFile
            d_ret['localOp']['stream']['timestamp']     = '%s' % datetime.datetime.now()
            d_ret['localOp']['stream']['filesize']      = "{:,}".format(len(str_response))

        if d_compress['archive'] == 'zip':
            self.qprint("Unzipping %s to %s"  % (str_localFile, str_localPath),
                        comms = 'status')
            d_fio = pfioh.zip_process(
                action          = "unzip",
                payloadFile     = str_localFile,
                path            = str_localPath
            )
            d_ret['localOp']['unzip']       = d_fio
            d_ret['localOp']['unzip']['timestamp']  = '%s' % datetime.datetime.now()
            d_ret['localOp']['unzip']['filesize']   = '%s' % "{:,}".format(os.stat(d_fio['fileProcessed']).st_size)
            d_ret['status']                 = d_fio['status']
            d_ret['msg']                    = d_fio['msg']

        print(d_ret)
        if b_cleanZip and d_ret['status']:
            self.qprint("Removing zip file %s..." % str_localFile,
                        comms = 'status')
            os.remove(str_localFile)

        return d_ret

    def pull_copy(self, d_msg, **kwargs):
        """
        Handle the "copy" pull operation
        """

        # Parse "header" information
        d_meta              = d_msg['meta']
        d_local             = d_meta['local']
        str_localPath       = d_local['path']
        d_remote            = d_meta['remote']
        d_transport         = d_meta['transport']
        d_copy              = d_transport['copy']

        # Pull the actual data into a dictionary holder
        d_curl                      = {}
        d_curl['remoteServer']      = self.pull_core(d_msg)
        d_curl['copy']              = {}
        d_curl['copy']['status']    = d_curl['remoteServer']['status']
        if not d_curl['copy']['status']:
            d_curl['copy']['msg']   = "Copy on remote server failed!"
        else:
            d_curl['copy']['msg']   = "Copy on remote server success!"

        return d_curl

    def pull_remoteLocationCheck(self, d_msg, **kwargs):
        """
        This method checks if the "remote" path is valid.
        """

        # Pull the actual data into a dictionary holder
        d_pull = self.pull_core(d_msg)
        return d_pull

    def localPath_check(self, d_msg, **kwargs):
        """
        Check if a path exists on the local filesystem

        :param self:
        :param kwargs:
        :return:
        """
        d_meta              = d_msg['meta']
        d_local             = d_meta['local']

        str_localPath       = d_local['path']

        b_isFile            = os.path.isfile(str_localPath)
        b_isDir             = os.path.isdir(str_localPath)
        b_exists            = os.path.exists(str_localPath)

        d_ret               = {
            'status':  b_exists,
            'isfile':  b_isFile,
            'isdir':   b_isDir
        }

        return {'check':        d_ret,
                'status':       d_ret['status'],
                'timestamp':    '%s' % datetime.datetime.now()}

    def pull(self, d_msg, **kwargs):
        """
        Pulls data from a remote server using pycurl.

        This method assumes that a prior call has "setup" a remote fileio
        listener and has the ip:port of that instance.

        Essentially, this method is the central dispatching nexus to various
        specialized pull operations.

        :param d_msg:
        :param kwargs:
        :return:
        """

        return self.remoteOp_do(d_msg, action = 'pull')

    def push_core(self, d_msg, **kwargs):
        """

        """

        str_fileToProcess   = ""
        str_encoding        = "none"
        d_ret               = {}
        for k,v in kwargs.items():
            if k == 'fileToPush':   str_fileToProcess   = v
            if k == 'encoding':     str_encoding        = v
            if k == 'd_ret':        d_ret               = v

        d_meta              = d_msg['meta']
        str_meta            = json.dumps(d_meta)

        d_remote            = d_meta['remote']
        str_ip              = self.str_ip
        str_port            = self.str_port
        if 'ip' in d_remote:
            str_ip          = d_remote['ip']
        if 'port' in d_remote:
            str_port        = d_remote['port']

        d_transport         = d_meta['transport']

        response            = io.BytesIO()

        self.qprint("http://%s:%s/api/v1/cmd/" % (str_ip, str_port) + '\n '+ str(d_msg),
                    comms  = 'tx')

        c = pycurl.Curl()
        c.setopt(c.POST, 1)
        c.setopt(c.URL, "http://%s:%s/api/v1/cmd/" % (str_ip, str_port))
        if str_fileToProcess:
            fread               = open(str_fileToProcess, "rb")
            filesize            = os.path.getsize(str_fileToProcess)
            c.setopt(c.HTTPPOST, [  ("local",    (c.FORM_FILE, str_fileToProcess)),
                                    ("encoding",  str_encoding),
                                    ("d_meta",    str_meta),
                                    ("filename",  str_fileToProcess)]
                     )
            c.setopt(c.READFUNCTION,    fread.read)
            c.setopt(c.POSTFIELDSIZE,   filesize)
        else:
            c.setopt(c.HTTPPOST, [
                                    ("d_meta",    str_meta),
                                  ]
                     )
        # c.setopt(c.VERBOSE, 1)
        c.setopt(c.WRITEFUNCTION,   response.write)
        if str_fileToProcess:
            self.qprint("Transmitting " + Colors.YELLOW + "{:,}".format(os.stat(str_fileToProcess).st_size) + \
                        Colors.PURPLE + " bytes...",
                        comms = 'status')
        else:
            self.qprint("Sending ctl data to server...",
                        comms = 'status')
        c.perform()
        c.close()

        str_response        = response.getvalue().decode()
        d_ret['push_core']  = json.loads(str_response)
        d_ret['status']     = d_ret['push_core']['status']
        d_ret['msg']        = 'push OK.'
        self.qprint(d_ret, comms = 'rx')

        return d_ret

    def push_compress(self, d_msg, **kwargs):
        """
        """

        d_meta              = d_msg['meta']
        str_meta            = json.dumps(d_meta)
        d_local             = d_meta['local']
        str_localPath       = d_local['path']

        d_remote            = d_meta['remote']
        str_ip              = self.str_ip
        str_port            = self.str_port
        if 'ip' in d_remote:
            str_ip          = d_remote['ip']
        if 'port' in d_remote:
            str_port        = d_remote['port']

        str_mechanism       = ""
        str_encoding        = ""
        str_archive         = ""
        d_transport         = d_meta['transport']
        if 'compress' in d_transport:
            d_compress      = d_transport['compress']
            str_archive     = d_compress['archive']
            str_encoding    = d_compress['encoding']

        str_remotePath      = d_remote['path']

        if 'cleanup' in d_compress:
            b_cleanZip      = d_compress['cleanup']


        str_fileToProcess   = str_localPath
        str_zipFile         = ""
        str_base64File      = ""

        b_zip               = True

        if str_archive      == 'zip':   b_zip   = True
        else:                           b_zip   = False

        if os.path.isdir(str_localPath):
            b_zip           = True
            str_archive     = 'zip'

        d_ret               = {}
        d_ret['local']      = {}
        # If specified (or if the target is a directory), create zip archive
        # of the local path
        if b_zip:
            self.qprint("Zipping target...", comms = 'status')
            d_fio   = pfioh.zip_process(
                action  = 'zip',
                path    = str_localPath,
                arcroot = str_localPath
            )
            if not d_fio['status']: return {'stdout': json.dumps(d_fio)}
            str_fileToProcess   = d_fio['fileProcessed']
            str_zipFile         = str_fileToProcess
            d_ret['local']['zip']               = d_fio

        # Encode possible binary filedata in base64 suitable for text-only
        # transmission.
        if str_encoding     == 'base64':
            self.qprint("base64 encoding target...", comms = 'status')
            d_fio   = pfioh.base64_process(
                action      = 'encode',
                payloadFile = str_fileToProcess,
                saveToFile  = str_fileToProcess + ".b64"
            )
            str_fileToProcess       = d_fio['fileProcessed']
            str_base64File          = str_fileToProcess
            d_ret['local']['encoding']                   = d_fio

        # Push the actual file -- note the d_ret!
        d_ret['remoteServer']  = self.push_core(    d_msg,
                                                    fileToPush  = str_fileToProcess,
                                                    encoding    = str_encoding)
                                                    # d_ret       = d_ret)
        d_ret['status'] = d_ret['remoteServer']['status']
        d_ret['msg']    = d_ret['remoteServer']['msg']

        if b_cleanZip:
            self.qprint("Removing temp files...", comms = 'status')
            if os.path.isfile(str_zipFile):     os.remove(str_zipFile)
            if os.path.isfile(str_base64File):  os.remove(str_base64File)

        return d_ret

        # return {'stdout': {'return' : d_ret},
        #         'status': d_ret['fromServer']['status']}

    def push_copy(self, d_msg, **kwargs):
        """
        Handle the "copy" pull operation
        """

        # Parse "header" information
        d_meta              = d_msg['meta']
        d_local             = d_meta['local']
        str_localPath       = d_local['path']
        d_remote            = d_meta['remote']
        d_transport         = d_meta['transport']
        d_copy              = d_transport['copy']

        # Pull the actual data into a dictionary holder
        d_curl                      = {}
        d_curl['remoteServer']      = self.push_core(d_msg)
        d_curl['copy']              = {}
        d_curl['copy']['status']    = d_curl['remoteServer']['status']
        if not d_curl['copy']['status']:
            d_curl['copy']['msg']   = "Copy on remote server failed!"
        else:
            d_curl['copy']['msg']   = "Copy on remote server success!"

        return d_curl

    def remoteOp_do(self, d_msg, **kwargs):
        """
        Entry point for push/pull calls.

        Essentially, this method is the central dispatching nexus to various
        specialized push operations.

        """

        d_meta              = d_msg['meta']
        d_transport         = d_meta['transport']
        b_OK                = True
        d_ret               = {}

        str_action          = "pull"
        for k,v, in kwargs.items():
            if k == 'action':   str_action  = v

        # First check on the paths, both local and remote
        self.qprint('Checking local path status...', comms = 'status')
        d_ret['localCheck'] = self.localPath_check(d_msg)
        if not d_ret['localCheck']['status']:
            self.qprint('An error occurred while checking on the local path.',
                        comms = 'error')
            d_ret['localCheck']['msg']          = 'The local path spec is invalid!'
            d_ret['localCheck']['status'] = False
            b_OK            = False
        else:
            d_ret['localCheck']['msg']          = "Check on local path successful."
        d_ret['status']     = d_ret['localCheck']['status']
        d_ret['msg']        = d_ret['localCheck']['msg']

        if b_OK:
            d_transport['checkRemote']  = True
            self.qprint('Checking remote path status...', comms = 'status')
            d_ret['remoteCheck']   = self.pull_remoteLocationCheck(d_msg)
            self.qprint(str(d_ret), comms = 'rx')
            if not d_ret['remoteCheck']['status']:
                self.qprint('An error occurred while checking the remote server.',
                            comms = 'error')
                d_ret['remoteCheck']['msg']     = "The remote path spec is invalid!"
                b_OK        = False
            else:
                d_ret['remoteCheck']['msg']     = "Check on remote path successful."
            d_transport['checkRemote']  = False
            d_ret['status']             = d_ret['localCheck']['status']
            d_ret['msg']                = d_ret['localCheck']['msg']

        b_jobExec           = False
        if b_OK:
            if 'compress' in d_transport and d_ret['status']:
                self.qprint('Calling %s_compress()...' % str_action, comms = 'status')
                d_ret['compress']   = eval("self.%s_compress(d_msg, **kwargs)" % str_action)
                d_ret['status']     = d_ret['compress']['status']
                d_ret['msg']        = d_ret['compress']['msg']
                b_jobExec       = True

            if 'copy' in d_transport:
                self.qprint('Calling %s_copy()...' % str_action, comms = 'status')
                d_ret['copyOp']     = eval("self.%s_copy(d_msg, **kwargs)" % str_action)
                d_ret['status']     = d_ret['copyOp']['copy']['status']
                d_ret['msg']        = d_ret['copyOp']['copy']['msg']
                b_jobExec       = True

        if not b_jobExec:
            d_ret['status']   = False
            d_ret['msg']      = 'No push/pull operation was performed! A filepath check failed!'

        d_meta['ctl']       = {
            'serverCmd':    'quit'
        }

        self.qprint('Shutting down server...', comms = 'status')
        d_shutdown  = self.push_core(d_msg, fileToPush = None)

        return {'stdout': json.dumps(d_ret)}


    def push(self, d_msg, **kwargs):
        """
        Push data to a remote server using pycurl.

        Essentially, this method is the central dispatching nexus to various
        specialized push operations.

        """

        return self.remoteOp_do(d_msg, action = 'push')


if __name__ == '__main__':

    str_defIP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

    parser  = argparse.ArgumentParser(description = 'curl-type comms in the pman system')

    parser.add_argument(
        '--msg',
        action  = 'store',
        dest    = 'msg',
        default = '',
        help    = 'Control signal to send to pman.'
    )
    parser.add_argument(
        '--ip',
        action  = 'store',
        dest    = 'ip',
        default = str_defIP,
        help    = 'IP to connect.'
    )
    parser.add_argument(
        '--port',
        action  = 'store',
        dest    = 'port',
        default = '5010',
        help    = 'Port to use.'
    )
    parser.add_argument(
        '--quiet',
        help    = 'if specified, only echo JSON output from server response',
        dest    = 'b_quiet',
        action  = 'store_true',
        default = False
    )
    parser.add_argument(
        '--man',
        help    = 'request help',
        dest    = 'man',
        action  = 'store',
        default = ''
    )
    parser.add_argument(
        '--pycurl',
        help    = 'use the internal python curl API',
        dest    = 'b_pycurl',
        action  = 'store_true',
        default = False
    )

    args    = parser.parse_args()
    purl  = Purl(
                        msg         = args.msg,
                        ip          = args.ip,
                        port        = args.port,
                        b_quiet     = args.b_quiet,
                        man         = args.man
                )
    # client.run()
    purl.push(args.msg)
    sys.exit(0)