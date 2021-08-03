from threading import Timer
from helpers import ClilocIDExists, GetParam
from py_stealth import *
from py_stealth.methods import *
from transitions import Machine
from RunebookHandler import Runebook
from random import randint

#### Variables ####
corpse_type = 2006
LootBag = Backpack
_waitLag = 200
secureID = 0
gold = 0
robes = 0
home_rune = 0
pet_id = 0

### Runebook vars ####
_runebook = Runebook('Rune','recall','osi')


#### End Vars
## Pathing Coordinates ##
x_f = [4195]
y_f = [3260]
x_door = [1135]
y_door = [1166]
x2_door = [1139]
y2_door = [1166]
x = [1183,1183,1184,1187, 1187]
y = [1189,1182,1177, 1175, 1126]

def Pathing(arr_x,arr_y):
    for x,y in arr_x,arr_y:
        NewMoveXY(x,y,True,1,True)
        Wait(_waitLag)
        if GetX(Self) == x and GetY(Self)== y:
            AddToSystemJournal('I got there ')
        else:  
            AddToSystemJournal('Cannot reach destination')



def GoTo(rune):
    _x = GetX(Self)
    _y = GetY(Self)
    while _x == GetX(Self) and _y == GetY(Self):
        _runebook.Recall(rune)
        Wait(_waitLag)
    
# class Bot(object):

#     states = ['fighting','looting','fleeing','moving','banking','disconnected']

#     def __init__(self,name):
#         self.name = name
#         self.gold = 0
#         self.machine = Machine(model = self,states = Bot.states, initial='moving')

#         self.machine.add_transition('fighting','moving','looting')
#         self.machine.add_transition('fleeing','*','banking')
#         self.machine.add_transition('looting','fighting','banking')
#         self.machine.add_transition('banking','looting','moving',before='CheckWeight')
#         self.machine.add_transition('disconnected','*','moving', conditions=['is_disconnected'])

    
def CheckWeight():
    if (Weight() >= MaxWeight()-20):
        return True
    return False


def dropItems(secureID):
    if FindTypeEx(0x0EED, 0xFFFF, Backpack(), True):
        _gold = GetFoundList()
        _runebook.Recall(home_rune)
        Wait(_waitLag)
        MoveItem(_gold[0],GetQuantity(_gold[0]),secureID,0,0,0)
        gold += GetQuantity(_gold[0])
        AddToSystemJournal('Total gold = '+ IntToStr(gold))
    if FindType(0x1F04, Backpack()):
        robes += 1
        MoveItem(FindItem,1,secureID,0,0,0)
        AddToSystemJournal('Total robes = ' + IntToStr(robes))
        return True
    return False

def Reconnect():
    while not Connected():
        Connect()
        Wait(10000)
        return AddToSystemJournal('Back online')
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
            if GetType(_loot) == 0x0EED:
                _count = GetQuantity(_loot)
                MoveItem(_loot, _count, LootBag, 0, 0, 0)
            if GetType(_loot) == 0x1F04: #### Robes
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
    if CheckWeight == True:
        dropItems(secureID)
    return

def safePosition(monster):
    while Dist(GetX(Self),GetY(Self),GetX(monster),GetY(monster)) < 4:
        Pathing(GetX(Self)* randint(-4,4),GetY(Self)* randint(-4,4))

def watchHealth(monster):
    if GetHP(Self) < (GetMaxHP(Self) - 30):
        if IsPoisoned(Self):
            Cast('Cure')
            WaitForTarget(2000)
            TargetID(Self)
            Wait(300)
        safePosition(monster)## Need to add monster we are fighting
        Cast('Heal')
        WaitForTarget(1000)
        TargetID(Self)

def locateBehindPet(pet_id , monster):
    if Dist(GetX(Self),GetY(Self),GetX(pet_id),GetY(pet_id))> 1:
        _x = 0
        _y = 0
        if GetX(pet_id) > GetX(monster):
            x = GetX(pet_id) + 1
        else:
            x = GetX(pet_id) - 1
        if GetY(pet_id) > GetY(monster):
            y = GetY(pet_id) + 1
        else:
            y = GetY(pet_id) - 1
        Pathing(_x,_y)
    

def healPet(pet_id,monster):
    

    if GetHP(pet_id) < GetMaxHP(pet_id)-100:
        locateBehindPet(pet_id, monster) 
        if FindType(0x02E0,Backpack) > 15:
            UseObject(FindItem)
            WaitForTarget(2000)
            TargetID(pet_id)
        else:
            AddToSystemJournal('Get bandages only ' + IntToStr(GetQuantity(FindItem)) + 'left')
            UseObject(FindItem)
            WaitForTarget(2000)
            TargetID(pet_id)
        return True 
    return False

def fightMonster(monster):
    hp = GetHP(monster)
    maxHp = GetMaxHP(monster)
    idle = 0
    watchHealth(monster)
    healPet(pet_id,monster)
    if Mana > 20 and (maxHp - hp)/maxHp > 0.2:
        Cast('Fireball')
        WaitForTarget(2000)
        TargetID(monster)
        idle = 500
    elif Mana > 50 and (maxHp - hp)/maxHp < 0.2:
        Cast('Word of Death')
        WaitForTarget(5000)
        TargetID(monster)
        idle(1000)
    return idle

def Go_Tyball():
    Pathing(x_f,y_f)
    Pathing(x_door,y_door)
    UseObject()
    Wait(_waitLag)
    Pathing(x2_door,y2_door)
    UseObject()
    Wait(_waitLag)
    Pathing(x,y)

def findMonster(monsters):
    if FindTypesArrayEx([monsters], [0xFFFF], [Ground], True):
        _monsters = GetFindedList()     
    for monster in _monsters:
        fightMonster(monster)

if __name__ == '__main__':
    SetFindDistance(15)
    SetFindVertical(10)

    while True:
        Go_Tyball
