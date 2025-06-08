NORMAL_PORT_LIST: list[str] = [
    '21/', '22/', '25/', '53/udp', '80/', '443/', '110/', '143/', '993/', '995/', '465/'
]

COMMON_HOSTNAMES: list[str] = [
    'www', 'ftp', 'vnc', 'fw', 'mail', 'dba', 'db', 'mssql', 'sql', 'ib', 'secure', 'oracle',
    'ora', 'oraweb', 'sybase', 'gw', 'log', 'logs', 'logserver', 'backup', 'windows', 'win',
    'nt', 'ntserver', 'win2k', 'mswin', 'msnt', 'posnt', 'server', 'test', 'firewall', 'cp',
    'cpfw1', 'cpfw1ng', 'fw', 'fw1', 'raptor', 'drag', 'dragon', 'pix', 'ciscopix',
    'nameserver', 'dns', 'ns', 'ns1', 'ns2', 'mx', 'webmail', 'mailhost', 'smtp', 'owa',
    'pop', 'notes', 'proxy', 'squid', 'imap', 'www1', 'www2', 'www3', 'corp', 'corpmail',
    'print', 'printer', 'search', 'telnet', 'tftp', 'web', 'bgp', 'citrix', 'pcanywhere',
    'ts', 'terminalserver', 'tserv', 'tserver', 'keyserver', 'pgp', 'samba', 'linux', 'redhat',
    'caldera', 'openlinux', 'conectiva', 'corel', 'corelinux', 'debian', 'mandrake',
    'linuxppc', 'bastille', 'stampede', 'suse', 'trinux', 'trustix', 'turbolinux', 'turbo',
    'tux', 'slack', 'slackware', 'bsd', 'daemon', 'darby', 'beasty', 'beastie', 'openbsd',
    'netbsd', 'freebsd', 'obsd', 'fbsd', 'nbsd', 'solaris', 'sun', 'sun1', 'sun2', 'sun3',
    'aix', 'tru64', 'hp-ux', 'hp', 'lynx', 'lynxos', 'macosx', 'osx', 'minix', 'next',
    'nextstep', 'qnx', 'rt', 'sco', 'xenix', 'sunos', 'ultrix', 'unixware', 'multics',
    'zeus', 'apollo', 'hercules', 'venus', 'pendragon', 'guinnevere', 'lancellot',
    'percival', 'prometheus', 'ssh', 'time', 'nicname', 'tacacs', 'domain', 'whois',
    'bootps', 'bootpc', 'gopher', 'http', 'kerberos', 'hostname', 'pop2', 'pop3', 'nntp',
    'ntp', 'irc', 'imap3', 'ldap', 'https', 'nntps', 'ldaps', 'webster', 'imaps', 'ircs',
    'pop3s', 'login', 'router', 'netnews', 'ica', 'radius', 'hsrp', 'mysql', 'amanda',
    'pgpkeyserver', 'quake', 'kerberos_master', 'passwd_server', 'smtps', 'swat', 'support',
    'afbackup', 'postgres', 'fax', 'hylafax', 'tircproxy', 'webcache', 'tproxy', 'jetdirect',
    'kamanda', 'fido', 'old'
]

GTLD_DOMAINS: list[str] = [
    'biz', 'info', 'net', 'com', 'org', 'edu', 'gov', 'me', 'tv', 'name'
]

TLD_DOMAINS: list[str] = [
    'edu', 'gov', 'mil', 'net', 'org', 'ag', 'co', 'go'
]

CC_DOMAINS: set[str] = {
    '.ac', '.ad', '.ae', '.aero', '.af', '.ag', '.ai', '.al', '.am', '.an', '.ao', '.aq',
    '.ar', '.arpa', '.as', '.asia', '.at', '.au', '.aw', '.ax', '.az', '.ba', '.bb', '.bd',
    '.be', '.bf', '.bg', '.bh', '.bi', '.biz', '.bj', '.bl', '.bm', '.bn', '.bo', '.bq',
    '.br', '.bs', '.bt', '.bv', '.bw', '.by', '.bz', '.ca', '.cat', '.cc', '.cd', '.cf',
    '.cg', '.ch', '.ci', '.ck', '.cl', '.cm', '.cn', '.co', '.com', '.coop', '.cr', '.cu',
    '.cv', '.cw', '.cx', '.cy', '.cz', '.de', '.dj', '.dk', '.dm', '.do', '.dz', '.ec',
    '.edu', '.ee', '.eg', '.eh', '.er', '.es', '.et', '.eu', '.fe', '.fi', '.fj', '.fk',
    '.fm', '.fo', '.fr', '.ga', '.gb', '.gd', '.ge', '.gf', '.gg', '.gh', '.gi', '.gl',
    '.gm', '.gn', '.gp', '.gq', '.gr', '.gs', '.gt', '.gu', '.gw', '.gy', '.hk', '.hm',
    '.hn', '.hr', '.ht', '.hu', '.id', '.ie', '.il', '.im', '.in', '.info', '.int', '.io',
    '.iq', '.ir', '.is', '.it', '.je', '.jm', '.jo', '.jobs', '.jp', '.ke', '.kg', '.kh',
    '.ki', '.km', '.kn', '.kp', '.kr', '.kw', '.ky', '.kz', '.la', '.lb', '.lc', '.li',
    '.lk', '.lr', '.ls', '.lt', '.lu', '.lv', '.ly', '.ma', '.mc', '.md', '.me', '.mf',
    '.mg', '.mh', '.mil', '.mk', '.ml', '.mm', '.mn', '.mo', '.mobi', '.mp', '.mq', '.mr',
    '.ms', '.mt', '.mu', '.museum', '.mv', '.mw', '.mx', '.my', '.mz', '.na/name', '.nc',
    '.ne', '.net', '.nf', '.ng', '.ni', '.nl', '.no', '.np', '.nr', '.nu', '.nz', '.om',
    '.org', '.pa', '.pe', '.pf', '.pg', '.ph', '.pk', '.pl', '.pm', '.pn', '.pr', '.pro',
    '.ps', '.pt', '.pw', '.py', '.qa', '.re', '.ro', '.rs', '.ru', '.rw', '.sa', '.sb',
    '.sc', '.sd', '.se', '.sg', '.sh', '.si', '.sj', '.sk', '.sl', '.sm', '.sn', '.so',
    '.sr', '.st', '.su', '.sv', '.sx', '.sy', '.sz', '.tc', '.td', '.tel', '.tf', '.tg',
    '.th', '.tj', '.tk', '.tl', '.tm', '.tn', '.to', '.tp', '.tr', '.travel', '.tt',
    '.tv', '.tw', '.tz', '.ua', '.ug', '.uk', '.um', '.us', '.uy', '.uz', '.va', '.vc',
    '.ve', '.vg', '.vi', '.vn', '.vu', '.wf', '.ws', '.ye', '.yt', '.za', '.zm', '.zw'
}

DEFAULT_NMAP_SCANTYPE: str = "-O --reason --webxml --traceroute -sS -sV -sC -Pn -n -v -F"
ZENMAP_COMMAND: str = "zenmap"
DEFAULT_MAX_CRAWL: int = 50
SOCKET_TIMEOUT: int = 10
