import requests
from datetime import datetime, timedelta
import os.path
import json
from bs4 import BeautifulSoup
import re
import urllib.parse
from cryptography.fernet import Fernet

# TODO: Adjust functions to use MorawareSession.session as a common requests session, rather than creating new sessions for each request. This will allow for better session management and less overhead. Although this can cause issues with multithreading, so will need to be tested.
# Can be done by optionally passing the session to the functions, and using it in the requests.get/post calls.

DEFAULTMORAWARECREDS = {'user': None,
                        'pwd': None}

CLIENT = None



#############################################################################################################################################################################
################################################################################# Functions #################################################################################
#############################################################################################################################################################################

############################################################################## General Functions ############################################################################

def Give_Key():
    '''
    Generates a key for use in encrypting and decrypting strings.
    '''
    return Fernet.generate_key()

def encrypt_string(string, key):
    '''
    Encrypts a string using a key.
    Args:
        string (str): The string to encrypt.
        key (str): The key to use for encryption.
    Returns:
        str: The encrypted string.
    '''
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(string.encode()).decode()

def decrypt_string(string, key):
    '''
    Decrypts a string using a key.
    Args:
        string (str): The string to decrypt.
        key (str): The key to use for decryption.
    Returns:
        str: The decrypted string.
    '''
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(string.encode()).decode()

def convert_date(input_string, desired_format):
    if not input_string: return input_string
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            dt = datetime.strptime(input_string, fmt)
            return dt.strftime(desired_format)
        except: pass
    print('Date Conversion Failed')
    return input_string

def Give_24hrTime(time):
    if not time: return time
    try:
        return datetime.strptime(time, '%I:%M%p').strftime('%H:%M')
    except:
        print('Time Conversion Failed')
        return time
    
def Encode_Dict_to_String(dict_to_encode):
    '''
    Encode a dictionary to a string for use in Moraware updates.
    Gives the P0 field for creating a job from a quote.
    '''
    encoded_items = [f'"{k}":{v}' if isinstance(v, int) else f'"{k}":"{v}"' for k, v in dict_to_encode.items()]
    return '{' + ','.join(encoded_items) + '}'



############################################################################### Moraware Classes ###############################################################################

class LoggingSession(requests.Session):
    def __init__(self, manager):
        super().__init__()
        self.last_request_time = None
        self.manager = manager
    def request(self, *args, **kwargs):
        if kwargs.get('JS_CORE'): kwargs.pop('JS_CORE') #Can implement other ways to handle different JS_CORE values
        else: self.manager.refresh() #Because JS_Core app is inteded to manage it's own session refreshes.
        self.last_request_time = self.manager.active = datetime.now()
        response = super().request(*args, **kwargs)
        return response


class MorawareSession:
    '''
    Create a Moraware login session, or fetch login session data from json file in this directory.
    If no session data is found, or the session data is expired, a new session is created.
    Will be defualt use seed data including credentials and decryption key.
    Otherwise will use entered credetntials and look for a json file with the client name and user name.
    Can quickly and easily be converted to and from json for storage - with the key for encryption.
    
    Attributes:
        session (requests.Session): the session object for the Moraware login.
        mw_cookie (dict): the cookie data for the Moraware login.
        expiry (datetime): the expiry time for the Moraware login.
        sessionheaders (dict): the headers for the Moraware login
        client (str): the client name for the Moraware login.
        user (str): the user name for the Moraware login.
        active (datetime): the last time the session was used.
        
    Methods:
        LoginProcess: logs in to Moraware and updates the session data.
        expired: returns True if the session has expired
        refresh: refreshes the session if it is close to expiry.
        to_json: returns the session data as a json string.
        from_json: creates a MorawareSession object from a json string.

    '''
    loginform = {'action': 'login',
                'LOGIN': 'Sign In',
                }
    name = 'Moraware'
    user = ''
    
    def __init__(self, client=CLIENT, UserCreds={}, Session=None, SeedData=None, key=None, **kwargs):
        if SeedData:
                self.client = SeedData.get('client', CLIENT)
                self.endpoint = f'https://{self.client}.moraware.net/'
                self.user = SeedData.get('user', '')
                self.mw_cookie = SeedData.get('mw_cookie', None) #decrypt
                self.expiry = SeedData.get('expiry', datetime.now())
                self.active = SeedData.get('active', datetime.now())
                self.sessionheaders = SeedData.get('sessionheaders', {})
                pwd = decrypt_string(SeedData.get('pwd', ''), key) if SeedData.get('pwd') else ''
                self.loginform.update( {'user': SeedData.get('user', ''), 'pwd': pwd} )
                
        else:
            self.client = client
            self.endpoint = f'https://{client}.moraware.net/'
            self.loginform.update(UserCreds)
            self.user = UserCreds.get('user', '')
            cookiedat = {}
            if os.path.exists(f'MWS_{client}_{self.user}.json'):
                with open(f'MWS_{client}_{self.user}.json', 'r') as jf: cookiedat = json.load(jf)
        
            self.mw_cookie = cookiedat.get('mw_cookie')
            self.expiry = datetime.fromisoformat(cookiedat.get('expiry', '1900-01-01T00:00:00'))
            self.active = datetime.fromisoformat(cookiedat.get('active', '1900-01-01T00:00:00'))
            self.sessionheaders = cookiedat.get('sessionheaders')
        
        self.session = Session if Session else LoggingSession(self)
        if self.mw_cookie:
            self.session.cookies.update(self.mw_cookie)
            self.session.headers.update(self.sessionheaders)
        
        if not self.mw_cookie or datetime.now() > self.expiry:
            self.LoginProcess()
            
    def LoginProcess(self):
        print('Logging in to Moraware...')
        s = self.session
        s.cookies.clear()
        rsp = s.post(self.endpoint, data=self.loginform, JS_CORE='login')
        #read the response page for successful login
        page = BeautifulSoup(rsp.content, 'html.parser')
        if 'sign in' in page.title.text.lower(): raise Exception('Login Failed')

        self.sessionheaders = dict(s.headers)
        self.expiry = datetime.now() + timedelta(minutes=50)
        self.mw_cookie = s.cookies.get_dict()
        self.active = datetime.now()
        with open(f'MWS_{self.client}_{self.user}.json', 'w') as f:
            json.dump({'mw_cookie': self.mw_cookie,
                       'expiry' : self.expiry.isoformat(),
                       'active' : self.active.isoformat(),
                       'user': self.user,
                       'sessionheaders': self.sessionheaders}, f)
        return self.mw_cookie

    def refresh(self):
        lr = self.session.last_request_time
        if not lr: lr = self.active
        if datetime.now() - lr > timedelta(minutes=55):
            self.LoginProcess()
            #return (True, 'Initialised')
            return {'active': self.active, 'status': 'Initialised'}
        elif datetime.now() - lr > timedelta(minutes=45):
            self.session.get(self.endpoint, JS_CORE='refresh')
            self.expiry = datetime.now() + timedelta(minutes=55)
            return {'active': self.active, 'status': 'Refreshed'}
        return {'active': self.active, 'status': 'Active'}
            
    def expired(self):
        lr = self.session.last_request_time
        if not lr: lr = self.active
        if datetime.now() - lr > timedelta(minutes=55):
            return True
    
    def __str__(self):
        return f'Moraware Session: {self.client}/{self.user}/{self.mw_cookie}'
    
    def to_json(self, key=None):
        return json.dumps({'mw_cookie': self.mw_cookie,
                           'expiry' : self.expiry.isoformat(),
                           'active' : self.active.isoformat(),
                           'sessionheaders': self.sessionheaders,
                           'client': self.client,
                           'user': self.user,
                           'pwd': encrypt_string(self.loginform['pwd'], key) if key else ''})
                           
    
    @classmethod
    def from_json(cls, jsondata, key=None):
        data = json.loads(jsondata)
        if data.get('expiry'):
            data['expiry'] = datetime.fromisoformat(data['expiry'])
        if data.get('active'):
            data['active'] = datetime.fromisoformat(data['active'])
        return cls(SeedData=data, key=key)


class MorawareConnection:
    '''
    Class for managing client Moraware data.
    This class stores IDs for various Moraware data, and fetches them if they are not present in the data dictionary, and updates the data dictionary.
    Intended primarily for managing the data dictionary for a single client, and providing that data to other classes.
    Can be converted to and from json for storage.
    Can create a Moraware Session object inside itself to manage the login.

    Attributes:
        session (MorawareSession): the session object for the Moraware login.
        client (str): the client name for the Moraware login.
        Data (dict): the data dictionary for the client.

    Methods:
        data_check: checks if a key is in the data dictionary.
        data_update: updates the data dictionary with a key and value.
        data_check_update: checks if a key is in the data dictionary, and if not, fetches the data and updates the dictionary.
        to_json: returns the session data as a json string.
        from_json: creates a MorawareConnection object from a json string.
        check_refresh_session: checks if the session is expired, and refreshes it if necessary.
        GetQuote: fetches a Moraware Quote object.
        
    '''
    def __init__(self, Session=None, **kwargs):
        if Session:
            self.session = Session
            client = Session.client
        else:
            client = kwargs.get('client', CLIENT)
            self.session = MorawareSession(**kwargs)
        self.client = client

        self.Data = {}
        if os.path.exists(f'{client}_MCD.json'):
            with open(f'{client}_MCD.json', 'r') as f:
                self.Data = json.load(f)
        if 'data' in kwargs:
            self.Data.update(kwargs['data'])
            with open(f'{client}_MCD.json', 'w') as f:
                json.dump(self.Data, f)

        self.new_job_script = kwargs.get('new_job_script')
        self.job_forms = kwargs.get('job_forms')

        if kwargs.get('checkauth'): self._checkauth()
        else: self.check_refresh_session()

    def __str__(self):
        return f'Moraware Connection: {self.client} - {self.session}'
    
    def _checkauth(self):
        self.check_refresh_session(force=True)
        url = f"https://{self.client}.moraware.net/sys/report/?&dt=1&ts=3&rptDate={datetime.now().strftime('%Y-%m-%d')}&measures=2:qli11:q3&dimensions=^2:qli11:q3&pageSize=30&sort=a1"
        rtn = self.GetView(url)
        if not rtn: raise Exception('Not Authorised')
    
    def CheckAuth(self):
        try:
            self._checkauth()
            return True
        except:
            return False
        
    def check_refresh_session(self, force=None):
        if self.session.expired() or force:
            self.session.LoginProcess()
        
    @property
    def mw_cookie(self):
        return self.session.mw_cookie

    def data_check(self, key):
        if key not in self.Data:
            return False
        return True
    
    def data_update(self, key, value):
        self.Data[key] = value
        with open(f'{self.client}_MCD.json', 'w') as f:
            json.dump(self.Data, f)

    def data_check_update(self, key, force=False):
        func = {'StatusIDs': GetActivityStatusIDs,
                'ActivityIDs': GetActivityIDs,
                'ProductIDs': GetALLInventoryIDs,
                'form': GetFormFields,
                'LocationIDs': GetInventoryLocations,
                'InventoryCustomFields': GetInventoryCustomFields,
                }
        if not self.Data.get(key) or force:
            keyname = key.split('_')[0] if '_' in key else key
            args = {'mw_cookie': self.mw_cookie, 'client': self.client, 'data_key_name': key}
            if keyname in func: self.data_update(key, func[keyname](**args))
            else: raise Exception(f'Key {keyname} not found in data dictionary, and no function to fetch it.')

    def Give(self, key, force_update=False):
        self.data_check_update(key=key, force=force_update)
        return self.Data[key]

    def to_json(self, key=None):
        return json.dumps({'client': self.client,
                           'data': self.Data,
                           'session': self.session.to_json(key)})
    
    @classmethod
    def from_json(cls, jsondata, key=None):
        data = json.loads(jsondata)
        return cls(Session=MorawareSession.from_json(data['session'], key), **data)
            
    def GetQuote(self, QuoteID):
        self.check_refresh_session()
        return MorawareQuote(self, QuoteID)
    
    def GetView(self, url, headers=None, IDCol_Index=[0], TableType=None):
        self.check_refresh_session()
        return Fetch_View(url, self.mw_cookie, headers, IDCol_Index, TableType)
    
    def GetJob(self, JobID):
        self.check_refresh_session()
        return MorawareJob(self, JobID, forms=self.job_forms)
    
    def GetInventory(self, ProductID):
        self.check_refresh_session()
        return MorawareInventory(self, ProductID)
    

    

class MorawareQuote:
    '''
    A Moraware Quote Object.
    '''
    def __init__(self, mw_Connect, QuoteID):
        self.QuoteID = QuoteID
        self.QuoteData = GetQuoteDetails(mw_Connect.mw_cookie, QuoteID, mw_Connect.client)
        self.mw_Connect = mw_Connect
        if hasattr(mw_Connect, 'new_job_script'):
            self.new_job_script = mw_Connect.new_job_script
        
    def CreateJob(self, JobName, NewJobScript=None, **kwargs):
        '''
        Create a Job from the Quote (conduct normal new-job procedures).
        Send back signal to MorawareConnection object to check to required resources, and call fetching of those resources if necessary.
        '''
        create_job_args = {
            'mw_cookie': self.mw_Connect.mw_cookie,
            'JobName': JobName,
            'QuoteID': self.QuoteID,
            'QuoteData': self.QuoteData,
            'client': self.mw_Connect.client
        }
        if 'templateid' in kwargs:
            create_job_args['templateid'] = kwargs['templateid']
        if 'processid' in kwargs:
            create_job_args['processid'] = kwargs['processid']

        self.QuoteData = CreateJobFromQuote(**create_job_args)

        # self.QuoteData = CreateJobFromQuote(mw_cookie=self.mw_Connect.mw_cookie,
        #                                     JobName=JobName,
        #                                     QuoteID=self.QuoteID,
        #                                     QuoteData=self.QuoteData,
        #                                     client=self.mw_Connect.client)
        job = MorawareJob(self.mw_Connect, self.QuoteData['Job ID'])
        if NewJobScript: NewJobScript(job, self)
        elif hasattr(self, 'new_job_script'): self.new_job_script(job, self)
        return job
    
    
class MorawareJob:
    '''
    A Moraware Job object
    Pass 'TRUE' into forms init to fetch first found form.

    Attributes:
        JobID (str): The Job ID.
        mw_Connect (MorawareConnection): The Moraware Connection object.
        JobData (dict): The Job Data dictionary.

    Methods:
        UpdateActivity: Update an activity in the job.
        UpdateJobForm: Update a Job Form on the job.
        CreateActivity: Create an activity in the job.
        AllocateMaterial: Allocate material to the job.
    '''
    def __init__(self, mw_Connect, JobID, forms=[{'name': 'JobCard', 'identifier': 'CUSTOMER AND SITE DETAILS', 'type_id': 'form_8'}]):
        self.JobID = JobID
        self.mw_Connect = mw_Connect
        self.JobData = GetJobDetails(mw_Connect=mw_Connect,
                                     SN=JobID,
                                     forms=forms)
        
    def UpdateActivity(self, ActivityType, Updates):
        '''
        Update an activity in the job.
        '''
        return UpdateJobActivity(MWJob=self,
                                 jid=self.JobID,
                                 Activity=ActivityType,
                                 Updates=Updates)
    
    def UpdateJobForm(self, formid, fields, form_type_id='form_8'):
        '''
        Update a Job Form on the job.

        Args:
            formid (str): The ID of the form to update.
            fields (dict): The fields to update.
            form_type_id (str): The type ID of the form.

        Returns:
            UpdateJobForm: The update form object.
        '''
        return UpdateJobForm(mw_Connect=self.mw_Connect,
                             JobID=self.JobID,
                             FormID=formid,
                             form_type_id=form_type_id,
                             Updates=fields)

    
    def CreateActivity(self, **Updates):
        '''
        Create an activity in the job.
        '''
        return CreateJobActivity(mw_Connect=self.mw_Connect,
                                 JobID=self.JobID,
                                 **Updates)
    
    def AllocateMaterial(self, ActivityID, MaterialData):
        '''
        Allocate material to the job.
        '''
        return AllocateMaterial(mw_cookie=self.mw_Connect.mw_cookie,
                                JobID=self.JobID,
                                ActivityID=ActivityID,
                                MaterialData=MaterialData,
                                client=self.mw_Connect.client)
    
    def CreateForm(self, form_type_id, FormName='', Updates={}):
        '''
        Create a form on the job.
        '''
        return CreateJobForm(mw_Connect=self.mw_Connect,
                             JobID=self.JobID,
                             form_type_id=form_type_id,
                             FormName=FormName,
                             Updates=Updates)
    
    @property
    def JobCard(self): # Shortcut to get the first form on a job (especially useful for new jobs).
        return self.JobData['Forms'][0]
    
    def Forms(self, form_name):
        '''
        Returns the forms on the job with the given name.
        '''
        return [form for form in self.JobData['Forms'] if form['form_type_name'] == form_name]


class MorawareInventory:
    '''
    A Moraware Inventory object.
    '''
    def __init__(self, mw_Connect, snid):
        self.snid = snid
        self.mw_Connect = mw_Connect
        self.ProductData, self.transactions = GetInvData(mw_cookie=mw_Connect.mw_cookie, 
                                                         snid=snid,
                                                         client=mw_Connect.client)
        
    def UpdateInventory(self, Updates):
        '''
        Update the inventory item.
        '''
        return UpdateInventory( mw_inventory=self,
                                fields=Updates)



############################################################################### Moraware Update Function ###############################################################################

def UpdateMoraware(mw_cookie, Serial, FormType='Job_UpdateJobActivities', endpoint='job', fields={}, client=CLIENT):
    '''
    Publishes an update form to Moraware.
    Update form is populated with the fields dictionary.
    fields are urlencoded and formatted to match the Moraware form.
    Example:
        P0 : '[str_or_int]'
        
    Args:
        mw_cookie: Login cookie for Moraware.
        Serial: Serial number of the object to update (job, inventory, quote etc).
        FormType: Type of form to update. This will also set the category for the update.
        endpoint: Endpoint for the update.
        fields: Dictionary containing the fields to update.
        
    Returns:
        response: Response from the Moraware server.
    '''
    payload = {
        'C': 'mjtrs1',
        'X': 1,
        'cuid': 24,
        'F': FormType}
    for key, value in fields.items():
        if isinstance(value, str): fields[key] = f'[{urllib.parse.quote(value)}]'
        else: fields[key] = f'[{value}]'
    payload.update(fields)
    ts = int(datetime.now().timestamp() * 1000000)
    response = requests.post(f'https://{client}.moraware.net/sys/{endpoint}/{Serial}', params={'U': ts}, data=payload, cookies=mw_cookie)
    print(response.content)
    if 'MW_RS_ErrorResponse' in response.text: raise Exception(f'Error updating Moraware: {response.text}')
    return response
    


######################################################################### Moraware Connection Data Fetch Functions ######################################################################

def GetActivityStatusIDs(mw_cookie, client=CLIENT, **kwargs):
    '''
    Fetches the activity status IDs from Moraware.
    '''
    url = f'https://{client}.moraware.net/sys/settings/jobactivitystatuses/'
    Activities = {}
    Statuss = requests.get(url, cookies=mw_cookie)
    soup = BeautifulSoup(Statuss.content, 'html.parser')
    table = soup.find('table', {'id': 'ActivityStatusesBody'})
    rows = table.find_all('tr')
    for i,row in enumerate(rows):
        if i == 0: continue
        td_elements = row.find_all('td')
        if td_elements:
            mjtclick_attr = td_elements[0].get('mjtclick', '')
            start = mjtclick_attr.find(',') + 1
            end = mjtclick_attr.find(')', start)
            ActID = mjtclick_attr[start:end].strip()
            ActName = td_elements[0].text.strip()
            Activities[ActName] = ActID
    return Activities

def GetActivityIDs(mw_cookie, client=CLIENT, **kwargs):
    '''
    Fetches the activity Type IDs from Moraware.
    '''
    url = f'https://{client}.moraware.net/sys/settings/jobactivitytypes/'
    Activities = {}
    acts = requests.get(url, cookies=mw_cookie)
    soup = BeautifulSoup(acts.content, 'html.parser')
    table = soup.find('table', {'id': 'ActivityTypesBody'})
    rows = table.find_all('tr')
    for row in rows:
        #if the row isn't of class oddRow or evenRow, then ignore it.
        if not row.get('class') or row.get('class')[0] not in ('oddRow', 'evenRow'): continue
        Act_element = row.find_all('td')[0]
        ActID = Act_element['mjtclick'].split(',')[1].strip()
        ActName = Act_element.text.strip()
        Activities[ActName] = ActID
    return Activities  

def Get_InvProductNamesID(mw_cookie, client=CLIENT):
    '''
    Fetches the inventory product IDs from Moraware.
    '''
    url = f'https://{client}.moraware.net/sys/settings/purchaseproducts/'
    inv = requests.get(url, cookies=mw_cookie)
    soup = BeautifulSoup(inv.content, 'html.parser')
    table = soup.find('table', {'id': 'ProductsBody'})
    rows = table.find_all('tr')
    headers = [hd.text.encode('ascii', 'ignore').decode() for hd in rows[0].find_all('td')]
    for q, header in enumerate(headers):
        if 'attribute' in header.lower():
            AttrHeaders = [f'{header} - {i+1}' for i in range(len(rows[1].find_all('td')))]
            break
    headers = headers[:q] + AttrHeaders + headers[q+1:] + ['Product ID']
    prod_data = []
    for row in rows[2:]:
        cells = row.find_all('td')
        if not cells: continue
        line = {headers[i]: cell.text for i, cell in enumerate(cells)}
        prod_page = row.find('a')['href']
        Prod_ID = prod_page.split('/')[-1]
        line['Product ID'] = Prod_ID
        line['url'] = f'https://{client}.moraware.net{prod_page}'
        prod_data.append(line)
    return prod_data

def Get_InvProductAttrListIDs(mw_cookie, ProductID, client=CLIENT):
    '''
    Fetches the inventory product attribute list IDs from Moraware.
    '''
    url = f'https://{client}.moraware.net/sys/settings/purchaseproduct/{ProductID}/'
    AttrList = {}
    inv = requests.get(url, cookies=mw_cookie)
    soup = BeautifulSoup(inv.content, 'html.parser')
    table = soup.find('table', {'id': 'attrScrollBody'})
    if not table: return {}
    rows = table.find_all('tr')
    for row in rows:
        if not row.find('a'): continue
        AttrListID = row.find('a')['href'].split('/')[-1]
        AttrName = row.find('a').text
        AttrList[AttrName] = AttrListID
    return AttrList

def Get_InvProductAttrIDs(mw_cookie, attrListID, client=CLIENT):
    '''
    Fetches the inventory product attribute IDs from Moraware.
    '''
    attributes = []
    i = 1
    PrevTopRow = None
    while True:
        url = f'https://{client}.moraware.net/sys/settings/purchaseproductattr/{attrListID}?&avtpage={i}'
        Products = requests.get(url, cookies=mw_cookie)
        soup = BeautifulSoup(Products.content, 'html.parser')
        table = soup.find('table', {'id': 'avtScrollBody'})
        if not table: break
        table_rows = table.find_all('tr')[1:]
        if PrevTopRow == table_rows[0]: break
        PrevTopRow = table_rows[0]
        for row in table_rows:
            attrElement = row.find(class_='linkedCell')
            if not attrElement: continue
            attrID = attrElement['mjtclick'].split(',')[1].strip(')')
            attrName = attrElement.text
            attributes.append({'ID': attrID, 'Name': attrName})
        i += 1
    return attributes
    
def Get_InventoryID_Data(mw_cookie, ProductID, client=CLIENT):
    '''
    Fetches Inventory Attribute Data from Moraware for a particular product.
    '''
    ProductAttributes = Get_InvProductAttrListIDs(mw_cookie, ProductID, client)
    for attrList, attrlist_id in ProductAttributes.items():
        ProductAttributes[attrList] = Get_InvProductAttrIDs(mw_cookie, attrlist_id, mw_cookie, client)
    return ProductAttributes

def GetALLInventoryIDs(mw_cookie, client=CLIENT, **kwargs):
    '''
    Fetches all inventory data from Moraware.
    '''
    result = {}
    products = Get_InvProductNamesID(mw_cookie, client)
    print(f'Found {len(products)} products')
    for i,product in enumerate(products):
        print(f'Fetching {i+1} of {len(products)}')
        namekey = f"{product['Product Family']}{product['Product Line']}{product['Product']}"
        result[namekey] = product
        result[namekey]['_ATTR'] = Get_InventoryID_Data(mw_cookie, product['Product ID'], client)
    return result

def GetFormFields(mw_cookie, client=CLIENT, formID='form_8', **kwargs):
    '''
    Returns the field names and IDs for a form in Moraware.

    Args:
        mw_cookie (str): The Moraware cookie.
        formID (str): The ID of the form.
        client (str): The Moraware client.

    Returns:
        dict: A dictionary of field names and IDs.
    '''
    if 'data_key_name' in kwargs: formID = kwargs['data_key_name']
    if '_' in formID: formID = formID.split('_')[-1]
    url = f"https://{client}.moraware.net/sys/settings/formtemplate/{formID}"
    FormBuild = requests.get(url, cookies=mw_cookie)
    soup = BeautifulSoup(FormBuild.content, 'html.parser')
    field_elements = soup.find_all("td", attrs={"mjtclick": True}, recursive=True)
    fields = {}
    fieldslist = []
    for td in field_elements:
        mjtclick_attr = td["mjtclick"]
        if 'formFieldId' in mjtclick_attr:
            idf = mjtclick_attr.split('formFieldId":')[1].split(',')[0]
            field_name_div = td.find("div")
            if field_name_div: field_name = field_name_div.get_text(strip=True)
            else: field_name = td.get_text(strip=True)
            field_name = field_name.strip(':')
            if not fields.get(field_name): # Saves and overwrites until there's an ID.
                fields.update({field_name: idf})
            fieldslist.append((field_name, idf))
    return fields

def GetInventoryLocations(mw_cookie, client=CLIENT, **kwargs):
    locations = []
    i = 1
    PrevTopRow = None
    while True:
        url = f'https://{client}.moraware.net/sys/settings/inventorylocations/?&inventoryLocationssort=a0&inventoryLocationspage={i}'
        response = requests.get(url, cookies=mw_cookie)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'InventoryLocationsBody'})
        if not table: break
        rows = table.find_all('tr')[1:]  # Skip the header row
        if PrevTopRow == rows[0]: break
        PrevTopRow = rows[0]
        for row in rows:
            name_cell = row.find('td', {'class': 'linkedCell'})
            if not name_cell: continue
            name = name_cell.text.strip()
            loc_id = name_cell['mjtclick'].split(',')[1].strip(')').strip("'")
            status_cell = row.find_all('td')[1]
            status = status_cell.text.strip()
            locations.append({'name': name, 'id': loc_id, 'status': status})
        i += 1
    return locations

def GetInventoryCustomFields(mw_cookie, client=CLIENT, **kwargs):
    UserFields = []
    url = f'https://{client}.moraware.net/sys/settings/snfields/'
    response = requests.get(url, cookies=mw_cookie)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'SNAttributesBody'})
    if not table: return UserFields
    rows = table.find_all('tr')
    headers = [header.text.split('\xa0')[0].strip() for header in rows[0].find_all('td')]
    for row in rows[1:]:
        cells = row.find_all('td')
        if not cells: continue
        userfielddata = {headers[i]: cells[i].text.strip() for i in range(len(cells))}
        userfielddata['ID'] = cells[0]['mjtclick'].split(',')[1].strip(')').strip("'")
        UserFields.append(userfielddata)
    return UserFields



########################################################################### Report and View Fetch Functions ###########################################################################

def Fetch_View(url, mw_cookie, headers=None, IDCol_Index=[0], TableType=None):
    '''
    Fetches a Moraware page and returns it as a list of dictionaries.

    TODO:
        Complete the type checking for the function.
        Switch to using MorawareSession.session for the requests. Pros: Better session management, less overhead. Cons: Multithreading issues.

    Args:
        url (str): The url of the Moraware page to fetch.
        LoginSession (MorawareSession): The login session to use for fetching the page. DEPRECATED
        mw_cookie (dict): The cookie data for the Moraware login.
        headers (list): The headers for the table.
        IDCol_Index (list): The indexes of columns to fetch IDs for.
        TableType (str): The type of table to fetch.

    Returns:
        list: A list of dictionaries containing the data from the table.
    '''
    if not headers: print('WARNING: Headers not provided for MWFetch. Parsing headers from the page.')
    views_dict = {'quotes'      : 'Quotes',
                'report'        : 'Report',
                'jobs'          : 'Jobs',
                'pos'           : 'POs',
                'inventory'     : 'Products',
                'settings'      : None,
                'accounts'      : 'Customers',
                'jobactivitytypes': 'ActivityTypes',
                'jobactivitystatuses': 'ActivityStatuses',
                'assignees'     : 'Assignees',
                'jobfields'     : 'JobAttributes',
                'jobissuecategories': 'IssueCategories'}
    if not TableType:
        view_type = url.split('sys/')[1].split('/')[0].split('?')[0]
        if view_type == 'settings':
            view_type = url.split('settings/')[1].split('/')[0].split('?')[0]
        if view_type not in views_dict: raise Exception('View Type Not Found')
        TableType = views_dict[view_type]

    rsp = requests.get(url, cookies=mw_cookie) #### s.get(url)
    soup = BeautifulSoup(rsp.content, 'html.parser')
    #Check if the login page is in the response.<title>Moraware Sign in - Moraware Systemize</title>
    if 'sign in' in soup.title.text.lower(): raise Exception('Login Failed')
    if "No Data Available. Press the 'Customize..' button above to change the report parameters." in rsp.text: return []
    if "You are not authorized to view this page" in rsp.text: raise Exception('Not Authorized')
    table = soup.find( 'table', {'id': f'{TableType}Body'} )
    rows = table.find_all('tr')
    if not headers: headers = [th.text.split('\xa0')[0].strip() for th in rows[0].find_all('td')]
    data = []
    for row in rows[1:]:
        cells = row.find_all('td')
        datarow = {headers[i]: td.text.strip() for i, td in enumerate(cells)}
        for i in IDCol_Index:
            #i = idc - 1
            if i > len(cells): continue
            hd = headers[i]
            try: datarow[f'{hd} ID'] = cells[i].find('a').get('href').split('/')[-1]
            except: datarow[f'{hd} ID'] = 'ID Not Found'
        data.append(datarow)
    return data

def Fetch_Report(url, mw_cookie, headers=None, IDCol_Index=[0]):
    return Fetch_View(url, mw_cookie, headers, IDCol_Index, 'Report')

def FetchNewQuotes(mw_cookie, client=CLIENT):
    url = f'https://{client}.moraware.net/sys/quotes?&view=0&sort=d3&cols=QN1,QA39,CN1,QN2,QN7,QN8,QN4,QN5,QN6,QA15&pageSize=9000&filters=2|3:0:j3:9:j3;1,1,2,,,!5|11:0:q3:9:q3;4,1,3,365,,'
    return Fetch_View(url, mw_cookie)



################################################################################## Soup Kitchen ###############################################################################

def GetSomeSoup(mw_cookie, jid, client=CLIENT, endpoint='job'):
    joburl = f'https://{client}.moraware.net/sys/{endpoint}/{jid}'
    job = requests.get(joburl, cookies=mw_cookie)
    soup = BeautifulSoup(job.content, 'html.parser')
    return soup



############################################################################### Quote Fetch Functions ###############################################################################

def GetQuoteDetails(mw_cookie, SN, client=CLIENT):
    url = f'https://{client}.moraware.net/sys/quote/{SN}'
    QuoteDetails = requests.get(url, cookies=mw_cookie)
    soup = BeautifulSoup(QuoteDetails.content, 'html.parser')
    main_table = soup.find('table', {'class': 'pageInfoCenteredJustifiedTable'})
    rows = main_table.find_all('tr')
    QuoteMainData = {'_QuoteID': SN}
    for row in rows:
        cols = row.find_all('td')
        colsb = ['\n'.join([st for st in ele.stripped_strings]) for ele in cols]
        QuoteMainData[colsb[0].strip(':')] = colsb[1]

    quotelines_table = soup.find('table', {'class': 'quoteLinesTable'})
    rows = quotelines_table.find_all('tr')
    QuoteLines = []
    for row in rows:
        cols = row.find_all('td')
        rowdata = []
        for ele in cols:
            el = ele.text.strip().replace('\uf111','').replace('×', 'x')
            if el: rowdata.append(el)
        QuoteLines.append(rowdata)

    QuoteLineData = []
    for i,line in enumerate(QuoteLines):
        if not line: continue
        try:
            if i==0: QuoteLineData.append( ['Quoted', ''.join(line)] )
            elif 'Measurement' in line[0].title():
                Pieces = []
                QuoteLineData.append( ['Measurements', ''.join(line).replace('\xa0', ' ')] )
                for piece in line[0].split(','):
                    piece = piece.replace('Measurement\xa0- ', '').strip()
                    if 'Sq Mtr' in piece:
                        piece = piece.split('[')[0].strip()
                    if piece: Pieces.append(piece)
                if Pieces: QuoteLineData.append(['Pieces', Pieces])
            elif 'Benchtop' in line[0].title():
                #Get the squaremetre from the next line, eg: '[Qty: 1.0000] [3.5153 Sq Mtr] [$0/Sq Mtr]'
                sqm = QuoteLines[i+1][0].split('[')[2].split(']')[0].split(' ')[0]
                QuoteLineData.append(['Material', line[0], sqm])
            elif 'Includes' in line[0].title():
                #Get the quantity of the item to incliude from next linme, eg: ['[Qty: 1.0000] [$870/Each]']
                qty = QuoteLines[i+1][0].split('[')[1].split(']')[0].split(' ')[1]
                QuoteLineData.append(['Includes', line[0], qty])
            elif 'Edge Finish' in line[0].title():
                #Get the lineal metreage from the following line, eg: ['[Qty: 1.0000] [1500m...5/Lin Mtr]']
                linm = QuoteLines[i+1][0].split('[')[2].split(']')[0].split(' ')[0]
                QuoteLineData.append(['Edge Finish', line[0], linm])
            elif 'Waterjet' in line[0].title():
                QuoteLineData.append(['Waterjet', line[0]])
        except:
            pass
    QuoteMainData['QuoteLines'] = QuoteLineData
    return QuoteMainData



############################################################################### Job Fetch Functions ###############################################################################
   
def GetJobActivities(JobSoup=None, **args):
    if not JobSoup: JobSoup = GetSomeSoup(mw_cookie=args.get('mw_cookie'), jid=args.get('jid'), client=args.get('client'))
    table = JobSoup.find('table', {'id': 'ActivitiesBody'})
    if not table: raise Exception('No Activities Table Found')

    def clean_cell(cell, hd=''):
        cl = [re.sub(r'[^\x00-\x7F]+', '', c) for c in cell.stripped_strings] # Remove non-ASCII characters
        # ^ - not, \x00-\x7F - ASCII characters, + - one or more, '' - replace with nothing
        cleaned_cell = '\n'.join(cl).strip('\n').strip()
        if not cleaned_cell: return cleaned_cell # Could return None or an empty string
        elif cleaned_cell == 'Add Material': return None
        elif 'date' in hd.lower():
                try: int(cleaned_cell[0]) # Test if the first character is a number (sometimes is a status letter)
                except: return cleaned_cell.split('\n')[1].strip()
        elif 'material' in hd.lower():
            return cleaned_cell.strip('\nAdd Material').strip()
        return cleaned_cell.strip('\n').strip()
    
    rows = table.find_all('tr')
    Activities = []
    for i,row in enumerate(rows): #Getting Activity ID and Materials
        rowdetails = row.find_all('td')
        if i == 0:
            ActivityTableHeaders = [clean_cell(cell) for cell in rowdetails]
            continue
        act_details = {}
        for j,cell in enumerate(rowdetails):
            hd = ActivityTableHeaders[j]
            act_details[hd] = clean_cell(cell, hd)
        act_details.update({
            'ActivityID': row['mjtdrop'].split('\'')[1],
            'Materials': extract_slab_details( rowdetails[ActivityTableHeaders.index('Material')] ),
            'Activity Type': act_details['Activity']
        })
        Activities.append(act_details)
    return Activities

def GetJobCard(JobSoup=None, form_def={}, fetch_all=True, **args):
    # if not form_def: raise Exception('No Form Definition Provided')
    if not JobSoup: JobSoup = GetSomeSoup(mw_cookie=args.get('mw_cookie'), jid=args.get('jid'), client=args.get('client'))
    JobForms = JobSoup.find_all('table', {'class': 'detail-form'})
    form_identifier = form_def.get('identifier', '')
    JobCards = [form for form in JobForms if form_identifier in form.text]
    if not JobCards: return []
    if fetch_all: return [extract_job_card_data(JobCard, form_def) for JobCard in JobCards]
    return extract_job_card_data(JobCards[0], form_def)

def extract_job_card_data(JobCard, form_def):
    formid = JobCard['id'].split('tblJobForm')[-1]
    JobData = {}
    header_divs = JobCard.find_all('div', style=re.compile(r';font-size:10pt;font-weight:bold;')) # Hard coded font size and weight (less flexible)
    for header in header_divs:
        header_text = header.text.strip().strip(':').strip()
        JobData[header_text] = '\n'.join( header.find_next('div').stripped_strings )
    JobData.update({'JobCardID': formid})
    JobData.update({'form_type_id': form_def.get('type_id')})
    JobData.update({'form_type_name': form_def.get('name')})
    return JobData

def extract_slab_details(cell):
    if cell.text.strip('\uf055') == 'Add Material': return []
    Materials = cell.find_all('a')
    slab_details = []
    for material in Materials:
        mt = material.find('div', class_='jobActMaterialCellContent')
        outername = mt.find('span')
        material_type = ''.join([str(content) for content in outername.contents if not content.name])
        serial_number_specs = material.find_all('div', class_='serialNumberSpec')
        for spec in serial_number_specs:
            # Slab Quantity SQM
            square_metre_info = spec.find('span', {'class': 'quantitySpec'}).text
            square_metre_match = re.search(r"(\d+\.\d+)\s*Sq Mtr", square_metre_info)
            quantity = square_metre_match.group(1) if square_metre_match else 0
            # Slab Serial Number
            serial_number = spec.find('span', class_='jobSerialNumber').text.strip()
            # Slab System ID
            if serial_number == '(Unserialized)': system_id = None
            else:
                span_with_onmousedown = spec.find('span', {'onmousedown': True})
                onmousedown_attr = span_with_onmousedown['onmousedown']
                match = re.search(r"JobActivitySerialNumberMouseDown\(event, \d+, \d+, \"(\d+)\"", onmousedown_attr)
                system_id = match.group(1) if match else ''

            slab_details.append({
                'SQM': quantity,
                'ExtSN': serial_number,
                'MorawareInternalID': system_id,
                'material_type': material_type
                })           
    return slab_details

def GetJobDetails(mw_Connect, SN, forms):
    client = mw_Connect.client
    mw_cookie = mw_Connect.mw_cookie
    url = f'https://{client}.moraware.net/sys/job/{SN}'
    JobPage = requests.get(url, cookies=mw_cookie)
    soup = BeautifulSoup(JobPage.content, 'html.parser')

    job_result = {
        'url': url,
        'jid': SN,
        'JobPage': JobPage,
        'soup': soup,
        'JobName': ' - '.join(soup.find('title').text.split(' - ')[:-2]).strip(),
        'Activities': GetJobActivities(soup),
        'Forms': []
        }

    if forms is True:
        job_result['Forms'].append( GetJobCard(soup, fetch_all=False) ) # Fetch the first form found.
    else:
        for form_data in forms:
            job_result['Forms'] += GetJobCard(soup, form_def=form_data) # Fetch all forms defined in the forms
    return job_result



################################################################################ Inventory Functions ###############################################################################

def GetInvData(mw_cookie, snid, client=CLIENT):
    soup = GetSomeSoup(jid=snid, mw_cookie=mw_cookie, client=client, endpoint='serialnumber')
    main_table = soup.find('table', {'class': 'pageInfoCenteredJustifiedTable'})
    if not main_table: raise Exception('No Inventory Data Found')
    rows = main_table.find_all('tr')
    InvMainData = {'_SNID': snid}
    for row in rows:
        cols = row.find_all('td')
        colsb = ['\n'.join([st for st in ele.stripped_strings]) for ele in cols]
        fieldname = colsb[0].strip(':')
        InvMainData[fieldname] = colsb[1]
    transactions_table = soup.find('table', {'id': 'TxnsBody'})
    rows = transactions_table.find_all('tr')
    headers = [ele.text.strip() for ele in rows[0].find_all('td')]
    TxnLines = []
    for row in rows[1:]:
        cols = row.find_all('td')
        TxnData = {}
        for i, ele in enumerate(cols):
            TxnData[headers[i]] = ele.text.strip()
        TxnLines.append(TxnData)
    return InvMainData, TxnLines

def UpdateInventory(mw_inventory, fields):
    mw_Connect = mw_inventory.mw_Connect
    locations_ids = {x['name']: x['id'] for x in mw_Connect.Give('LocationIDs')}
    userfield_ids = {x['Name']: x['ID'] for x in mw_Connect.Give('InventoryCustomFields')}
    p_mapping = {
        'Serial Number': 'P1',
        'Batch Number': 'P2',
        'Description': 'P3',
        'Location_ID': 'P4',
    }
    p_dict = {v: mw_inventory.ProductData.get(k) for k, v in p_mapping.items() if k in mw_inventory.ProductData}
    if mw_inventory.ProductData.get('Location'):
        p_dict[p_mapping['Location_ID']] = locations_ids.get(mw_inventory.ProductData['Location']) or ''
    
    if 'Location' in fields:
        p_dict[p_mapping['Location_ID']] = locations_ids.get(fields['Location']) or ''
    p_dict.update( {v: fields[k] for k, v in p_mapping.items() if k in fields } )

    userfields_update = [( userfield_ids.get(k), str(v).replace('?', '')) for k,v in fields.items() if k in userfield_ids]
    if userfields_update:
        upd = list(zip(*userfields_update))
        p_dict.update({
            'P5': ','.join(upd[0]) + ',',
            'P6': '?'.join(upd[1]) + '?'
        })
    else:
        p_dict['P5'] = ''
        p_dict['P6'] = ''
        
    # p_dict['P0'] = mw_inventory.snid
    p_dict = {'P0': mw_inventory.snid, **p_dict}
    return UpdateMoraware(  mw_cookie=mw_Connect.mw_cookie,
                            Serial=mw_inventory.snid,
                            FormType='Inventory_UpdateSerialNumber',
                            endpoint='serialnumber',
                            fields=p_dict,
                            client=mw_Connect.client )



############################################################################### Job Update Functions ###############################################################################

def UpdateJobActivity(MWJob, jid, Activity, Updates):#, mw_Connect):
    '''
    Initiate a job update in Moraware.
    Uses a MorawareJob object containing all job data and mw_Connect object containing the Moraware connection objects.
    Activity argument should be the activity to be updated.
    Updates argument should be a dictionary containing the updates to be made.
    ie: 'Install', {'Status': 'Completed', 'Start Date': '2021-06-01', 'Assigned To': 'John Doe', 'Notes': 'Completed the install.'}
    Use the MWSession class to get the StatusIDs and Inventory Locations as class variables for every session.
    Start Date should be in the format 'YYYY-MM-DD' (otherwise will assume US format).
    Names of activities and statuses should be exact and match shown in Moraware.
    
    Args:
        MWJob: MorawareJob object containing all job data.
        jid: Job ID
        Activity: Activity to be updated.
        Updates: Dictionary containing the updates to be made.
        
    Returns:
        rsp: Response from the Moraware server.
    '''
    mw_Connect = MWJob.mw_Connect
    StatusIDs = mw_Connect.Give('StatusIDs')
    mw_cookie = mw_Connect.mw_cookie
    client = mw_Connect.client
    JobData = MWJob.JobData['Activities']
    p_mapping = {
        'ActivityID': 'P0',
        'Status': 'P1',
        'Start Date': 'P2',
        'Sched Time': 'P3',
        'Duration': 'P4',
        'Assigned To': 'P5',
        'Notes': 'P6'}
    ActionedActivity = {act['Activity Type']: act for act in JobData}[Activity]
    ActionedActivity.update(Updates)
    MW_Act_Dat = ActionedActivity.copy()
    if MW_Act_Dat['Status'] == 'Auto-Schedule' and 'Start Date' in Updates and 'Status' not in Updates:
        Updates['Status'] = 'Estimate'
    MW_Act_Dat['Status'] = StatusIDs[MW_Act_Dat['Status']]
    MW_Act_Dat['Start Date'] = convert_date(MW_Act_Dat['Start Date'], '%Y-%m-%d')
    MW_Act_Dat['Sched Time'] = Give_24hrTime(MW_Act_Dat['Sched Time'])

    #Creating the update dictionary, updating with existing data.
    UpdateDict = {}
    for i in range(0, 11): UpdateDict[f'P{i}'] = ''
    UpdateDict.update( { p_mapping[k]:v for k,v in MW_Act_Dat.items() if k in p_mapping } )

    #Setting Status update to StatusID, adding the updates to the update dict.
    if 'Status' in Updates: Updates['Status'] = StatusIDs[Updates['Status']]
    UpdateDict.update( { p_mapping[k]:v for k,v in Updates.items() if k in p_mapping } )

    #This tells Moraware which fields are being modified, even if false information is in other fields, it will only update the fields that are flagged as modified.
    UpdateDict['P9'] = '%2C'.join( [ '1' if key in Updates else '0' for key in p_mapping.keys() ] + ['0'] )
    return UpdateMoraware( mw_cookie=mw_cookie,
                            Serial=jid,
                            FormType='Job_UpdateJobActivities',
                            endpoint='job',
                            fields=UpdateDict,
                            client=client
                            )

def CreateJobFromQuote(mw_cookie, JobName, QuoteID, QuoteData, templateid='1', processid=1, client=CLIENT):
    '''
    Create a job from a quote in Moraware.
    Only creates the job, does not update any fields.
    '''
    DecodedString = {'quoteId': QuoteID,
                     'jobName': JobName,
                     'jobTemplateId': str(templateid), # Change this to use different job template.
                     'jobProcessId': int(processid), # Need a flag in the quote for Commercial, Residential, Remakes etc quotes.
                     'salespersonId': '',
                     'useDefaultSalespersonId': 1}
    EncodedString = Encode_Dict_to_String(DecodedString)
    rsp = UpdateMoraware(mw_cookie=mw_cookie,
                         Serial=QuoteID,
                         FormType='Quote2_CreateJobFromQuote2',
                         endpoint='quote',
                         fields={'P0': EncodedString},
                         client=client
                         )
    if 'MW_RS_ErrorResponse' in rsp.text: raise Exception(f'Error creating job from quote: {rsp.text}')
    jid = eval(rsp.text)['jobId']
    QuoteData.update({'Job ID': jid})
    return QuoteData

def AllocateMaterial(mw_cookie, JobID, ActivityID, MaterialData, client=CLIENT):
    '''
    Allocate material to a job.

    Args:
        mw_cookie: Login cookie for Moraware.
        JobID: The Job ID to allocate the material to.
        ActivityID: The Activity ID to allocate the material to.
        MaterialData: Dictionary containing the material data to allocate.
        client: Moraware client name.

    Returns:
        rsp: Response from the Moraware server.
    '''
    MaterialData['ActivityID'] = ActivityID
    if not 'UnserQtyAlloc' in MaterialData: MaterialData['UnserQtyAlloc'] = '0'
    material_alloc_mapping = {
        'ActivityID': 'P0',
        'ProductID': 'P1',
        'AttrID1': 'P2',
        'AttrID2': 'P3',
        'AttrID3': 'P4',
        'AttrID4': 'P5',
        'AttrID5': 'P6',
        'UnserQtyAlloc': 'P7',
        }
    fields = {v:MaterialData.get(k, '') for k,v in material_alloc_mapping.items()}
    fields['P8'] = f'?|{MaterialData["SN_ID"]}|{MaterialData["SN_Display"]}|{MaterialData["SQM_Allocating"]}|Sq%20Mtr|{MaterialData["SQM_OG"]}'
    rsp = UpdateMoraware(mw_cookie=mw_cookie,
                         Serial=JobID,
                         FormType='Job_CreateAndAllocateJobActivityProduct',
                         fields=fields,
                         client=client)
    if 'MW_RS_ErrorResponse' in rsp.text:
        if 'variant id=' in rsp.text:
            pass
    return rsp

def CreateJob(mw_cookie, JobName, AccountID='', TemplateID='1', ProcessID='1', client=CLIENT):
    '''
    Create a job in Moraware.
    '''
    fields = {
        'P0': JobName,
        'P1': AccountID,
        'P2': TemplateID,
        'P3': ProcessID,
        'P4': '',
        'P5': '1'
        }
    rsp = UpdateMoraware(mw_cookie=mw_cookie,
                         Serial=ProcessID,
                         FormType='Job_CreateJob',
                         endpoint='jobs',
                         fields=fields,
                         client=client)
    return rsp

def CreateJobActivity(mw_Connect, JobID, Status='Estimate', **Updates):
    '''
    Create a job activity in Moraware.

    Args:
        mw_Connect: Moraware connection object.
        JobID: The Job ID to create the activity for.
        ActivityType: The Activity Type by Display Name.
        ActivityID: The Activity Type by ID.
        Status: Status of the activity by name (default: Estimate).
        StatusID: Status of the activity by ID (default: Estimate).
        StartDate: Start date of the activity (default: unscheduled).
        ScheduledTime: Scheduled time of the activity (default: unscheduled).
        Duration: Duration of the activity (default: empty).
        Assignee: Activity assigned to by name (default: unassigned).
        Notes: Notes for the activity.

    Returns:
        rsp: Response from the Moraware server.
    '''
    mw_cookie = mw_Connect.mw_cookie
    client = mw_Connect.client
    StatusIDs = mw_Connect.Give('StatusIDs')
    ActivityIDs = mw_Connect.Give('ActivityIDs')
    Updates['JobID'] = JobID
    if not 'StatusID' in Updates: Updates['StatusID'] = StatusIDs[Status]
    if not 'ActivityID' in Updates: Updates['ActivityID'] = ActivityIDs[Updates['ActivityType']]
    if Updates.get('StartDate'): Updates['StartDate'] = convert_date(Updates['StartDate'], '%Y-%m-%d')

    field_mapping = {
        'JobID': 'P0',
        'ActivityID': 'P1',
        'StatusID': 'P2',
        'StartDate': 'P3',
        'ScheduledTime': 'P4',
        'Duration': 'P5',
        'Assignee': 'P6',
        'Notes': 'P7'
        }
    fields = {f'P{i}' : '' for i in range(11)}
    fields.update({ field_mapping[k]:v for k,v in Updates.items() if k in field_mapping })
    rsp = UpdateMoraware(mw_cookie=mw_cookie,
                         Serial=JobID,
                         FormType='Job_CreateJobActivity',
                         endpoint='job',
                         fields=fields,
                         client=client)
    return rsp

def UpdateJobForm(mw_Connect, JobID, FormID, form_type_id, Updates):
    '''
    Update a job form in Moraware.

    Args:
        mw_Connect: Moraware connection object.
        JobID: The Job ID to update the form for.
        FormID: The Form ID to update.
        form_type_id: The form type ID.
        Updates: Dictionary containing the updates to be made

    Returns:
        rsp: Response from the Moraware server.
    '''
    mw_cookie = mw_Connect.mw_cookie
    client = mw_Connect.client
    field_mapping = mw_Connect.Give(form_type_id)
    missing_fields = [k for k in Updates if k not in field_mapping]
    if missing_fields:
        print(f'Field not found in field mapping: {missing_fields}\nUpdating field mapping....')
        field_mapping = mw_Connect.Give(form_type_id, True)
    updates_field = [( field_mapping[k],str(v).replace('?', '') ) for k,v in Updates.items() if k in field_mapping]
    if not updates_field: return None
    upd = list(zip(*updates_field))
    updatedict = {  'P0': FormID,
                    'P1': '?'.join(upd[0]) + '?',
                    'P2': '?'.join(upd[1]) + '?',
                    'P3': '',
                    'P4': -1,
                    'P5': ''
                    }
    return UpdateMoraware(  mw_cookie=mw_cookie,
                            Serial=JobID,
                            FormType='Job_UpdateJobForm',
                            endpoint='job',
                            fields=updatedict,
                            client=client)

def CreateJobForm(mw_Connect, JobID, form_type_id, FormName='', Updates={}):
    field_mapping = mw_Connect.Give(form_type_id)
    missing_fields = [k for k in Updates if k not in field_mapping]
    if missing_fields:
        print(f'Field not found in field mapping: {missing_fields}\nUpdating field mapping....')
        field_mapping = mw_Connect.Give(form_type_id, True)
    if '_' in form_type_id: form_type_id = form_type_id.split('_')[-1]
    updates_field = [( field_mapping[k],v.replace('?', '') ) for k,v in Updates.items() if k in field_mapping]
    upd = list(zip(*updates_field))
    updatedict = {
        'P0': {
            'jobId': f'{JobID}',
            'formTemplateId': f'{form_type_id}',
            'formId': '',
            'modifiedFieldIds': '?'.join(upd[0]) + '?' if upd else '',
            'modifiedFieldValues': '?'.join(upd[1]) + '?' if upd else '',
            'formName': FormName,
            'phaseIds': '',
            'orderOnlyId': '',
            'cgOrderAreaUniqueId': ''
            }}
    UpdateMoraware(mw_cookie=mw_Connect.mw_cookie,
                    Serial=JobID,
                    FormType='Job2_CreateAndUpdateJobForm2',
                    fields=updatedict,
                    client=mw_Connect.client)



############################################################################### Inventory Materials ###############################################################################

def Give_BIN(mw_Connect, binconfig, client=CLIENT):
    mw_cookie = mw_Connect.mw_cookie
    binsheets = Fetch_View( url=binconfig['binsList'], mw_cookie=mw_cookie, headers=['name', 'account'] )
    bins = {b['name']:b for b in binsheets}

    binName = binconfig.get('binName', f"{datetime.now().strftime('%B %Y')} BIN Movements")
    if binName in bins:
        current_bin = bins[binName]
        bin_id = current_bin.get('name ID')
    else:
        print(f'Creating BIN Movement Job: {binName}')
        rsp = CreateJob(mw_cookie=mw_cookie,
                        JobName=binName,
                        AccountID=binconfig['accountID'],
                        TemplateID=binconfig['templateID'],
                        ProcessID=binconfig['processID'],
                        client=client)
        bin_id = rsp.text
        print(f'Created BIN Movement Job: {binName} with ID {bin_id}')
    bin_job = MorawareJob(mw_Connect, bin_id)
    bin_job.total_slabs_allocated = 0
    for activity in bin_job.JobData['Activities']:
        bin_job.total_slabs_allocated += len(activity['Materials'])
    return bin_job

def slabdata_from_entry(entry, ProductIDs):
    '''
    Get the slab data from an inventory list - for example the bin list.

    Args:
        entry: The entry from the inventory list.
        ProductIDs: The product IDs from the inventory.

    Returns:
        SlabData: The slab data for the entry.
    '''
    namekey = f"{entry['Product Family']}{entry['Product Line']}{entry['Product']}"
    if namekey not in ProductIDs:
        print(f"Product not found in Inventory Data: {namekey}")
        return None
    FullStoneName = entry['Product Variant'] # Full name of the stone variant, including all attributes.
    FullStoneName.replace(entry['Product'], '').strip() # Remove the product from the variant name.
    VariantData = ProductIDs[namekey] # Attribute lists for this product.
    AttrIDs = []
    for attrCat, attrList in VariantData['_ATTR'].items(): # Dict of { attrCategory(colour, thickness, etc): [attr1, attr2, ...] }
        attrmatchlen = 0 #Give the best match for the attribute.
        match_attr = None
        for val in attrList:
            if val['Name'] in FullStoneName: #Checking if the attribute name is in the variant name.
                if len(val['Name']) > attrmatchlen: #Checking how much of the attribute name is in the variant name.
                    match_attr = val
                    attrmatchlen = len(val['Name']) #Updating the best match.
        if match_attr: #If a match is found, add the attribute ID to the list and remove the attribute name from the variant name.
            AttrIDs.append(match_attr['ID'])
            FullStoneName = FullStoneName.replace(match_attr['Name'], '').strip()
        else:
            print(f'Attribute not found for {namekey}: {attrCat} - {FullStoneName}')

    SlabData = {
        'ProductID': VariantData['Product ID'],
        'SN_ID': entry['Serial Number ID'],
        'SN_Display': entry['Serial Number'],
        'SQM_Allocating': entry['Available Qty'],
        'SQM_OG': entry['Available Qty']
        }
    for i,attr in enumerate(AttrIDs): SlabData[f'AttrID{i+1}'] = attr
    return SlabData

def doBin(mw_Connect, binconfig):
    client = mw_Connect.client
    ind = 1
    binName = binconfig.get('binName', f"{datetime.now().strftime('%B %Y')} BIN Movements")

    def bin_full_check(bin_job): return bin_job.total_slabs_allocated >= 100   
    def next_bin():
        nonlocal ind
        ind += 1
        binconfig['binName'] = f"{binName} - {ind}"
        return Give_BIN(binconfig=binconfig, mw_Connect=mw_Connect, client=client)
    def Give_binActivity(bin_job):
        for activity in bin_job.JobData['Activities']:
            if activity['Activity Type'] == 'Stone Reservations & Adjustments' and activity['Start Date'] == datetime.now().strftime('%d/%m/%Y'):
                return activity['ActivityID']
        datestring = datetime.now().strftime('%Y-%m-%d')
        print(f'Creating BIN Movement Activity: {datestring}')
        rsp = bin_job.CreateActivity(ActivityType='Stone Reservations & Adjustments', StartDate=datestring)
        return rsp.text

    binnableList = binconfig['binnable']
    InvV = mw_Connect.Give('ProductIDs')
    binslabs = mw_Connect.GetView(binnableList)
    binnable = []
    for binned in binslabs: 
        SlabData = slabdata_from_entry(binned, InvV)
        if SlabData: binnable.append(SlabData)
    if not binnable: return None

    bin_job = Give_BIN(binconfig=binconfig, mw_Connect=mw_Connect, client=client)
    while bin_full_check(bin_job):
        bin_job = next_bin()
    actid = Give_binActivity(bin_job)

    print(f'Allocating {len(binnable)} slabs to {bin_job.JobData["JobName"]}')
    while len(binnable) > 0:
        print(f'    Remaining: {len(binnable)} - Current Bin: {bin_job.JobData["JobName"]}')
        if bin_full_check(bin_job):
            while bin_full_check(bin_job):
                bin_job = next_bin()
            actid = Give_binActivity(bin_job)
        else:
            slab = binnable.pop()
            bin_job.AllocateMaterial(actid, slab)
            bin_job.total_slabs_allocated += 1
    return bin_job



############################################################################### PS Specific Functions ###############################################################################
######## All the below are in the webapp - can be safely removed from the API. ########

def PS__NewJob_Updates(MWJob, MWQuote): ##### PS SPECIFIC
    '''
    New version of the JobCreate_update function.
    Utilises the MorawareJob, MorawareQuote and MorawareConnection classes.
    Performs initial job updates for setting up a new job from a quote.

    PS Specific. Uses PS Specific new job fields function, published to form_8 (the job card)

    Args:
        MWJob: MorawareJob object.
        MWQuote: MorawareQuote object.

    Returns:
        None
    '''
    QuoteData = MWQuote.QuoteData
    jid = MWJob.JobID
    template = datetime.strptime(QuoteData['Template Date'], '%d/%m/%Y')
    rsp = MWJob.UpdateActivity('Template', {'Start Date': template.strftime('%Y-%m-%d'), 'Status': 'Estimate'})
    rsp = MWJob.UpdateActivity('Deposit Inv Sent', {'Status': 'Estimate'})
    JobCardFields = PS__Give_NewJob_JobCard_Fieldsv2(QuoteData)#, fieldmapping=FormFields)
    # jcid = MWJob.JobData['JobCard']['JobCardID']
    jcid = MWJob.JobData['Forms'][0]['JobCardID']
    rsp = MWJob.UpdateJobForm(jcid, JobCardFields, 'form_80')


def PS__Give_NewJob_JobCard_Fields(QuoteData): ##### PS SPECIFIC
    '''
    Give the fields for updating a new job jobcard with initial quote data.
    Defaults to field IDs for environment Job Card.

    PS Specific. Uses PS Specific quote line definitions to match with jobcard fields.

    Args:
        QuoteData: The QuoteData dictionary.

    Returns:
        dict: The fields for updating
    '''
    fields = []
    edge = ''
    NoteField = ''
    # if QuoteData.get('Built Edge'): fields.append( ( 'Built Edge', '1' ) )
    for line in QuoteData['QuoteLines']:
        if line[0] == 'Pieces': NoteField += f'> Pieces: {len(line[1])}\n'
        elif line[0] == 'Quoted': NoteField += ' '.join(line[1:]) + '\n'
        else: NoteField += '> ' + ' '.join(line[1:]) + '\n'
        
        if line [0] == 'Includes':
            if 'Tap' in line[1]: fields.append( ( 'Tap', '1' ) )
            if 'Hob' in line[1]: fields.append( ( 'Hob', '1' ) )
        elif line[0] == 'Edge Finish':
            if edge: edge += '\n'
            edge += ' '.join(line[1:])
            if 'Mitre' in line[1]: fields.append( ( 'Mitred', '1' ) )
        elif 'Waterjet' in line[0]: fields.append( ( 'Waterjet', '1' ) )
        elif line[0] == 'Quoted': fields.append( ( 'Templating & Installation', ' '.join(line[1:]) ) )
    fields.append( ( 'Job Detail Notes', NoteField ) )
    fields.append( ( 'Edge Detail', edge ) )
    return {k: v for k,v in fields}

def PS__Give_NewJob_JobCard_Fieldsv2(QuoteData): ##### PS SPECIFIC
    '''
    Give the fields for updating a new job jobcard with initial quote data.
    Defaults to field IDs for environment Job Card.

    PS Specific. Uses PS Specific quote line definitions to match with jobcard fields.

    Args:
        QuoteData: The QuoteData dictionary.

    Returns:
        dict: The fields for updating
    '''
    fields = []
    edge = ''
    NoteField = ''
    # if QuoteData.get('Built Edge'): fields.append( ( 'Built Edge', '1' ) )
    for line in QuoteData['QuoteLines']:
        if line[0] == 'Pieces': NoteField += f'-- Pieces: {len(line[1])}\n'
        # elif line[0] == 'Quoted': NoteField += ' '.join(line[1:]) + '\n'
        # else: NoteField += '> ' + ' '.join(line[1:]) + '\n'
        
        elif line [0] == 'Includes':
            for ea in ('Tap', 'Hob', 'Sink'):
                if ea in line[1]:
                    fields.append( ( ea, '1' ) )
            if 'Mileage' in line[1] or 'Care Kit' in line[1]: continue
            notes_entry = line[1:]
            try: notes_entry[-1] = str(int(float(notes_entry[-1]))) # round the decimal string by converting to int.
            except: pass
            entry_str = f"-- {notes_entry[0].replace('Includes', '').strip()} x{notes_entry[-1]}\n"
            NoteField += entry_str

        elif line[0] == 'Edge Finish':
            if edge: edge += '\n'
            edge += ' '.join(line[1:])
            if 'Mitre' in line[1]: fields.append( ( 'Mitred', '1' ) )
        elif line[0] == 'Quoted': fields.append( ( 'Templating & Installation', ' '.join(line[1:]) ) )
        elif line[0] == 'Measurements': NoteField += '-- ' + ' '.join(line[1:]) + '\n'
        elif 'Waterjet' in line[0]: fields.append( ( 'Waterjet', '1' ) )
        elif 'Material' in line[0]: fields.append( ( 'Stone Colour', ' '.join(line[1:]) ) )
        else:
            print(f'Unknown line in quote: {line[0]}')
            NoteField += '-- ' + ' '.join(line[1:]) + '\n'
    fields.append( ( 'Job Detail Notes', NoteField ) )
    fields.append( ( 'Edge Detail', edge ) )
    return {k: v for k,v in fields}
