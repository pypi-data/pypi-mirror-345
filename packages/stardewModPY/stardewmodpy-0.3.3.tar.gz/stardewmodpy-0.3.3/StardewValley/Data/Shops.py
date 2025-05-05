from .model import modelsData
from typing import Optional, Any


class ShopModifiersData(modelsData):
    def __init__(
        self,
        Id: str,
        Modification: str,
        Amount: Optional[float] = 0.0,
        RandomAmount: Optional[list[float]] = None,
        Condition: Optional[str] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.Modification = Modification
        self.Amount = Amount
        self.RandomAmount = RandomAmount
        self.Condition = Condition


class ShopItemsData(modelsData):
    def __init__(
        self,
        Id: str,
        ItemId: str,
        Price: Optional[int] = -1,
        TradeItemId: Optional[str] = None,
        TradeItemAmount: Optional[int] = 1,
        ApplyProfitMargins: Optional[bool] = None,
        IgnoreShopPriceModifiers: Optional[bool] = False,
        AvailableStockModifiers: Optional[list[ShopModifiersData]] = None,
        PriceModifiers: Optional[list[ShopModifiersData]] = None,
        AvailableStockModifierMode: Optional[str] = "Stack",
        PriceModifierMode: Optional[str] = "Stack",
        AvoidRepeat: Optional[bool] = False,
        UseObjectDataPrice: Optional[bool] = False,
        AvailableStock: Optional[int] = -1,
        AvailableStockLimit: Optional[str] = "Global",
        PerItemCondition: Optional[str] = None,
        ActionsOnPurchase: Optional[list[str]] = None,
        RandomItemId: Optional[list[str]] = [],
        Condition: Optional[str] = None,
        IsRecipe: Optional[bool] = False,
        Quality: Optional[int] = -1,
        MinStack: Optional[int] = -1,
        MaxStack: Optional[int] = -1,
        ObjectInternalName: Optional[str] = None,
        ObjectDisplayName: Optional[str] = None,
        ToolUpgradeLevel: Optional[int] = -1,
        StackModifiers: Optional[Any] = None,
        QualityModifiers: Optional[Any] = None,
        QualityModifierMode: Optional[str] = "Stack",
        StackModifierMode: Optional[str] = "Stack",
        ModData: Optional[dict[str, str]] = None,
        CustomFields: Optional[Any] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.ItemId = ItemId
        self.Price = Price
        self.TradeItemId = TradeItemId
        self.TradeItemAmount = TradeItemAmount
        self.ApplyProfitMargins = ApplyProfitMargins
        self.IgnoreShopPriceModifiers = IgnoreShopPriceModifiers
        self.AvailableStockModifiers = AvailableStockModifiers
        self.PriceModifiers = PriceModifiers
        self.AvailableStockModifierMode = AvailableStockModifierMode
        self.PriceModifierMode = PriceModifierMode
        self.AvoidRepeat = AvoidRepeat
        self.UseObjectDataPrice = UseObjectDataPrice
        self.AvailableStock = AvailableStock
        self.AvailableStockLimit = AvailableStockLimit
        self.PerItemCondition = PerItemCondition
        self.ActionsOnPurchase = ActionsOnPurchase
        self.RandomItemId = RandomItemId
        self.Condition = Condition
        self.IsRecipe = IsRecipe
        self.Quality = Quality
        self.MinStack = MinStack
        self.MaxStack = MaxStack
        self.ObjectInternalName = ObjectInternalName
        self.ObjectDisplayName = ObjectDisplayName
        self.ToolUpgradeLevel = ToolUpgradeLevel
        self.StackModifiers = StackModifiers
        self.QualityModifiers = QualityModifiers
        self.QualityModifierMode = QualityModifierMode
        self.StackModifierMode = StackModifierMode
        self.ModData = ModData
        self.CustomFields = CustomFields


class ShopOwnersDialoguesData(modelsData):
    def __init__(
        self,
        Id: str,
        Dialogue: str,
        RandomDialogue: Optional[list[str]] = None,
        Condition: Optional[str] = None,
    ):
        super().__init__(None)
        self.Id = Id
        self.Dialogue = Dialogue
        self.RandomDialogue = RandomDialogue
        self.Condition = Condition



class ShopItemsOwnersData(modelsData):
    def __init__(
        self,
        Name: str,
        Id: Optional[str],
        Condition: Optional[str] = None,
        Portrait: Optional[str] = None,
        Dialogues: Optional[list[ShopOwnersDialoguesData]] = [],
        RandomizeDialogueOnOpen: Optional[bool] = True,
        ClosedMessage: Optional[str] = None
    ):
        super().__init__(None)
        self.Name = Name
        self.Id = Id
        self.Condition = Condition
        self.Portrait = Portrait
        self.Dialogues = Dialogues
        self.RandomizeDialogueOnOpen = RandomizeDialogueOnOpen
        self.ClosedMessage = ClosedMessage





class CursorsData(modelsData):
    def __init__(
        self,
        X: int,
        Y: int,
        Width: int,
        Height: int
    ):
        super().__init__(None)
        self.X = X
        self.Y = Y
        self.Width = Width
        self.Height = Height





class VisualThemeData(modelsData):
    def __init__(
        self,
        WindowBorderTexture: str,
        WindowBorderSourceRect: CursorsData,
        ItemRowBackgroundTexture: str,
        ItemRowBackgroundSourceRect: CursorsData,
        ItemIconBackgroundTexture: str,
        ItemIconBackgroundSourceRect: CursorsData,
        ItemRowBackgroundHoverColor: str,
        ItemRowTextColor: str,
        Condition: Optional[str] = None,
        PortraitBackgroundTexture: Optional[str] = None,
        PortraitBackgroundSourceRect: Optional[CursorsData] = None,
        DialogueBackgroundTexture: Optional[str] = None,
        DialogueBackgroundSourceRect: Optional[CursorsData] = None,
        DialogueColor: Optional[str] = None,
        DialogueShadowColor: Optional[str] = None,
        ScrollUpTexture: Optional[str] = None,
        ScrollUpSourceRect: Optional[CursorsData] = None,
        ScrollDownTexture: Optional[str] = None,
        ScrollDownSourceRect: Optional[CursorsData] = None,
        ScrollBarFrontTexture: Optional[str] = None,
        ScrollBarFrontSourceRect: Optional[CursorsData] = None,
        ScrollBarBackTexture: Optional[str] = None,
        ScrollBarBackSourceRect: Optional[CursorsData] = None
    ):
        super().__init__(None)
        self.WindowBorderTexture = WindowBorderTexture
        self.WindowBorderSourceRect = WindowBorderSourceRect
        self.ItemRowBackgroundTexture = ItemRowBackgroundTexture
        self.ItemRowBackgroundSourceRect = ItemRowBackgroundSourceRect
        self.ItemIconBackgroundTexture = ItemIconBackgroundTexture
        self.ItemIconBackgroundSourceRect = ItemIconBackgroundSourceRect
        self.ItemRowBackgroundHoverColor = ItemRowBackgroundHoverColor
        self.ItemRowTextColor = ItemRowTextColor
        self.Condition = Condition
        self.PortraitBackgroundTexture = PortraitBackgroundTexture
        self.PortraitBackgroundSourceRect = PortraitBackgroundSourceRect
        self.DialogueBackgroundTexture = DialogueBackgroundTexture
        self.DialogueBackgroundSourceRect = DialogueBackgroundSourceRect
        self.DialogueColor = DialogueColor
        self.DialogueShadowColor = DialogueShadowColor
        self.ScrollUpTexture = ScrollUpTexture
        self.ScrollUpSourceRect = ScrollUpSourceRect
        self.ScrollDownTexture = ScrollDownTexture
        self.ScrollDownSourceRect = ScrollDownSourceRect
        self.ScrollBarFrontTexture = ScrollBarFrontTexture
        self.ScrollBarFrontSourceRect = ScrollBarFrontSourceRect
        self.ScrollBarBackTexture = ScrollBarBackTexture
        self.ScrollBarBackSourceRect = ScrollBarBackSourceRect



class ShopsData(modelsData):
    def __init__(
        self,
        key: str,
        Items: list[ShopItemsData],
        Owners: list[ShopItemsOwnersData],
        SalableItemTags: Optional[list[str]] = None,
        Currency: Optional[int] = 0,
        ApplyProfitMargins: Optional[bool] = None,
        StackSizeVisibility: Optional[str] = None,
        OpenSound: Optional[str] = "dwop",
        PurchaseSound: Optional[str] = "purchaseClick",
        purchaseRepeatSound: Optional[str] = "purchaseRepeat",
        PriceModifiers: Optional[ShopModifiersData] = None,
        PriceModifierMode: Optional[str] = "Stack",
        VisualTheme: Optional[list[VisualThemeData]] = None,
        CustomFields: Optional[Any] = None
    ):
        super().__init__(key)
        self.Items = Items
        self.Owners = Owners
        self.SalableItemTags = SalableItemTags
        self.Currency = Currency
        self.ApplyProfitMargins = ApplyProfitMargins
        self.StackSizeVisibility = StackSizeVisibility
        self.OpenSound = OpenSound
        self.PurchaseSound = PurchaseSound
        self.purchaseRepeatSound = purchaseRepeatSound
        self.PriceModifiers = PriceModifiers
        self.PriceModifierMode = PriceModifierMode
        self.VisualTheme = VisualTheme
        self.CustomFields = CustomFields
