from .manifest import Manifest
from typing import Optional, Any

class Coordinates:
    def __init__(
        self,
        X:int,
        Y:int,
        toX:int,
        toY:int
    ):
        self.X=X
        self.Y=Y
    def getJson(self) -> str:
        return f"{self.X},{self.Y}/{self.toX},{self.toY}"

class SpawnTimingSettings:
    def __init__(
        self,
        StartTime:int,
        TimeEndTime:int,
        MinimumTimeBetweenSpawns:int=10,
        MaximumSimultaneousSpawns:int=1,
        OnlySpawnIfAPlayerIsPresent:bool=False,
        SpawnSound:str=""
    ):
        self.StartTime=StartTime
        self.TimeEndTime=TimeEndTime
        self.MinimumTimeBetweenSpawns=MinimumTimeBetweenSpawns if MinimumTimeBetweenSpawns>=10 else 10
        self.MaximumSimultaneousSpawns=MaximumSimultaneousSpawns if MaximumSimultaneousSpawns>=1 else 1
        self.OnlySpawnIfAPlayerIsPresent=OnlySpawnIfAPlayerIsPresent
        self.SpawnSound=SpawnSound
    
    def getJson(self) -> dict:
        return {
            "StartTime":self.StartTime,
            "TimeEndTime":self.TimeEndTime,
            "MinimumTimeBetweenSpawns":self.MinimumTimeBetweenSpawns,
            "MaximumSimultaneousSpawns":self.MaximumSimultaneousSpawns,
            "OnlySpawnIfAPlayerIsPresent":self.OnlySpawnIfAPlayerIsPresent,
            "SpawnSound":self.SpawnSound
        }

class ExtraConditions:
    def __init__(
        self,
        Years:list[str]=[],
        Seasons:list[str]=[],
        Days:list[str]=[],
        WeatherYesterday:list[str]=[],
        WeatherToday:list[str]=[],
        WeatherTomorrow:list[str]=[],
        GameStateQueries:list[str]=[],
        CPConditions:dict[str, str]={},
        EPUPreconditions:list[str]=[],
        LimitedNumberOfSpawns:Optional[int]=None
    ):
        self.Years=Years        
        self.Seasons=Seasons
        self.Days=Days
        self.WeatherYesterday=WeatherYesterday
        self.WeatherToday=WeatherToday
        self.WeatherTomorrow=WeatherTomorrow
        self.GameStateQueries=GameStateQueries
        self.CPConditions=CPConditions
        self.EPUPreconditions=EPUPreconditions
        self.LimitedNumberOfSpawns=LimitedNumberOfSpawns
    
    def getJson(self) -> dict:
        return {
            "Years":self.Years,
            "Seasons":self.Seasons,
            "Days":self.Days,
            "WeatherYesterday":self.WeatherYesterday,
            "WeatherToday":self.WeatherToday,
            "WeatherTomorrow":self.WeatherTomorrow,
            "GameStateQueries":self.GameStateQueries,
            "CPConditions":self.CPConditions,
            "EPUPreconditions":self.EPUPreconditions,
            "LimitedNumberOfSpawns":self.LimitedNumberOfSpawns
        }

class Areas:
    def __init__(
        self,
        UniqueAreaID:str,
        MapName:str,
        MinimumSpawnsPerDay:str,
        MaximumSpawnsPerDay:str,
        SpawnTiming: SpawnTimingSettings,
        ExtraConditions: ExtraConditions,
        IncludeTerrainTypes:Optional[list[str]]=[],
        ExcludeTerrainTypes:Optional[list[str]]=[],
        IncludeCoordinates:Optional[list[Coordinates]]=[],
        ExcludeCoordinates:Optional[list[Coordinates]]=[],
        StrictTileChecking:Optional[str]="Maximum",
        DaysUntilSpawnsExpire:Optional[int|None]=None       
    ):
        self.UniqueAreaID=UniqueAreaID
        self.MapName=MapName
        self.MinimumSpawnsPerDay=MinimumSpawnsPerDay
        self.MaximumSpawnsPerDay=MaximumSpawnsPerDay
        self.SpawnTiming=SpawnTiming.getJson()
        self.ExtraConditions=ExtraConditions.getJson()
        self.IncludeTerrainTypes=IncludeTerrainTypes
        self.ExcludeTerrainTypes=ExcludeTerrainTypes
        self.IncludeCoordinates=[item.getJson() for item in IncludeCoordinates]
        self.ExcludeCoordinates=[item.getJson() for item in ExcludeCoordinates]
        self.StrictTileChecking=StrictTileChecking
        self.DaysUntilSpawnsExpire=DaysUntilSpawnsExpire
    
    def getJson(self) -> dict:
        return {
            "UniqueAreaID":self.UniqueAreaID,
            "MapName":self.MapName,
            "MinimumSpawnsPerDay":self.MinimumSpawnsPerDay,
            "MaximumSpawnsPerDay":self.MaximumSpawnsPerDay,
            "SpawnTiming":self.SpawnTiming,
            "ExtraConditions":self.ExtraConditions,
            "IncludeTerrainTypes":self.IncludeTerrainTypes,
            "ExcludeTerrainTypes":self.ExcludeTerrainTypes,
            "IncludeCoordinates":self.IncludeCoordinates,
            "ExcludeCoordinates":self.ExcludeCoordinates,
            "StrictTileChecking":self.StrictTileChecking,
            "DaysUntilSpawnsExpire":self.DaysUntilSpawnsExpire
        }

class ForageAreas(Areas):
    def __init__(
        self,
        SpringItemIndex:Any,
        SummerItemIndex:Any,
        FallItemIndex:Any,
        WinterItemIndex:Any,
        UniqueAreaID:str,
        MapName:str,
        MinimumSpawnsPerDay:str,
        MaximumSpawnsPerDay:str,
        SpawnTiming: SpawnTimingSettings,
        ExtraConditions: ExtraConditions,
        IncludeTerrainTypes:Optional[list[str]]=[],
        ExcludeTerrainTypes:Optional[list[str]]=[],
        IncludeCoordinates:Optional[list[Coordinates]]=[],
        ExcludeCoordinates:Optional[list[Coordinates]]=[],
        StrictTileChecking:Optional[str]="Maximum",
        DaysUntilSpawnsExpire:Optional[int|None]=None
    ):
        self.SpringItemIndex=SpringItemIndex
        self.SummerItemIndex=SummerItemIndex
        self.FallItemIndex=FallItemIndex
        self.WinterItemIndex=WinterItemIndex
        super().__init__(UniqueAreaID, MapName, MinimumSpawnsPerDay, MaximumSpawnsPerDay, SpawnTiming, ExtraConditions, IncludeTerrainTypes, ExcludeTerrainTypes, IncludeCoordinates, ExcludeCoordinates, StrictTileChecking, DaysUntilSpawnsExpire)
        
    
    def getJson(self) -> dict:
        json=super().getJson()
        
        json["SpringItemIndex"]=self.SpringItemIndex,
        json["SummerItemIndex"]=self.SummerItemIndex,
        json["FallItemIndex"]=self.FallItemIndex,
        json["WinterItemIndex"]=self.WinterItemIndex,
        return json

class OreAreas(Areas):
    def __init__(
        self,
        UniqueAreaID:str,
        MapName:str,
        MinimumSpawnsPerDay:str,
        MaximumSpawnsPerDay:str,
        SpawnTiming: SpawnTimingSettings,
        ExtraConditions: ExtraConditions,
        MiningLevelRequired:dict[str, int]=None,
        StartingSpawnChance:dict[str, int]=None,
        LevelTenSpawnChance:dict[str, int]=None,
        IncludeTerrainTypes:Optional[list[str]]=[],
        ExcludeTerrainTypes:Optional[list[str]]=[],
        IncludeCoordinates:Optional[list[Coordinates]]=[],
        ExcludeCoordinates:Optional[list[Coordinates]]=[],
        StrictTileChecking:Optional[str]="Maximum",
        DaysUntilSpawnsExpire:Optional[int|None]=None       
    ):
        self.MiningLevelRequired=MiningLevelRequired
        self.StartingSpawnChance=StartingSpawnChance
        self.LevelTenSpawnChance=LevelTenSpawnChance
        super().__init__(UniqueAreaID, MapName, MinimumSpawnsPerDay, MaximumSpawnsPerDay, SpawnTiming, ExtraConditions, IncludeTerrainTypes, ExcludeTerrainTypes, IncludeCoordinates, ExcludeCoordinates, StrictTileChecking, DaysUntilSpawnsExpire)
        
    def getJson(self) -> dict:
        json= super().getJson()
        json["MiningLevelRequired"]=self.MiningLevelRequired
        json["StartingSpawnChance"]=self.StartingSpawnChance
        json["LevelTenSpawnChance"]=self.LevelTenSpawnChance
        return json

class LargueObjectAreas(Areas):
    def __init__(
        self,
        ObjectTypes:list[str],
        FindExistingObjectLocations:bool,
        RelatedSkill:str,
        UniqueAreaID:str,
        MapName:str,        
        MinimumSpawnsPerDay:str,
        MaximumSpawnsPerDay:str,
        SpawnTiming: SpawnTimingSettings,
        ExtraConditions: ExtraConditions,        
        PercentExtraSpawnsPerSkillLevel:int=0,
        IncludeTerrainTypes:Optional[list[str]]=[],
        ExcludeTerrainTypes:Optional[list[str]]=[],
        IncludeCoordinates:Optional[list[Coordinates]]=[],
        ExcludeCoordinates:Optional[list[Coordinates]]=[],
        StrictTileChecking:Optional[str]="Maximum",
        DaysUntilSpawnsExpire:Optional[int|None]=None
    ):
        self.ObjectTypes=ObjectTypes
        self.FindExistingObjectLocations=FindExistingObjectLocations
        self.RelatedSkill=RelatedSkill
        self.PercentExtraSpawnsPerSkillLevel=PercentExtraSpawnsPerSkillLevel
        super().__init__(UniqueAreaID, MapName, MinimumSpawnsPerDay, MaximumSpawnsPerDay, SpawnTiming, ExtraConditions, IncludeTerrainTypes, ExcludeTerrainTypes, IncludeCoordinates, ExcludeCoordinates, StrictTileChecking, DaysUntilSpawnsExpire)
        
    def getJson(self) -> dict:
        json=super().getJson()
        json["ObjectTypes"]=self.ObjectTypes,
        json["FindExistingObjectLocations"]=self.FindExistingObjectLocations,
        json["RelatedSkill"]=self.RelatedSkill,
        json["PercentExtraSpawnsPerSkillLevel"]=self.PercentExtraSpawnsPerSkillLevel,
        return json

class MonsterTypeSettings:
    def __init__(
        self,
        SpawnWeight:int=1,
        HP:int=1,
        CurrentHP:int=1,
        PersistentHP:bool=False,
        Damage:int=0,
        Defense:int=0,
        DodgeChance:int=0,
        EXP:int=0,
        ExtraLoot:bool=True,
        SeesPlayersAtSpawn:bool=False,
        RangedAttacks:bool=True,
        InstantKillImmunity:bool=False,
        StunImmunity:bool=False,
        Segments:int=0,
        MinimumSkillLevel:int=0,
        MaximumSkillLevel:int=0,


        Loot:Optional[list[int|str]]=None,
        SightRange:Optional[int]=None,
        FacingDirection:Optional[str]=None,
        Sprite:Optional[str]=None,
        Color:Optional[str]=None,
        MinColor:Optional[str]=None,
        MaxColor:Optional[str]=None,
        Gender:Optional[str]=None,
        RelatedSkill:Optional[str]=None,
        PercentExtraHPPerSkillLevel:Optional[int]=None,
        PercentExtraDamagePerSkillLevel:Optional[int]=None,
        PercentExtraDefensePerSkillLevel:Optional[int]=None,
        PercentExtraDodgeChancePerSkillLevel:Optional[int]=None,
        PercentExtraEXPPerSkillLevel:Optional[int]=None
    ):
        self.SpawnWeight=SpawnWeight
        self.HP=HP
        self.CurrentHP=CurrentHP
        self.PersistentHP=PersistentHP
        self.Damage=Damage
        self.Defense=Defense
        self.DodgeChance=DodgeChance
        self.EXP=EXP
        self.ExtraLoot=ExtraLoot
        self.SeesPlayersAtSpawn=SeesPlayersAtSpawn
        self.RangedAttacks=RangedAttacks
        self.InstantKillImmunity=InstantKillImmunity
        self.StunImmunity=StunImmunity
        self.Segments=Segments
        self.MinimumSkillLevel=MinimumSkillLevel
        self.MaximumSkillLevel=MaximumSkillLevel

        self.Loot=Loot
        self.SightRange=SightRange
        self.FacingDirection=FacingDirection
        self.Sprite=Sprite
        self.Color=Color
        self.MinColor=MinColor
        self.MaxColor=MaxColor
        self.Gender=Gender
        self.RelatedSkill=RelatedSkill
        self.PercentExtraHPPerSkillLevel=PercentExtraHPPerSkillLevel
        self.PercentExtraDamagePerSkillLevel=PercentExtraDamagePerSkillLevel
        self.PercentExtraDefensePerSkillLevel=PercentExtraDefensePerSkillLevel
        self.PercentExtraDodgeChancePerSkillLevel=PercentExtraDodgeChancePerSkillLevel
        self.PercentExtraEXPPerSkillLevel=PercentExtraEXPPerSkillLevel

        
    def getJson(self) -> dict:
        json={}
        json["SpawnWeight"]=self.SpawnWeight,
        json["HP"]=self.HP,
        json["CurrentHP"]=self.CurrentHP,
        json["PersistentHP"]=self.PersistentHP,
        json["Damage"]=self.Damage,
        json["Defense"]=self.Defense,
        json["DodgeChance"]=self.DodgeChance,
        json["EXP"]=self.EXP,
        json["ExtraLoot"]=self.ExtraLoot,
        json["SeesPlayersAtSpawn"]=self.SeesPlayersAtSpawn,
        json["RangedAttacks"]=self.RangedAttacks,
        json["InstantKillImmunity"]=self.InstantKillImmunity,
        json["StunImmunity"]=self.StunImmunity,
        json["Segments"]=self.Segments,
        json["MinimumSkillLevel"]=self.MinimumSkillLevel,
        json["MaximumSkillLevel"]=self.MaximumSkillLevel,

        if self.Loot is not None:
            json["Loot"]=self.Loot,
        if self.SightRange is not None:
            json["SightRange"]=self.SightRange,
        if self.FacingDirection is not None:
            json["FacingDirection"]=self.FacingDirection,
        if self.Sprite is not None:
            json["Sprite"]=self.Sprite,
        if self.Color is not None:
            json["Color"]=self.Color,
        if self.MinColor is not None:
            json["MinColor"]=self.MinColor,
        if self.MaxColor is not None:
            json["MaxColor"]=self.MaxColor,
        if self.Gender is not None:
            json["Gender"]=self.Gender,
        if self.RelatedSkill is not None:
            json["RelatedSkill"]=self.RelatedSkill,
        if self.PercentExtraHPPerSkillLevel is not None:
            json["PercentExtraHPPerSkillLevel"]=self.PercentExtraHPPerSkillLevel,
        if self.PercentExtraDamagePerSkillLevel is not None:
            json["PercentExtraDamagePerSkillLevel"]=self.PercentExtraDamagePerSkillLevel,
        if self.PercentExtraDefensePerSkillLevel is not None:
            json["PercentExtraDefensePerSkillLevel"]=self.PercentExtraDefensePerSkillLevel,
        if self.PercentExtraDodgeChancePerSkillLevel is not None:
            json["PercentExtraDodgeChancePerSkillLevel"]=self.PercentExtraDodgeChancePerSkillLevel,
        if self.PercentExtraEXPPerSkillLevel is not None:
            json["PercentExtraEXPPerSkillLevel"]=self.PercentExtraEXPPerSkillLevel
        

        return json
        

class MonsterTypes:
    def __init__(
        self,
        MonsterName:str,
        Settings:MonsterTypeSettings
    ):
        self.MonsterName=MonsterName
        self.Settings=Settings
    
    def getJson(self) -> dict:
        return {"MonsterName":self.MonsterName, "Settings":self.Settings.getJson()}
        

class MonsterAreas(Areas):
    def __init__(
        self,
        MonsterTypes:list[MonsterTypes],
        UniqueAreaID:str,
        MapName:str,
        MinimumSpawnsPerDay:str,
        MaximumSpawnsPerDay:str,
        SpawnTiming: SpawnTimingSettings,
        ExtraConditions: ExtraConditions,
        IncludeTerrainTypes:Optional[list[str]]=[],
        ExcludeTerrainTypes:Optional[list[str]]=[],
        IncludeCoordinates:Optional[list[Coordinates]]=[],
        ExcludeCoordinates:Optional[list[Coordinates]]=[],
        StrictTileChecking:Optional[str]="Maximum",
        DaysUntilSpawnsExpire:Optional[int|None]=None 
    ):
        self.MonsterTypes=MonsterTypes
        super().__init__(UniqueAreaID, MapName, MinimumSpawnsPerDay, MaximumSpawnsPerDay, SpawnTiming, ExtraConditions, IncludeTerrainTypes, ExcludeTerrainTypes, IncludeCoordinates, ExcludeCoordinates, StrictTileChecking, DaysUntilSpawnsExpire)
        

    def getJson(self) -> dict:
        json= super().getJson()
        json["MonsterTypes"]=[item.getJson() for item in self.MonsterTypes]
        return json

class GlobalSpawnSettings:
    def __init__(
        self,
        Enable:bool,
        Areas:list[Areas],
        CustomTileIndex:Optional[list[int]]=[] 
    ):
        self.Enable=Enable
        self.Areas=Areas
        self.CustomTileIndex=CustomTileIndex
        
    def getJson(self) -> dict:
        return {
            "Areas":self.Areas,
            "CustomTileIndex":self.CustomTileIndex
        }
class ForageSpawnSettings(GlobalSpawnSettings):
    def __init__(
        self,
        Enable:bool,
        Areas:list[ForageAreas],
        PercentExtraSpawnsPerForagingLevel:int=0,
        SpringItemIndex:list[Any]=[],
        SummerItemIndex:list[Any]=[],
        FallItemIndex:list[Any]=[],
        WinterItemIndex:list[Any]=[],
        CustomTileIndex:Optional[list[int]]=[] 
    ):
        super().__init__(Enable, Areas, CustomTileIndex)
        self.key="Forage_Spawn_Settings"
        self.PercentExtraSpawnsPerForagingLevel=PercentExtraSpawnsPerForagingLevel
        self.SpringItemIndex=SpringItemIndex
        self.SummerItemIndex=SummerItemIndex
        self.FallItemIndex=FallItemIndex
        self.WinterItemIndex=WinterItemIndex
    
    def getJson(self) -> dict:
        json=super().getJson()
        json["PercentExtraSpawnsPerForagingLevel"]=self.PercentExtraSpawnsPerForagingLevel,
        json["SpringItemIndex"]=self.SpringItemIndex,
        json["SummerItemIndex"]=self.SummerItemIndex,
        json["FallItemIndex"]=self.FallItemIndex,
        json["WinterItemIndex"]=self.WinterItemIndex
        return json

class LargeObjectSpawnSettings(GlobalSpawnSettings):
    def __init__(
        self,
        Enable:bool,
        Areas:list[LargueObjectAreas],
        CustomTileIndex:Optional[list[int]]=[]
    ):
        self.key="LargeObject_Spawn_Settings"
        super().__init__(Enable, Areas, CustomTileIndex)
    
    def getJson(self) -> dict:
        return super().getJson()

class OreSpawnSettings(GlobalSpawnSettings):
    def __init__(
        self,
        Enable:bool,
        Areas:list[OreAreas],
        PercentExtraSpawnsPerMiningLevel:int=0,
        MiningLevelRequired:dict[str,int]={},
        StartingSpawnChance:dict[str,int]={},
        LevelTenSpawnChance:dict[str,int]={},
        CustomTileIndex:Optional[list[int]]=[]
    ):
        self.key="Ore_Spawn_Settings"
        self.PercentExtraSpawnsPerMiningLevel=PercentExtraSpawnsPerMiningLevel
        self.MiningLevelRequired=MiningLevelRequired
        self.StartingSpawnChance=StartingSpawnChance
        self.LevelTenSpawnChance=LevelTenSpawnChance
        super().__init__(Enable, Areas, CustomTileIndex)
    
    def getJson(self) -> dict:
        json=super().getJson()
        json["PercentExtraSpawnsPerMiningLevel"]=self.PercentExtraSpawnsPerMiningLevel,
        json["MiningLevelRequired"]=self.MiningLevelRequired,
        json["StartingSpawnChance"]=self.StartingSpawnChance,
        json["LevelTenSpawnChance"]=self.LevelTenSpawnChance
        return json

class MonsterSpawnSettings(GlobalSpawnSettings):
    def __init__(
        self,
        Enable:bool,
        Areas:list[MonsterAreas],
        CustomTileIndex:Optional[list[int]]=[]
    ):
        self.key="Monster_Spawn_Settings"
        super().__init__(Enable, Areas, CustomTileIndex)
    
    def getJson(self) -> dict:
        return super().getJson()
        
class FarmTypeManager:
    def __init__(
        self,
        manifest:Manifest
    ):
        self.Manifest=manifest
        self.Manifest.ContentPackFor={
            "UniqueID": "Esca.FarmTypeManager",
            "MinimumVersion": "1.23.0"
        }
        self.fileName="content.json"

        self.contentFile={}

    def registryContentData(self, forageSpawn:ForageSpawnSettings, largeObjectSpawn:LargeObjectSpawnSettings, oreSpawn:OreSpawnSettings, monsterSpawn:MonsterSpawnSettings):
        self.contentFile[forageSpawn.key]=forageSpawn.getJson()
        self.contentFile[largeObjectSpawn.key]=largeObjectSpawn.getJson()
        self.contentFile[oreSpawn.key]=oreSpawn.getJson()
        self.contentFile[monsterSpawn.key]=monsterSpawn.getJson()