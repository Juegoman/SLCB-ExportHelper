import clr, json, os, sys, codecs, re, System, csv, inspect, pprint
clr.AddReference([asbly for asbly in System.AppDomain.CurrentDomain.GetAssemblies() if "AnkhBotR2" in str(asbly)][0])
import AnkhBotR2

ScriptName = "Export Helper"
Description = "Script to help export chatbot data to file."
Creator = "EncryptedThoughts"
Version = "1.0.0"
Website = "twitch.tv/encryptedthoughts"

#---------------------------
#   Define Global Variables
#---------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
ReadMe = os.path.join(os.path.dirname(__file__), "README.md")

#---------------------------------------
# Classes
#---------------------------------------
class Settings(object):
    def __init__(self, SettingsFile=None):
        if SettingsFile and os.path.isfile(SettingsFile):
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        else:
            self.EnableDebug = True

    def Reload(self, jsondata):
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        return

    def Save(self, SettingsFile):
        try:
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(SettingsFile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return

#---------------------------------------
#   [Required] Initialize Data / Load Only
#---------------------------------------
def Init():
    global ScriptSettings
    ScriptSettings = Settings(SettingsFile)
    ScriptSettings.Save(SettingsFile)

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    ScriptSettings.__dict__ = json.loads(jsonData)
    ScriptSettings.Save(SettingsFile)
    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):

    regex = "\$export\(\s*(quotes|extraQuotes|queue)\s*,\s*[0-9]+\s*,\s*.*\s*\,.*\)" # !export(string,number,string,string)
    item = re.search(regex, parseString)
    if item is not None:
        rawArguments = item.group().strip()[8:][:-1]
        args = rawArguments.split(",")

        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, str(args))

        exportType = args[0]
        startIndex = int(args[1])-1
        endIndex = args[2]
        fileName = args[3]

        if exportType == "quotes":
            SaveQuotesToFile(startIndex, endIndex, fileName)
        elif exportType == "extraQuotes":
            SaveExtraQuotesToFile(startIndex, endIndex, fileName)
        elif exportType == "queue":
            SaveQueueToFile(startIndex, endIndex, fileName)

        parseString = parseString.replace(item.group(), "")
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, parseString)

    return parseString

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

def OpenReadme():
    os.startfile(ReadMe)

def ExportQuotesButton():
    SaveQuotesToFile(0,"max","QuotesExport")

def ExportExtraQuotesButton():
    SaveExtraQuotesToFile(0,"max","ExtraQuotesExport")

def ExportQueueButton():
    SaveQueueToFile(0,"max","QueueExport")

def ExportCommandsButton():
    SaveCommandsToFile()

def ExportSFXButton():
    SaveSFXToFile()

def ExportCurrencyButton():
    SaveCurrencyToFile()

def get_sfx_list():
    """
    List items have the following properties:
        - Name
        - File
        - Volume
        - Votes
        - Group
        - Commands
    """
    g_manager = AnkhBotR2.Managers.GlobalManager.Instance
    sfx = g_manager.VMLocator.SFXView.SFX
    return list(sfx) # Convert to list to make a copy of the ObservableCollection

def get_command_list():
    g_manager = AnkhBotR2.Managers.GlobalManager.Instance
    commands = g_manager.VMLocator.CommandView.Commands
    return list(commands)

def get_currency_list():
    g_manager = AnkhBotR2.Managers.GlobalManager.Instance
    currencies = g_manager.VMLocator.CurrencyView.Users
    return list(currencies)

def SaveSFXToFile():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    log = os.path.join(os.path.dirname(__file__) + "\Exports", "sfx.csv")

    sfxs = get_sfx_list()

    with codecs.open(log, "w", encoding="utf-8") as fout:
        
        writer = csv.writer(fout, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["name", "file", "volume"])

        for index, sfx in enumerate(sfxs):

            writer.writerow([
                sfx.Name,
                sfx.File,
                sfx.Volume,
            ])

def SaveCurrencyToFile():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    log = os.path.join(os.path.dirname(__file__) + "\Exports", "currency.csv")

    currencys = get_currency_list()

    with codecs.open(log, "w", encoding="utf-8") as fout:
        
        writer = csv.writer(fout, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["name", "rank", "points", "minutes"])

        for index, c_info in enumerate(currencys):

            writer.writerow([
                c_info.User.Name,
                c_info.Rank,
                c_info.Points,
                c_info.TimeWatched,
            ])

def SaveCommandsToFile():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    log = os.path.join(os.path.dirname(__file__) + "\Exports", "commands.csv")

    commands = get_command_list()
    # sfx_list = get_sfx_list()

    # sfx_mapping = {
    #     sfx.Name: {
    #         "File": sfx.File,
    #         "Volume": sfx.Volume
    #     }
    #     for sfx in sfx_list
    # }

    with codecs.open(log, "w", encoding="utf-8") as fout:
        writer = csv.writer(fout, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["name", "cost", "cooldown", "userCooldown", "sound"])
        # writer.writerow(["name", "cost", "cooldown", "userCooldown", "sound", "sfx_file", "sfx_volume"])
        for index, command in enumerate(commands):
            # Look up the associated sfx by command.SoundFile
            # associated_sfx = sfx_mapping.get(command.SoundFile)

            # If the sfx is found, extract its attributes; otherwise, default to empty strings
            # sfx_file = associated_sfx["File"] if associated_sfx else ""
            # sfx_volume = associated_sfx["Volume"] if associated_sfx else ""

            writer.writerow([
                command.Name,
                command.Cost,
                command.Cooldown,
                command.UserCooldown,
                command.SoundFile,
                # sfx_file,    # Add the sfx file attribute
                # sfx_volume   # Add the sfx volume attribute
            ])
    

def SaveQuotesToFile(startIndex, endIndex, fileName):    
    quoteView = AnkhBotR2.Managers.GlobalManager.Instance.VMLocator.QuoteView
    quotes = list(quoteView.Quotes)

    if endIndex == "max":
        quotes = quotes[startIndex:]
    else:
        quotes = quotes[startIndex:int(endIndex)-1]

    file = os.path.join(os.path.dirname(__file__) + "\Exports", fileName + ".csv")
    Parent.Log(ScriptName, file)
    with open(file, 'w') as f:
        for quote in quotes:
            f.write(str(int(quote.Id)+1) + "," + quote.Text.encode('utf-8') +  "\n")

def SaveExtraQuotesToFile(startIndex, endIndex, fileName):
    extraQuoteView = AnkhBotR2.Managers.GlobalManager.Instance.VMLocator.ExtraQuoteView
    quotes = list(extraQuoteView.ExtraQuotes)

    if endIndex == "max":
        quotes = quotes[startIndex:]
    else:
        quotes = quotes[startIndex:int(endIndex)-1]

    file = os.path.join(os.path.dirname(__file__) + "\Exports", fileName + ".csv")
    Parent.Log(ScriptName, file)
    with open(file, 'w') as f:
        for quote in quotes:
            f.write(str(int(quote.Id)+1) + "," + quote.Text.encode('utf-8') +  "\n")

def SaveQueueToFile(startIndex, endIndex, fileName):
    queueView = AnkhBotR2.Managers.GlobalManager.Instance.VMLocator.Queue
    queue = list(queueView.Queue)

    if endIndex == "max":
        queue = queue[startIndex:]
    else:
        queue = queue[startIndex:int(endIndex)-1]

    file = os.path.join(os.path.dirname(__file__) + "\Exports", fileName + ".csv")
    Parent.Log(ScriptName, file)
    with open(file, 'w') as f:
        for entry in queue:
            f.write(str(int(entry.Id)+1) + "," + str(entry.Time) + "," + str(entry.UserId) + "," + str(entry.User.Name) + "," + entry.Note.encode('utf-8') + "\n")