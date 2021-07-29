from helpers import ClilocIDExists, GetParam
from py_stealth import *
from py_stealth.methods import *
from transitions import Machine
from RunebookHandler import Runebook

#### Variables ####
_corpse = 2006
LootBag = Backpack
_robe = 0x1F04
_gold = 0x0EED



_runebook = Runebook('Rune','recall','osi')
#### End Vars
## Pathing Coordinates ##
x_f = 4195
y_f = 3260
x_door = 1135
y_door = 1166
x2_door = 1139
y2_door = 1166
x = 1183,1183,1184,1187, 1187
y = 1189,1182,1177, 1175, 1126

def Pathing(x,y):
    NewMoveXY(x,y,True,1,True)
    if GetX(Self) == x and GetY(Self)== y:
        return True
    else:  
        return False, AddToSystemJournal('Cannot reach destination')



class Bot(object):

    states = ['fighting','looting','fleeing','moving','banking','disconnected']

    def __init__(self,name):
        self.name = name
        self.gold = 0
        self.machine = Machine(model = self,states = Bot.states, initial='moving')

        self.machine.add_transition('fighting','moving','looting')
        self.machine.add_transition('fleeing','*','banking')
        self.machine.add_transition('looting','fighting','banking')
        self.machine.add_transition('banking','looting','moving',before='CheckWeight')
        self.machine.add_transition('disconnected','*','moving', conditions=['is_disconnected'])

    
    def CheckWeight(self):
        if (Weight() >= MaxWeight()-20):
            if FindTypeEx(_gold, 0xFFFF, Backpack(), True):
                #_gold = GetFoundList()
                # _runebook.Recall(0)
                # Wait(1500)
                # WaitTargetObject(_gold[0])
                #return GetQuantity(FindItem())
                return True
        return False
   
    def Reconnect(self):
        while not Connected():
            Connect()
            Wait(10000)
            return AddToSystemJournal('Back online')
    
    @property
    def is_disconnected(self):
        if not Connected():
            return True
        return False



def InsureItem(_item):
    Wait(250)
    RequestContextMenu(Self())
    _i = 0
    for _menuItem in GetContextMenu().splitlines():
        if "Toggle Item Insurance" in _menuItem:
            SetContextMenuHook(Self(), _i)
            Wait(250)
            WaitTargetObject(_item)
            Wait(250)
            CancelMenu()
        else:
            _i += 1
            AddToSystemJournal("Couldn't find insure menu item.")
    CancelAllMenuHooks()
    CancelTarget()
    return

def LootCorpse(_corpse):
    UseObject(_corpse)
    Wait(1500)
    if FindTypesArrayEx([0xFFFF], [0xFFFF], [_corpse], True):
        _lootList = GetFindedList()
        for _loot in _lootList:
            if GetType(_loot) == _gold:
                _count = GetQuantity(_loot)
                MoveItem(_loot, _count, LootBag, 0, 0, 0)
            if GetType(_loot) == _robe: #### Robes
                AddToSystemJournal(f'Looting Item: {_loot}')
                MoveItem(_loot, 1, LootBag, 0, 0, 0)
                InsureItem(_loot)
            _tooltipRec = GetTooltipRec(_loot)
            if GetParam(_tooltipRec, 1112857) >= 20 and not\
                    ClilocIDExists(_tooltipRec, 1152714) and not\
                    ClilocIDExists(_tooltipRec, 1049643): ###Code to loot weapons with splintering
                AddToSystemJournal(f'Looting Item: {_loot}')
                MoveItem(_loot, 1, LootBag, 0, 0, 0)
                InsureItem(_loot)
    Ignore(_corpse)
    return


